"""Closed operational bridge for the frozen collar comparison."""

from __future__ import annotations

import re
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from typing import Callable
from uuid import uuid4

from .comparator import MemberPlan, MemberPreparation, orchestrate
from .comparison_adapter import (
    ComparisonMemberExecutionRequest,
    ComparisonMemberExecutionResponse,
    execute_comparison_member,
)
from .comparison_models import InvocationRecord, PlannedParameters, utc_now
from .comparison_readiness import ComparisonReadiness
from .comparison_preflight import preflight_comparison_execution
from .comparison_spec import ComparisonSpec
from .config import SimulationConfig
from .equipment_transform import materialize_neck_profile
from .runner import (
    RunReservation,
    _argv_sha256,
    _file_sha256,
    _portable_argv,
    reserve_run,
)


class ComparisonExecutionError(RuntimeError):
    """The controlled execution bridge rejected or could not persist a run."""


ExecutionIdSource = Callable[[], str]
_EXECUTION_ID_PATTERN = re.compile(r"cmp-[0-9a-f]{32}")


def _execution_id(source: ExecutionIdSource | None) -> str:
    selected = source if source is not None else lambda: f"cmp-{uuid4().hex}"
    value = selected()
    if not isinstance(value, str) or _EXECUTION_ID_PATTERN.fullmatch(value) is None:
        raise ComparisonExecutionError("comparison_execution_id_invalid")
    return value


def _member_config(
    config: SimulationConfig,
    spec: ComparisonSpec,
    plan: MemberPlan,
) -> SimulationConfig:
    return replace(
        config,
        runs_dir=(config.runs_dir.resolve()),
        threads=spec.protocol.threads,
        iterations=spec.protocol.iterations_per_run,
        target_error=None,
        seed=plan.seed,
        generate_html=False,
        variant=None,
    )


def _prepare_member(
    plan: MemberPlan,
    reservation: RunReservation,
    *,
    spec: ComparisonSpec,
    config: SimulationConfig,
    root: Path,
) -> MemberPreparation:
    base = spec.base_profile.read_bytes()
    if sha256(base).hexdigest() != spec.base_profile_sha256:
        raise ComparisonExecutionError("comparison_base_profile_changed")
    arm = spec.arm_a if plan.arm == "a" else spec.arm_b
    effective = reservation.run_directory / "effective_profile.simc"
    transformed = materialize_neck_profile(base, arm, effective)
    if (
        transformed.base_sha256 != spec.base_profile_sha256
        or transformed.only_neck_changed is not True
    ):
        raise ComparisonExecutionError("comparison_profile_transform_invalid")
    member_config = _member_config(config, spec, plan)
    json_file = reservation.run_directory / "simc.json"
    command = [
        str(member_config.simc_exe.resolve()),
        str(effective.resolve()),
        f"threads={member_config.threads}",
        f"json={json_file.resolve()},version=2,pretty_print=1",
        f"iterations={member_config.iterations}",
        f"max_time={member_config.max_time}",
        f"vary_combat_length={member_config.vary_combat_length:g}",
        f"fight_style={member_config.fight_style}",
        f"desired_targets={member_config.desired_targets}",
        f"seed={member_config.seed}",
    ]
    portable = _portable_argv(command, root=root)
    invocation = InvocationRecord(
        "built",
        portable,
        _argv_sha256(portable),
        _argv_sha256(command),
        _file_sha256(member_config.simc_exe),
        member_config.executable_source,
        True,
        False,
        utc_now(),
    )
    return MemberPreparation(transformed.effective_sha256, invocation)


def _run_member(
    plan: MemberPlan,
    reservation: RunReservation,
    *,
    spec: ComparisonSpec,
    config: SimulationConfig,
    readiness: ComparisonReadiness,
    root: Path,
) -> ComparisonMemberExecutionResponse:
    effective = reservation.run_directory / "effective_profile.simc"
    digest = sha256(effective.read_bytes()).hexdigest()
    member_config = _member_config(config, spec, plan)
    request = ComparisonMemberExecutionRequest(
        spec.comparison_id,
        plan.comparison_execution_id,
        spec.source_sha256,
        plan.block_index,
        plan.attempt,
        plan.arm,
        plan.order_position,
        plan.candidate_item_id,
        reservation,
        spec.base_profile,
        effective,
        spec.scenario_sha256,
        spec.evidence_sha256,
        readiness.preflight.software.dpslab.version,
        PlannedParameters(
            plan.seed,
            spec.protocol.iterations_per_run,
            spec.protocol.threads,
            None,
            spec.protocol.timeout_seconds,
        ),
        readiness.preflight.software.simulationcraft,
        spec.base_profile_sha256,
        digest,
    )
    return execute_comparison_member(request, member_config, root=root)


def execute_frozen_comparison(
    spec: ComparisonSpec,
    config: SimulationConfig,
    readiness: ComparisonReadiness,
    *,
    confirmation: str,
    root: Path,
    execution_id_source: ExecutionIdSource | None = None,
):
    """Cross the write boundary once and delegate the entire protocol."""
    root = root.resolve()
    if not isinstance(readiness, ComparisonReadiness):
        raise ComparisonExecutionError("comparison_execution_precondition_failed")
    try:
        revalidated = preflight_comparison_execution(
            spec,
            config,
            readiness.preflight.software.simulationcraft,
            readiness.preflight.software,
            root=root,
        )
    except Exception:
        raise ComparisonExecutionError(
            "comparison_execution_precondition_failed"
        ) from None
    if (
        confirmation != spec.comparison_id
        or readiness.ready is not True
        or readiness.preflight.comparison_id != spec.comparison_id
        or readiness.preflight.comparison_spec_sha256 != spec.source_sha256
        or readiness.preflight.software.simulationcraft.version
        != spec.simc_version
        or readiness.preflight.software.simulationcraft.revision
        != spec.simc_revision
        or config.executable_source != "explicit_cli"
        or revalidated != readiness.preflight
    ):
        raise ComparisonExecutionError("comparison_execution_precondition_failed")
    execution_id = _execution_id(execution_id_source)
    comparison_root = root / "results" / "comparisons"
    output_directory = comparison_root / execution_id
    if output_directory.parent != comparison_root or output_directory.exists():
        raise ComparisonExecutionError("comparison_execution_output_exists")
    try:
        output_directory.mkdir(parents=True, exist_ok=False)
    except OSError:
        raise ComparisonExecutionError(
            "comparison_execution_output_unavailable"
        ) from None
    output = output_directory / "comparison_result.json"
    return orchestrate(
        spec,
        execution_id,
        output,
        lambda plan, reservation: _run_member(
            plan,
            reservation,
            spec=spec,
            config=config,
            readiness=readiness,
            root=root,
        ),
        reserve_member=lambda plan: reserve_run(
            config.runs_dir,
            comparison_execution_id=plan.comparison_execution_id,
            member_id=plan.member_id,
        ),
        prepare_member=lambda plan, reservation: _prepare_member(
            plan,
            reservation,
            spec=spec,
            config=config,
            root=root,
        ),
        software=readiness.preflight.software,
    )
