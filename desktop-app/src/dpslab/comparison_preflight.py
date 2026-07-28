"""Fail-closed, read-only preflight for one frozen comparison execution."""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from hashlib import sha256
from pathlib import Path
from pathlib import PurePosixPath

from .comparison_environment import source_tree_inventory, source_tree_sha256
from .comparison_models import ComparisonSoftware, SimulationCraftIdentity
from .comparison_spec import (
    ComparisonSpec,
    ComparisonSpecError,
    load_comparison_spec,
)
from .config import SimulationConfig
from .scenario import ScenarioError, load_scenario


class ComparisonExecutionPreflightError(ValueError):
    """The frozen comparison is not ready to cross the process boundary."""


@dataclass(frozen=True, slots=True)
class ComparisonExecutionPreflight:
    comparison_id: str
    comparison_spec_sha256: str
    base_profile_sha256: str
    scenario_sha256: str
    evidence_manifest_sha256: str
    runs_dir: str
    software: ComparisonSoftware
    ready: bool = True


_ALLOWED_EXECUTABLE_SOURCES = frozenset(
    {"explicit_cli", "environment", "local_config"}
)


def _version_parts(value: str, field_name: str) -> tuple[int, ...]:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", value)
    if match is None:
        raise ComparisonExecutionPreflightError(f"{field_name}_invalid")
    return tuple(int(part) for part in match.groups())


def _portable_source_inventory(values: tuple[str, ...]) -> bool:
    if not values or tuple(sorted(set(values))) != values:
        return False
    for value in values:
        path = PurePosixPath(value)
        if (
            not value
            or "\\" in value
            or ":" in value
            or path.is_absolute()
            or any(part in {"", ".", ".."} for part in path.parts)
            or path.as_posix() != value
        ):
            return False
    return True


def _require_runtime(software: ComparisonSoftware, root: Path) -> None:
    if software.python.implementation != "CPython":
        raise ComparisonExecutionPreflightError("python_implementation_mismatch")
    if _version_parts(software.python.version, "python_version") < (3, 11, 0):
        raise ComparisonExecutionPreflightError("python_version_mismatch")
    if software.scipy.requirement != ">=1.11.0,<2.0.0":
        raise ComparisonExecutionPreflightError("scipy_requirement_mismatch")
    scipy = _version_parts(software.scipy.version, "scipy_version")
    if scipy < (1, 11, 0) or scipy >= (2, 0, 0):
        raise ComparisonExecutionPreflightError("scipy_version_mismatch")
    source = software.dpslab
    if source.version != "0.1.0":
        raise ComparisonExecutionPreflightError("dpslab_version_mismatch")
    if source.source_identity_kind == "git_commit":
        if (
            source.commit is None
            or re.fullmatch(r"[0-9a-f]{40}", source.commit) is None
            or source.dirty_state is not False
            or source.source_tree_sha256 is not None
            or source.source_inventory_method is not None
            or source.source_inventory
        ):
            raise ComparisonExecutionPreflightError("dpslab_git_identity_not_clean")
    elif source.source_identity_kind == "dpslab_source_tree_sha256_v1":
        source_root = root / "desktop-app" / "src" / "dpslab"
        actual_inventory = source_tree_inventory(source_root)
        if (
            source.commit is not None
            or source.dirty_state is not None
            or source.source_tree_sha256 is None
            or re.fullmatch(r"[0-9a-f]{64}", source.source_tree_sha256) is None
            or source.source_inventory_method != "sorted_portable_paths_v1"
            or not _portable_source_inventory(source.source_inventory)
            or source.source_inventory != actual_inventory
            or source.source_tree_sha256 != source_tree_sha256(source_root)
        ):
            raise ComparisonExecutionPreflightError(
                "dpslab_source_identity_invalid"
            )
    else:
        raise ComparisonExecutionPreflightError("dpslab_source_identity_invalid")


def _require_file_hash(path: Path, expected: str, label: str) -> None:
    if not path.is_file() or sha256(path.read_bytes()).hexdigest() != expected:
        raise ComparisonExecutionPreflightError(f"{label}_hash_mismatch")


def preflight_comparison_execution(
    spec: ComparisonSpec,
    config: SimulationConfig,
    observed_simc: SimulationCraftIdentity,
    software: ComparisonSoftware,
    *,
    root: Path,
) -> ComparisonExecutionPreflight:
    """Validate frozen execution inputs without starting a process or writing state."""
    root = root.resolve()
    if (
        spec.source_file.parent != root / "comparisons"
        or spec.source_file.name != f"{spec.comparison_id}.toml"
    ):
        raise ComparisonExecutionPreflightError("comparison_spec_path_mismatch")
    _require_file_hash(
        spec.source_file, spec.source_sha256, "comparison_spec"
    )
    _require_file_hash(
        spec.base_profile, spec.base_profile_sha256, "base_profile"
    )
    _require_file_hash(spec.scenario, spec.scenario_sha256, "scenario")
    _require_file_hash(
        spec.evidence_manifest, spec.evidence_sha256, "evidence_manifest"
    )
    try:
        authoritative_spec = load_comparison_spec(spec.source_file, root=root)
    except (ComparisonSpecError, OSError) as exc:
        raise ComparisonExecutionPreflightError(
            "comparison_spec_authoritative_reload_failed"
        ) from exc
    if spec.status != "frozen" or spec != authoritative_spec:
        raise ComparisonExecutionPreflightError(
            "comparison_spec_semantic_mismatch"
        )
    if config.variant is not None:
        raise ComparisonExecutionPreflightError("variant_not_allowed")
    scenario = config.scenario
    if (
        scenario is None
        or scenario.source_file != spec.scenario
        or scenario.source_sha256 != spec.scenario_sha256
    ):
        raise ComparisonExecutionPreflightError("scenario_identity_mismatch")
    try:
        authoritative_scenario = load_scenario(spec.scenario)
    except (ScenarioError, OSError) as exc:
        raise ComparisonExecutionPreflightError(
            "scenario_authoritative_reload_failed"
        ) from exc
    if scenario != authoritative_scenario:
        raise ComparisonExecutionPreflightError("scenario_semantic_mismatch")
    expected_config = (
        spec.protocol.iterations_per_run,
        spec.protocol.threads,
        spec.protocol.timeout_seconds,
        None,
        None,
    )
    actual_config = (
        config.iterations,
        config.threads,
        config.timeout_seconds,
        config.target_error,
        config.seed,
    )
    if actual_config != expected_config:
        raise ComparisonExecutionPreflightError("execution_parameters_mismatch")
    scenario_values = scenario.scenario
    if (
        config.max_time,
        config.vary_combat_length,
        config.fight_style,
        config.desired_targets,
    ) != (
        scenario_values.max_time,
        scenario_values.vary_combat_length,
        scenario_values.fight_style,
        scenario_values.desired_targets,
    ):
        raise ComparisonExecutionPreflightError("scenario_parameters_mismatch")
    runs_dir = (root / "results" / "runs").resolve()
    if config.runs_dir.resolve() != runs_dir:
        raise ComparisonExecutionPreflightError("runs_dir_mismatch")
    if config.executable_source not in _ALLOWED_EXECUTABLE_SOURCES:
        raise ComparisonExecutionPreflightError("executable_source_invalid")
    if not config.simc_exe.is_file():
        raise ComparisonExecutionPreflightError("simulationcraft_executable_missing")
    executable_sha256 = sha256(config.simc_exe.read_bytes()).hexdigest()
    expected_simc = SimulationCraftIdentity(
        spec.simc_version, spec.simc_revision, executable_sha256
    )
    if observed_simc != expected_simc:
        raise ComparisonExecutionPreflightError("simulationcraft_identity_mismatch")

    _require_runtime(software, root)
    software = replace(software, simulationcraft=observed_simc)
    return ComparisonExecutionPreflight(
        comparison_id=spec.comparison_id,
        comparison_spec_sha256=spec.source_sha256,
        base_profile_sha256=spec.base_profile_sha256,
        scenario_sha256=spec.scenario_sha256,
        evidence_manifest_sha256=spec.evidence_sha256,
        runs_dir="results/runs",
        software=software,
    )
