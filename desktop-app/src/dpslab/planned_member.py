"""Pure planning and candidate construction for a new comparison member."""

from __future__ import annotations

import re
import secrets
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from hashlib import sha256
from typing import Callable

from .comparison_models import (
    ComparisonMember,
    ComparisonResult,
    ComparisonResultError,
    InvocationRecord,
    PlannedParameters,
    RunArtifactSet,
    RunReservationRecord,
    SimulationCraftIdentity,
    StateEvent,
    validate_result,
)
from .comparison_spec import ComparisonArm, ComparisonSpec
from .run_identity import RunIdentityPlan, validate_run_identity_plan


RUNS_ROOT_PORTABLE = "results/runs"
TokenSource = Callable[[], str]
_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_-]{32,}")


@dataclass(frozen=True, slots=True)
class PlannedMemberCreationPlan:
    """Ephemeral input for jointly creating a planned member and reservation."""

    run_identity: RunIdentityPlan
    comparison_spec: ComparisonSpec = field(repr=False)
    reservation_token: str = field(repr=False)
    token_sha256: str
    comparison_id: str
    comparison_spec_sha256: str
    planned_order: str
    order_position: int
    seed: int
    candidate_item_id: int
    base_profile_sha256: str
    scenario_sha256: str
    evidence_manifest_sha256: str
    planned_parameters: PlannedParameters
    expected_simc: SimulationCraftIdentity

    @property
    def run_id(self) -> str:
        return self.run_identity.run_id


def _is_sha256(value: str | None) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _timestamp(value: str, field_name: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ComparisonResultError(f"{field_name} invalido")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ComparisonResultError(f"{field_name} invalido") from exc
    if parsed.tzinfo is None:
        raise ComparisonResultError(f"{field_name} debe incluir zona horaria")
    return parsed


def _validate_token(token: str) -> None:
    if not isinstance(token, str) or _TOKEN_PATTERN.fullmatch(token) is None:
        raise ComparisonResultError(
            "El token de reserva debe ser URL-safe y contener al menos 32 caracteres"
        )


def _arm_data(
    spec: ComparisonSpec,
    plan: RunIdentityPlan,
) -> tuple[ComparisonArm, str, int]:
    if spec.status != "frozen":
        raise ComparisonResultError("comparison_spec no esta congelado")
    if not 1 <= plan.block_index <= len(spec.protocol.seeds):
        raise ComparisonResultError("block_index no existe en comparison_spec")
    planned_order = spec.protocol.orders[plan.block_index - 1]
    upper_arm = plan.arm.upper()
    if upper_arm not in planned_order:
        raise ComparisonResultError("arm no pertenece al orden planificado")
    order_position = planned_order.index(upper_arm) + 1
    arm = spec.arm_a if plan.arm == "a" else spec.arm_b
    if arm.key != plan.arm:
        raise ComparisonResultError("Identidad de brazo incoherente")
    return arm, planned_order, order_position


def validate_planned_member_creation_plan(
    creation_plan: PlannedMemberCreationPlan,
) -> None:
    validate_run_identity_plan(
        creation_plan.run_identity,
        runs_root_portable=RUNS_ROOT_PORTABLE,
    )
    _validate_token(creation_plan.reservation_token)
    expected_digest = sha256(creation_plan.reservation_token.encode("utf-8")).hexdigest()
    if creation_plan.token_sha256 != expected_digest or not _is_sha256(
        creation_plan.token_sha256
    ):
        raise ComparisonResultError("token_sha256 no corresponde al token efimero")
    if not creation_plan.comparison_id.strip():
        raise ComparisonResultError("comparison_id vacio")
    if not _is_sha256(creation_plan.comparison_spec_sha256):
        raise ComparisonResultError("comparison_spec_sha256 invalido")
    if creation_plan.planned_order not in {"AB", "BA"}:
        raise ComparisonResultError("planned_order invalido")
    expected_position = creation_plan.planned_order.index(
        creation_plan.run_identity.arm.upper()
    ) + 1
    if creation_plan.order_position != expected_position:
        raise ComparisonResultError("order_position incoherente")
    if (
        isinstance(creation_plan.seed, bool)
        or not isinstance(creation_plan.seed, int)
        or creation_plan.seed <= 0
    ):
        raise ComparisonResultError("seed invalida")
    if (
        isinstance(creation_plan.candidate_item_id, bool)
        or not isinstance(creation_plan.candidate_item_id, int)
        or creation_plan.candidate_item_id <= 0
    ):
        raise ComparisonResultError("candidate_item_id invalido")
    for name in (
        "base_profile_sha256",
        "scenario_sha256",
        "evidence_manifest_sha256",
    ):
        if not _is_sha256(getattr(creation_plan, name)):
            raise ComparisonResultError(f"{name} invalido")
    parameters = creation_plan.planned_parameters
    if (
        parameters.seed != creation_plan.seed
        or isinstance(parameters.iterations, bool)
        or parameters.iterations <= 0
        or isinstance(parameters.threads, bool)
        or parameters.threads <= 0
        or parameters.target_error is not None
        or parameters.timeout_seconds <= 0
    ):
        raise ComparisonResultError("PlannedParameters incoherentes")
    expected_simc = creation_plan.expected_simc
    if not expected_simc.version or not expected_simc.revision:
        raise ComparisonResultError("SimulationCraftIdentity esperada incompleta")
    if (
        expected_simc.executable_sha256 is not None
        and not _is_sha256(expected_simc.executable_sha256)
    ):
        raise ComparisonResultError("SimulationCraft executable_sha256 invalido")
    spec = creation_plan.comparison_spec
    arm, planned_order, order_position = _arm_data(spec, creation_plan.run_identity)
    expected_parameters = PlannedParameters(
        spec.protocol.seeds[creation_plan.run_identity.block_index - 1],
        spec.protocol.iterations_per_run,
        spec.protocol.threads,
        None,
        spec.protocol.timeout_seconds,
    )
    if (
        creation_plan.comparison_id != spec.comparison_id
        or creation_plan.comparison_spec_sha256 != spec.source_sha256
        or creation_plan.planned_order != planned_order
        or creation_plan.order_position != order_position
        or creation_plan.seed
        != spec.protocol.seeds[creation_plan.run_identity.block_index - 1]
        or creation_plan.candidate_item_id != arm.item_id
        or creation_plan.base_profile_sha256 != spec.base_profile_sha256
        or creation_plan.scenario_sha256 != spec.scenario_sha256
        or creation_plan.evidence_manifest_sha256 != spec.evidence_sha256
        or creation_plan.planned_parameters != expected_parameters
        or expected_simc.version != spec.simc_version
        or expected_simc.revision != spec.simc_revision
    ):
        raise ComparisonResultError("creation_plan no coincide con comparison_spec")


def prepare_planned_member_creation(
    run_identity_plan: RunIdentityPlan,
    spec: ComparisonSpec,
    expected_simc: SimulationCraftIdentity,
    *,
    token_source: TokenSource | None = None,
) -> PlannedMemberCreationPlan:
    """Prepare one frozen creation plan without touching durable or physical state."""
    validate_run_identity_plan(
        run_identity_plan,
        runs_root_portable=RUNS_ROOT_PORTABLE,
    )
    arm, planned_order, order_position = _arm_data(spec, run_identity_plan)
    if not callable(token_source) and token_source is not None:
        raise ComparisonResultError("token_source debe ser invocable")
    source = token_source or (lambda: secrets.token_urlsafe(32))
    reservation_token = source()
    _validate_token(reservation_token)
    creation_plan = PlannedMemberCreationPlan(
        run_identity=run_identity_plan,
        comparison_spec=spec,
        reservation_token=reservation_token,
        token_sha256=sha256(reservation_token.encode("utf-8")).hexdigest(),
        comparison_id=spec.comparison_id,
        comparison_spec_sha256=spec.source_sha256,
        planned_order=planned_order,
        order_position=order_position,
        seed=spec.protocol.seeds[run_identity_plan.block_index - 1],
        candidate_item_id=arm.item_id,
        base_profile_sha256=spec.base_profile_sha256,
        scenario_sha256=spec.scenario_sha256,
        evidence_manifest_sha256=spec.evidence_sha256,
        planned_parameters=PlannedParameters(
            spec.protocol.seeds[run_identity_plan.block_index - 1],
            spec.protocol.iterations_per_run,
            spec.protocol.threads,
            None,
            spec.protocol.timeout_seconds,
        ),
        expected_simc=expected_simc,
    )
    validate_planned_member_creation_plan(creation_plan)
    return creation_plan


def _all_members(result: ComparisonResult) -> tuple[ComparisonMember, ...]:
    return tuple(
        member
        for block in result.blocks
        for attempt in block.attempts
        for member in attempt.members
    )


def _target_location(
    result: ComparisonResult,
    creation_plan: PlannedMemberCreationPlan,
) -> tuple[int, int]:
    identity = creation_plan.run_identity
    blocks = [
        (index, block)
        for index, block in enumerate(result.blocks)
        if block.block_index == identity.block_index
    ]
    if len(blocks) != 1:
        raise ComparisonResultError("ComparisonBlock objetivo ausente o duplicado")
    block_index, block = blocks[0]
    if block.status != "running":
        raise ComparisonResultError("ComparisonBlock objetivo no esta running")
    if (
        block.comparison_execution_id != result.comparison_execution_id
        or block.comparison_execution_id != identity.comparison_execution_id
        or block.seed != creation_plan.seed
        or block.planned_order != creation_plan.planned_order
    ):
        raise ComparisonResultError("ComparisonBlock objetivo incoherente")
    attempts = [
        (index, attempt)
        for index, attempt in enumerate(block.attempts)
        if attempt.attempt == identity.attempt
    ]
    if len(attempts) != 1:
        raise ComparisonResultError("PairAttempt objetivo ausente o duplicado")
    attempt_index, attempt = attempts[0]
    expected_attempt_id = (
        f"{identity.comparison_execution_id}:block-{identity.block_index}:"
        f"attempt-{identity.attempt}"
    )
    if (
        attempt.status != "running"
        or attempt.comparison_execution_id != identity.comparison_execution_id
        or attempt.attempt_id != expected_attempt_id
    ):
        raise ComparisonResultError("PairAttempt objetivo incoherente")
    if block.planned_order not in {"AB", "BA"}:
        raise ComparisonResultError("planned_order objetivo invalido")
    if len(attempt.members) > len(block.planned_order):
        raise ComparisonResultError(
            "PairAttempt contiene mas miembros que brazos planificados"
        )
    for position, member in enumerate(attempt.members, 1):
        if position < 1 or position > len(block.planned_order):
            raise ComparisonResultError(
                "Posicion fisica fuera del planned_order"
            )
        expected_arm = block.planned_order[position - 1].lower()
        if (
            member.comparison_execution_id != identity.comparison_execution_id
            or member.block_index != identity.block_index
            or member.attempt != identity.attempt
            or member.order_position != position
            or member.arm != expected_arm
        ):
            raise ComparisonResultError("Miembro previo incompatible con planned_order")
    matching_member = tuple(
        member for member in attempt.members if member.member_id == identity.member_id
    )
    if matching_member:
        if (
            len(matching_member) != 1
            or matching_member[0].arm != identity.arm
            or matching_member[0].order_position != creation_plan.order_position
        ):
            raise ComparisonResultError("member_id existente en ubicacion incoherente")
        return block_index, attempt_index
    if len(attempt.members) >= 2:
        raise ComparisonResultError("PairAttempt ya contiene una pareja completa")
    if creation_plan.order_position != len(attempt.members) + 1:
        raise ComparisonResultError("El brazo no ocupa la siguiente posicion planificada")
    if any(
        member.arm == identity.arm
        or member.order_position == creation_plan.order_position
        for member in attempt.members
    ):
        raise ComparisonResultError("Brazo u order_position duplicado")
    return block_index, attempt_index


def _initial_member(
    creation_plan: PlannedMemberCreationPlan,
    occurred_at: str,
) -> ComparisonMember:
    identity = creation_plan.run_identity
    reservation = RunReservationRecord(
        planned_run_id=identity.run_id,
        owner_execution_id=identity.comparison_execution_id,
        owner_member_id=identity.member_id,
        token_sha256=creation_plan.token_sha256,
        status="reserved",
        created_at=occurred_at,
    )
    return ComparisonMember(
        member_id=identity.member_id,
        comparison_id=creation_plan.comparison_id,
        comparison_execution_id=identity.comparison_execution_id,
        comparison_spec_sha256=creation_plan.comparison_spec_sha256,
        block_index=identity.block_index,
        attempt=identity.attempt,
        arm=identity.arm,
        order_position=creation_plan.order_position,
        seed=creation_plan.seed,
        candidate_item_id=creation_plan.candidate_item_id,
        reservation=reservation,
        base_profile_sha256=creation_plan.base_profile_sha256,
        effective_profile_sha256=None,
        scenario_sha256=creation_plan.scenario_sha256,
        evidence_manifest_sha256=creation_plan.evidence_manifest_sha256,
        planned_parameters=creation_plan.planned_parameters,
        effective_parameters=None,
        invocation=InvocationRecord(status="not_built"),
        expected_simc=creation_plan.expected_simc,
        observed_simc=None,
        artifacts=RunArtifactSet(),
        dps=None,
        integrity=None,
        errors=[],
        warnings=[],
        status="planned",
        planned_at=occurred_at,
        run_id=None,
        started_at=None,
        finished_at=None,
        duration_seconds=None,
    )


def _has_initial_shape(
    result: ComparisonResult,
    member: ComparisonMember,
    creation_plan: PlannedMemberCreationPlan,
) -> bool:
    identity = creation_plan.run_identity
    try:
        _timestamp(member.planned_at, "member.planned_at")
    except ComparisonResultError:
        return False
    matching_events = [
        event
        for event in result.events
        if (
            event.entity_type == "comparison_member"
            and event.entity_id == identity.member_id
            and event.previous_status is None
            and event.new_status == "planned"
        )
    ]
    return (
        member.member_id == identity.member_id
        and member.comparison_id == creation_plan.comparison_id
        and member.comparison_execution_id == identity.comparison_execution_id
        and member.comparison_spec_sha256
        == creation_plan.comparison_spec_sha256
        and member.block_index == identity.block_index
        and member.attempt == identity.attempt
        and member.arm == identity.arm
        and member.order_position == creation_plan.order_position
        and member.seed == creation_plan.seed
        and member.candidate_item_id == creation_plan.candidate_item_id
        and member.reservation.planned_run_id == identity.run_id
        and member.reservation.owner_execution_id
        == identity.comparison_execution_id
        and member.reservation.owner_member_id == identity.member_id
        and member.reservation.token_sha256 == creation_plan.token_sha256
        and member.reservation.status == "reserved"
        and member.reservation.created_at == member.planned_at
        and member.base_profile_sha256 == creation_plan.base_profile_sha256
        and member.effective_profile_sha256 is None
        and member.scenario_sha256 == creation_plan.scenario_sha256
        and member.evidence_manifest_sha256
        == creation_plan.evidence_manifest_sha256
        and member.planned_parameters == creation_plan.planned_parameters
        and member.effective_parameters is None
        and member.invocation == InvocationRecord(status="not_built")
        and member.expected_simc == creation_plan.expected_simc
        and member.observed_simc is None
        and member.artifacts.references == ()
        and member.dps is None
        and member.integrity is None
        and member.errors == []
        and member.warnings == []
        and member.status == "planned"
        and member.run_id is None
        and member.started_at is None
        and member.finished_at is None
        and member.duration_seconds is None
        and len(matching_events) == 1
        and matching_events[0].occurred_at == member.planned_at
        and bool(matching_events[0].event_id.strip())
        and bool(matching_events[0].reason.strip())
    )


def _validate_identity_and_collisions(
    previous: ComparisonResult,
    creation_plan: PlannedMemberCreationPlan,
    target_block_index: int,
    target_attempt_index: int,
) -> ComparisonMember | None:
    identity = creation_plan.run_identity
    if (
        previous.status != "running"
        or previous.comparison_id != creation_plan.comparison_id
        or previous.comparison_execution_id != identity.comparison_execution_id
        or previous.spec_sha256 != creation_plan.comparison_spec_sha256
    ):
        raise ComparisonResultError("Identidad global incompatible con creation_plan")
    if previous.inputs is None or previous.precision is None or previous.protocol is None:
        raise ComparisonResultError("ComparisonResult no contiene contrato congelado")
    if (
        previous.inputs.base_profile.sha256 != creation_plan.base_profile_sha256
        or previous.inputs.scenario.sha256 != creation_plan.scenario_sha256
        or previous.inputs.evidence_manifest.sha256
        != creation_plan.evidence_manifest_sha256
        or previous.precision.iterations_per_run
        != creation_plan.planned_parameters.iterations
        or previous.protocol.threads != creation_plan.planned_parameters.threads
        or previous.protocol.timeout_seconds
        != creation_plan.planned_parameters.timeout_seconds
    ):
        raise ComparisonResultError("Entradas o protocolo incompatibles con creation_plan")
    member_locations = tuple(
        (block_index, attempt_index, member_index, member)
        for block_index, block in enumerate(previous.blocks)
        for attempt_index, attempt in enumerate(block.attempts)
        for member_index, member in enumerate(attempt.members)
    )
    same_id = tuple(
        location
        for location in member_locations
        if location[3].member_id == identity.member_id
    )
    if len(same_id) > 1:
        raise ComparisonResultError("member_id duplicado")
    existing_location = same_id[0] if same_id else None
    existing = existing_location[3] if existing_location is not None else None
    for _, _, _, member in member_locations:
        if member is existing:
            continue
        if (
            member.reservation.planned_run_id == identity.run_id
            or member.run_id == identity.run_id
        ):
            raise ComparisonResultError("run_id o planned_run_id ya utilizado")
        if member.reservation.token_sha256 == creation_plan.token_sha256:
            raise ComparisonResultError("token_sha256 ya utilizado por otra reserva")
    if existing is not None and not _has_initial_shape(previous, existing, creation_plan):
        raise ComparisonResultError("member_id coincide parcialmente con otro estado")
    if existing_location is not None:
        expected_location = (
            target_block_index,
            target_attempt_index,
            creation_plan.order_position - 1,
        )
        if existing_location[:3] != expected_location:
            raise ComparisonResultError(
                "member_id existente fuera de su ubicacion fisica planificada"
            )
    return existing


def validate_planned_member_candidate(
    previous: ComparisonResult,
    candidate: ComparisonResult,
    creation_plan: PlannedMemberCreationPlan,
) -> None:
    if previous is candidate:
        raise ComparisonResultError("candidate debe ser un objeto independiente")
    validate_result(previous)
    validate_planned_member_creation_plan(creation_plan)
    block_index, attempt_index = _target_location(previous, creation_plan)
    if (
        _validate_identity_and_collisions(
            previous,
            creation_plan,
            block_index,
            attempt_index,
        )
        is not None
    ):
        raise ComparisonResultError("El alta idempotente no requiere candidate")
    previous_members = previous.blocks[block_index].attempts[attempt_index].members
    candidate_members = candidate.blocks[block_index].attempts[attempt_index].members
    if len(candidate_members) != len(previous_members) + 1:
        raise ComparisonResultError("El alta requiere exactamente un miembro nuevo")
    if candidate_members[:-1] != previous_members:
        raise ComparisonResultError("Miembros anteriores modificados o reordenados")
    member = candidate_members[-1]
    if member != _initial_member(creation_plan, member.planned_at):
        raise ComparisonResultError("ComparisonMember inicial incoherente")
    if len(candidate.events) != len(previous.events) + 1:
        raise ComparisonResultError("El alta requiere exactamente un evento nuevo")
    if tuple(candidate.events[:-1]) != tuple(previous.events):
        raise ComparisonResultError("El historial de eventos no es prefijo exacto")
    event = candidate.events[-1]
    if (
        event.sequence != len(candidate.events)
        or not event.event_id.strip()
        or any(old.event_id == event.event_id for old in previous.events)
        or event.entity_type != "comparison_member"
        or event.entity_id != creation_plan.run_identity.member_id
        or event.previous_status is not None
        or event.new_status != "planned"
        or not event.reason.strip()
    ):
        raise ComparisonResultError("StateEvent inicial incoherente")
    event_time = _timestamp(event.occurred_at, "StateEvent.occurred_at")
    if event_time < _timestamp(previous.updated_at, "previous.updated_at"):
        raise ComparisonResultError("StateEvent.occurred_at anterior a previous.updated_at")
    if (
        candidate.updated_at != event.occurred_at
        or member.planned_at != event.occurred_at
        or member.reservation.created_at != event.occurred_at
    ):
        raise ComparisonResultError("Timestamps iniciales incoherentes")
    sanitized = deepcopy(candidate)
    sanitized.blocks[block_index].attempts[attempt_index].members = deepcopy(
        previous_members
    )
    sanitized.events = deepcopy(previous.events)
    sanitized.updated_at = previous.updated_at
    if sanitized != previous:
        raise ComparisonResultError("planned_member_candidate contiene un delta no autorizado")
    validate_result(candidate)


def planned_member_candidate(
    previous: ComparisonResult,
    creation_plan: PlannedMemberCreationPlan,
    occurred_at: str,
    event_id: str,
    reason: str,
) -> ComparisonResult:
    """Build one copy-on-write candidate without persistence or filesystem access."""
    validate_result(previous)
    validate_planned_member_creation_plan(creation_plan)
    block_index, attempt_index = _target_location(previous, creation_plan)
    existing = _validate_identity_and_collisions(
        previous,
        creation_plan,
        block_index,
        attempt_index,
    )
    if existing is not None:
        return previous
    _timestamp(occurred_at, "occurred_at")
    if _timestamp(occurred_at, "occurred_at") < _timestamp(
        previous.updated_at, "previous.updated_at"
    ):
        raise ComparisonResultError("occurred_at anterior a previous.updated_at")
    if not isinstance(event_id, str) or not event_id.strip():
        raise ComparisonResultError("event_id vacio")
    if any(event.event_id == event_id for event in previous.events):
        raise ComparisonResultError("event_id duplicado")
    if not isinstance(reason, str) or not reason.strip():
        raise ComparisonResultError("reason vacia")
    candidate = deepcopy(previous)
    member = _initial_member(creation_plan, occurred_at)
    candidate.blocks[block_index].attempts[attempt_index].members = [
        *candidate.blocks[block_index].attempts[attempt_index].members,
        member,
    ]
    candidate.events = [
        *candidate.events,
        StateEvent(
            sequence=len(candidate.events) + 1,
            event_id=event_id,
            occurred_at=occurred_at,
            entity_type="comparison_member",
            entity_id=creation_plan.run_identity.member_id,
            previous_status=None,
            new_status="planned",
            reason=reason,
        ),
    ]
    candidate.updated_at = occurred_at
    validate_planned_member_candidate(previous, candidate, creation_plan)
    return candidate
