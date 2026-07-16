"""Pure transactional candidates and validation for comparison members."""

from __future__ import annotations

import math
from copy import deepcopy
from datetime import datetime

from .comparison_models import (
    ComparisonMember,
    ComparisonResult,
    ComparisonResultError,
    StateEvent,
    StructuredError,
)


_ALLOWED_MEMBER_TRANSITIONS = {
    ("planned", "running"),
    ("planned", "invalid"),
    ("planned", "interrupted"),
    ("running", "completed"),
    ("running", "invalid"),
    ("running", "interrupted"),
}
_TERMINAL_MEMBER_STATUSES = {"completed", "invalid", "interrupted"}
_PROCESS_STARTED_INVOCATIONS = {"process_started", "completed", "failed_after_start"}


def _is_sha256(value: str | None) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdefABCDEF" for character in value)
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


def _member_locations(result: ComparisonResult, member_id: str) -> list[tuple[int, int, int, ComparisonMember]]:
    return [
        (block_index, attempt_index, member_index, member)
        for block_index, block in enumerate(result.blocks)
        for attempt_index, attempt in enumerate(block.attempts)
        for member_index, member in enumerate(attempt.members)
        if member.member_id == member_id
    ]


def _unique_member(result: ComparisonResult, member_id: str) -> tuple[int, int, int, ComparisonMember]:
    locations = _member_locations(result, member_id)
    if not locations:
        raise ComparisonResultError("ComparisonMember ausente")
    if len(locations) != 1:
        raise ComparisonResultError("member_id duplicado")
    return locations[0]


def _reservation_belongs_to_member(result: ComparisonResult, member: ComparisonMember) -> bool:
    reservation = member.reservation
    try:
        _timestamp(reservation.created_at, "reservation.created_at")
    except ComparisonResultError:
        return False
    return (
        bool(reservation.planned_run_id)
        and _is_sha256(reservation.token_sha256)
        and reservation.owner_execution_id == result.comparison_execution_id
        and reservation.owner_execution_id == member.comparison_execution_id
        and reservation.owner_member_id == member.member_id
        and member.comparison_id == result.comparison_id
        and member.comparison_spec_sha256 == result.spec_sha256
    )


def _process_started(member: ComparisonMember) -> bool:
    return (
        member.invocation.status in _PROCESS_STARTED_INVOCATIONS
        or member.invocation.process_started_at is not None
    )


def _invocation_is_built(member: ComparisonMember) -> bool:
    invocation = member.invocation
    if invocation.built_at is not None:
        try:
            _timestamp(invocation.built_at, "invocation.built_at")
        except ComparisonResultError:
            return False
    return (
        invocation.status == "built"
        and bool(invocation.portable_argv)
        and _is_sha256(invocation.portable_argv_sha256)
        and _is_sha256(invocation.process_argv_sha256)
        and _is_sha256(invocation.executable_sha256)
        and bool(invocation.executable_source)
        and invocation.argument_list is True
        and invocation.shell is False
        and invocation.built_at is not None
        and invocation.process_started_at is None
    )


def _has_durable_cause(member: ComparisonMember) -> bool:
    return any(
        isinstance(error, StructuredError)
        and error.code.strip()
        and error.message.strip()
        and error.stage.strip()
        for error in member.errors
    )


def _artifacts_are_complete(member: ComparisonMember) -> bool:
    references = member.artifacts.references
    return (
        len(references) == 6
        and len({reference.kind for reference in references}) == 6
        and all(
            reference.exists
            and reference.valid is not False
            and _is_sha256(reference.sha256)
            for reference in references
        )
    )


def _parameters_match(member: ComparisonMember) -> bool:
    effective = member.effective_parameters
    planned = member.planned_parameters
    return (
        effective is not None
        and effective.seed == planned.seed
        and effective.iterations == planned.iterations
        and effective.threads == planned.threads
        and effective.target_error == planned.target_error
        and effective.timeout_seconds == planned.timeout_seconds
    )


def _accepted_result(member: ComparisonMember) -> bool:
    observed = member.observed_simc
    return (
        member.reservation.status == "consumed"
        and member.invocation.status == "completed"
        and member.run_id == member.planned_run_id
        and member.run_id is not None
        and member.dps is not None
        and member.dps.mean is not None
        and math.isfinite(member.dps.mean)
        and member.dps.mean > 0
        and _parameters_match(member)
        and _is_sha256(member.effective_profile_sha256)
        and observed is not None
        and bool(observed.version)
        and bool(observed.revision)
        and _is_sha256(observed.executable_sha256)
        and _artifacts_are_complete(member)
        and member.integrity is not None
        and member.integrity.valid
    )


def validate_member_transition_preconditions(
    result: ComparisonResult,
    member: ComparisonMember,
    new_status: str,
) -> None:
    transition = (member.status, new_status)
    if transition not in _ALLOWED_MEMBER_TRANSITIONS:
        raise ComparisonResultError(f"Transicion member no valida: {member.status} -> {new_status}")
    if not _reservation_belongs_to_member(result, member):
        raise ComparisonResultError("Reserva o identidad del miembro incoherente")
    if member.finished_at is not None:
        raise ComparisonResultError("finished_at ya confirmado")

    if member.status == "planned":
        if member.started_at is not None:
            raise ComparisonResultError("Miembro planned con started_at")
        if _process_started(member):
            raise ComparisonResultError("Proceso ya iniciado para miembro planned")
        if new_status == "running":
            if member.reservation.status != "reserved":
                raise ComparisonResultError("Reserva no lista para ejecucion")
            if not _invocation_is_built(member):
                raise ComparisonResultError("Invocacion no construida")
            if (
                member.run_id is not None
                or member.dps is not None
                or member.effective_parameters is not None
                or member.observed_simc is not None
                or member.artifacts.references
                or member.integrity is not None
                or member.errors
            ):
                raise ComparisonResultError("Resultado o diagnostico incompatible con planned -> running")
        else:
            if member.reservation.status != "abandoned":
                raise ComparisonResultError("Terminal planned exige reserva abandonada")
            if not _has_durable_cause(member):
                raise ComparisonResultError("Falta causa durable del miembro")
            if _accepted_result(member):
                raise ComparisonResultError("Existe resultado final aceptado")
            if member.integrity is not None and member.integrity.valid:
                raise ComparisonResultError("Integridad terminal aprobada incompatible")
        return

    if member.started_at is None:
        raise ComparisonResultError("Miembro running sin started_at")
    if member.reservation.status != "consumed":
        raise ComparisonResultError("Miembro running exige reserva consumida")
    if not _process_started(member):
        raise ComparisonResultError("Falta evidencia durable de proceso iniciado")
    if new_status == "completed":
        if not _accepted_result(member):
            raise ComparisonResultError("Resultado final o integridad incompletos")
        if member.errors:
            raise ComparisonResultError("Completion incompatible con errores del miembro")
    else:
        if not _has_durable_cause(member):
            raise ComparisonResultError("Falta causa durable del miembro")
        if _accepted_result(member):
            raise ComparisonResultError("Resultado final aceptado incompatible con terminal no elegible")


def _validate_candidate_timestamps(
    previous: ComparisonResult,
    previous_member: ComparisonMember,
    candidate: ComparisonResult,
    candidate_member: ComparisonMember,
    event: StateEvent,
) -> None:
    event_time = _timestamp(event.occurred_at, "StateEvent.occurred_at")
    previous_updated = _timestamp(previous.updated_at, "previous.updated_at")
    if event_time < previous_updated:
        raise ComparisonResultError("StateEvent.occurred_at anterior a previous.updated_at")
    if candidate.updated_at != event.occurred_at:
        raise ComparisonResultError("updated_at no coincide con StateEvent.occurred_at")
    _timestamp(candidate.updated_at, "candidate.updated_at")

    transition = (previous_member.status, candidate_member.status)
    if transition == ("planned", "running"):
        if candidate_member.started_at != event.occurred_at or candidate_member.finished_at is not None:
            raise ComparisonResultError("Timestamps invalidos para planned -> running")
    elif previous_member.status == "planned":
        if candidate_member.started_at is not None or candidate_member.finished_at != event.occurred_at:
            raise ComparisonResultError("Timestamps invalidos para terminal desde planned")
    else:
        if (
            candidate_member.started_at != previous_member.started_at
            or candidate_member.finished_at != event.occurred_at
        ):
            raise ComparisonResultError("Timestamps invalidos para terminal desde running")

    if candidate_member.started_at is not None:
        started = _timestamp(candidate_member.started_at, "member.started_at")
        if candidate_member.finished_at is not None:
            finished = _timestamp(candidate_member.finished_at, "member.finished_at")
            if finished < started:
                raise ComparisonResultError("finished_at anterior a started_at")


def validate_member_candidate(
    previous: ComparisonResult,
    candidate: ComparisonResult,
    member_id: str,
) -> None:
    if previous is candidate:
        raise ComparisonResultError("candidate debe ser un objeto independiente")
    previous_location = _unique_member(previous, member_id)
    candidate_location = _unique_member(candidate, member_id)
    if previous_location[:3] != candidate_location[:3]:
        raise ComparisonResultError("ComparisonMember movido")
    previous_member = previous_location[3]
    candidate_member = candidate_location[3]

    validate_member_transition_preconditions(previous, previous_member, candidate_member.status)

    normalized_member = deepcopy(candidate_member)
    normalized_member.status = previous_member.status
    normalized_member.started_at = previous_member.started_at
    normalized_member.finished_at = previous_member.finished_at
    if normalized_member != previous_member:
        raise ComparisonResultError("ComparisonMember contiene un delta no autorizado")

    sanitized = deepcopy(candidate)
    block_index, attempt_index, member_index = candidate_location[:3]
    sanitized.blocks[block_index].attempts[attempt_index].members[member_index] = deepcopy(previous_member)
    sanitized.events = deepcopy(previous.events)
    sanitized.updated_at = previous.updated_at
    if sanitized != previous:
        raise ComparisonResultError("commit_member contiene un delta no autorizado")

    if len(candidate.events) != len(previous.events) + 1:
        raise ComparisonResultError("La transicion member requiere exactamente un evento nuevo")
    if tuple(candidate.events[:-1]) != tuple(previous.events):
        raise ComparisonResultError("El historial de eventos no es prefijo exacto")
    event = candidate.events[-1]
    if (
        event.sequence != len(candidate.events)
        or not event.event_id.strip()
        or any(previous_event.event_id == event.event_id for previous_event in previous.events)
    ):
        raise ComparisonResultError("sequence o event_id de member invalido")
    if (
        event.entity_type,
        event.entity_id,
        event.previous_status,
        event.new_status,
    ) != (
        "member",
        member_id,
        previous_member.status,
        candidate_member.status,
    ):
        raise ComparisonResultError("StateEvent no corresponde al miembro")
    if not event.reason.strip():
        raise ComparisonResultError("Motivo de transicion member vacio")
    _validate_candidate_timestamps(previous, previous_member, candidate, candidate_member, event)


def member_transition_candidate(
    previous: ComparisonResult,
    member_id: str,
    new_status: str,
    occurred_at: str,
    event_id: str,
    reason: str,
) -> ComparisonResult:
    _, _, _, previous_member = _unique_member(previous, member_id)
    validate_member_transition_preconditions(previous, previous_member, new_status)
    event_time = _timestamp(occurred_at, "StateEvent.occurred_at")
    if event_time < _timestamp(previous.updated_at, "previous.updated_at"):
        raise ComparisonResultError("StateEvent.occurred_at anterior a previous.updated_at")
    if not event_id.strip():
        raise ComparisonResultError("event_id de member vacio")
    if any(event.event_id == event_id for event in previous.events):
        raise ComparisonResultError("event_id de member duplicado")
    if not reason.strip():
        raise ComparisonResultError("Motivo de transicion member vacio")

    candidate = deepcopy(previous)
    _, _, _, member = _unique_member(candidate, member_id)
    member.status = new_status
    if (previous_member.status, new_status) == ("planned", "running"):
        member.started_at = occurred_at
    elif new_status in _TERMINAL_MEMBER_STATUSES:
        member.finished_at = occurred_at
    candidate.events = [
        *candidate.events,
        StateEvent(
            len(candidate.events) + 1,
            event_id,
            occurred_at,
            "member",
            member_id,
            previous_member.status,
            new_status,
            reason,
        ),
    ]
    candidate.updated_at = occurred_at
    validate_member_candidate(previous, candidate, member_id)
    return candidate
