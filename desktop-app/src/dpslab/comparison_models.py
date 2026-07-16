"""Closed, typed durable models for ``comparison_result`` schema 0.1."""

from __future__ import annotations

from dataclasses import dataclass, field, fields, replace
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Literal
from uuid import uuid4


class ComparisonResultError(ValueError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True, slots=True)
class StructuredError:
    code: str
    message: str
    stage: str


@dataclass(frozen=True, slots=True)
class StructuredWarning:
    code: str
    message: str
    level: str


@dataclass(frozen=True, slots=True)
class DpsLabSourceIdentity:
    source_identity_kind: str
    version: str
    commit: str | None
    dirty_state: bool | None
    source_tree_sha256: str | None
    source_inventory_method: str | None = None
    source_inventory: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class SimulationCraftIdentity:
    version: str | None
    revision: str | None
    executable_sha256: str | None


@dataclass(frozen=True, slots=True)
class PythonIdentity:
    version: str
    implementation: str


@dataclass(frozen=True, slots=True)
class ScipyIdentity:
    requirement: str
    version: str


@dataclass(frozen=True, slots=True)
class PlatformIdentity:
    system: str
    release: str
    machine: str
    python_platform: str


@dataclass(frozen=True, slots=True)
class ComparisonSoftware:
    python: PythonIdentity
    dpslab: DpsLabSourceIdentity
    scipy: ScipyIdentity
    platform: PlatformIdentity
    simulationcraft: SimulationCraftIdentity


SoftwareIdentity = ComparisonSoftware


@dataclass(frozen=True, slots=True)
class InputFile:
    path: str
    sha256: str
    hash_verified: bool


@dataclass(frozen=True, slots=True)
class ComparisonInputs:
    base_profile: InputFile
    scenario: InputFile
    evidence_manifest: InputFile


@dataclass(frozen=True, slots=True)
class ComparisonNormalization:
    policy: str
    status: str
    evidence: InputFile


NormalizationRecord = ComparisonNormalization


@dataclass(frozen=True, slots=True)
class ComparisonPrecision:
    precision_source: str
    precision_mode: str
    iterations_per_run: int
    target_error: float | None


PrecisionRecord = ComparisonPrecision


@dataclass(frozen=True, slots=True)
class ComparisonProtocol:
    blocks: int
    threads: int
    within_pair_pause_seconds: float
    between_block_pause_seconds: float
    timeout_seconds: float
    max_pair_attempts: int
    retry_full_pair: bool
    require_all_blocks_valid: bool
    exclude_dps_outliers: bool
    early_stopping: bool


ProtocolRecord = ComparisonProtocol


@dataclass(frozen=True, slots=True)
class RunReservationRecord:
    planned_run_id: str
    owner_execution_id: str
    owner_member_id: str
    token_sha256: str
    status: Literal["reserved", "consumed", "abandoned"]
    created_at: str


@dataclass(frozen=True, slots=True)
class PlannedParameters:
    seed: int
    iterations: int
    threads: int
    target_error: None
    timeout_seconds: float


@dataclass(frozen=True, slots=True)
class EffectiveParameters:
    seed: int | None
    iterations: int | None
    threads: int | None
    target_error: float | None
    timeout_seconds: float | None


@dataclass(frozen=True, slots=True)
class InvocationRecord:
    status: Literal["not_built", "built", "process_started", "completed", "failed_before_start", "failed_after_start"]
    portable_argv: tuple[str, ...] | None = None
    portable_argv_sha256: str | None = None
    process_argv_sha256: str | None = None
    executable_sha256: str | None = None
    executable_source: str | None = None
    argument_list: bool | None = None
    shell: bool | None = None
    built_at: str | None = None
    process_started_at: str | None = None
    failure_stage: str | None = None
    failure_reason: str | None = None


@dataclass(frozen=True, slots=True)
class RunArtifactReference:
    kind: str
    path: str
    sha256: str | None
    exists: bool
    valid: bool | None


@dataclass(frozen=True, slots=True)
class RunArtifactSet:
    references: tuple[RunArtifactReference, ...] = ()


@dataclass(frozen=True, slots=True)
class MemberDps:
    mean: float | None


@dataclass(frozen=True, slots=True)
class MemberIntegrity:
    run_id_verified: bool
    reservation_verified: bool
    parameters_verified: bool
    profile_verified: bool
    scenario_verified: bool
    only_neck_changed: bool
    simc_identity_verified: bool
    artifacts_verified: bool
    dps_verified: bool

    @property
    def valid(self) -> bool:
        return all(getattr(self, item.name) for item in fields(self))


@dataclass(slots=True)
class ComparisonMember:
    member_id: str
    comparison_id: str
    comparison_execution_id: str
    comparison_spec_sha256: str
    block_index: int
    attempt: int
    arm: Literal["a", "b"]
    order_position: int
    seed: int
    candidate_item_id: int
    reservation: RunReservationRecord
    base_profile_sha256: str
    effective_profile_sha256: str | None
    scenario_sha256: str
    evidence_manifest_sha256: str
    planned_parameters: PlannedParameters
    effective_parameters: EffectiveParameters | None
    invocation: InvocationRecord
    expected_simc: SimulationCraftIdentity
    observed_simc: SimulationCraftIdentity | None
    artifacts: RunArtifactSet
    dps: MemberDps | None
    integrity: MemberIntegrity | None
    errors: list[StructuredError]
    warnings: list[StructuredWarning]
    status: Literal["planned", "running", "completed", "invalid", "interrupted"] = "planned"
    planned_at: str = field(default_factory=utc_now)
    run_id: str | None = None
    started_at: str | None = None
    finished_at: str | None = None
    duration_seconds: float | None = None

    @property
    def planned_run_id(self) -> str:
        return self.reservation.planned_run_id


@dataclass(slots=True)
class PairAttempt:
    attempt: int
    attempt_id: str
    comparison_execution_id: str
    status: Literal["planned", "running", "valid", "invalid", "interrupted"] = "planned"
    previous_attempt_id: str | None = None
    planned_at: str = field(default_factory=utc_now)
    members: list[ComparisonMember] = field(default_factory=list)
    errors: list[StructuredError] = field(default_factory=list)
    within_pair_pause_seconds: float | None = None


@dataclass(slots=True)
class ComparisonBlock:
    block_index: int
    seed: int
    planned_order: Literal["AB", "BA"]
    comparison_execution_id: str
    status: Literal["planned", "running", "retry_pending", "valid", "exhausted"] = "planned"
    selected_attempt: int | None = None
    attempts: list[PairAttempt] = field(default_factory=list)
    between_block_pause_seconds: float | None = None


@dataclass(frozen=True, slots=True)
class PrimaryAnalysisResult:
    method: str
    estimate_percent: float
    standard_error: float
    degrees_of_freedom: float
    t_critical: float
    ci_low: float
    ci_high: float
    classification: str


PrimaryAnalysis = PrimaryAnalysisResult


@dataclass(frozen=True, slots=True)
class PairedSensitivityResult(PrimaryAnalysisResult):
    pass


PairedSensitivityAnalysis = PairedSensitivityResult


@dataclass(frozen=True, slots=True)
class AnalysisDiagnostics:
    estimate_difference_percent_points: float
    classification_disagreement: bool


@dataclass(slots=True)
class ComparisonAnalysis:
    status: Literal["not_run", "completed", "failed"] = "not_run"
    analysis_seed: None = None
    stochastic_analysis: bool = False
    primary: PrimaryAnalysisResult | None = None
    paired_sensitivity: PairedSensitivityResult | None = None
    diagnostics: AnalysisDiagnostics | None = None
    final_classification: str | None = None


@dataclass(frozen=True, slots=True)
class ComparisonValidation:
    valid_blocks: int
    required_valid_blocks: int
    valid_run_ids: tuple[str, ...]
    duplicate_run_ids: tuple[str, ...]
    all_seeds_verified: bool
    all_orders_verified: bool
    all_parameters_verified: bool
    only_neck_changed: bool
    provenance_complete: bool


@dataclass(frozen=True, slots=True)
class StateEvent:
    sequence: int
    event_id: str
    occurred_at: str
    entity_type: str
    entity_id: str
    previous_status: str | None
    new_status: str
    reason: str


ComparisonEvent = StateEvent


def empty_validation() -> ComparisonValidation:
    return ComparisonValidation(0, 8, (), (), False, False, False, False, False)


@dataclass(slots=True)
class ComparisonResult:
    comparison_id: str
    comparison_execution_id: str
    spec_path: str
    spec_sha256: str
    software: ComparisonSoftware | None = None
    inputs: ComparisonInputs | None = None
    normalization: ComparisonNormalization | None = None
    precision: ComparisonPrecision | None = None
    protocol: ComparisonProtocol | None = None
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    status: Literal["blocked", "ready", "running", "completed", "inconclusive", "failed_protocol"] = "ready"
    started_at: str | None = None
    finished_at: str | None = None
    blocks: list[ComparisonBlock] = field(default_factory=list)
    events: list[StateEvent] = field(default_factory=list)
    validation: ComparisonValidation = field(default_factory=empty_validation)
    analysis: ComparisonAnalysis = field(default_factory=ComparisonAnalysis)
    blocking_errors: list[StructuredError] = field(default_factory=list)
    protocol_failures: list[StructuredError] = field(default_factory=list)
    analysis_warnings: list[StructuredWarning] = field(default_factory=list)
    advisory_warnings: list[StructuredWarning] = field(default_factory=list)

    def add_event(self, entity_type: str, entity_id: str, previous: str | None, new: str, reason: str) -> None:
        self.events = [*self.events, StateEvent(len(self.events) + 1, uuid4().hex, utc_now(), entity_type, entity_id, previous, new, reason)]
        self.updated_at = utc_now()

    def transition_execution(self, new: str, reason: str) -> None:
        transition(self, "comparison_execution", self.comparison_execution_id, new, reason, self)
        if new == "running" and self.started_at is None:
            self.started_at = utc_now()
        if new in {"completed", "inconclusive", "failed_protocol"}:
            self.finished_at = utc_now()

    def to_dict(self) -> dict[str, object]:
        from .comparison_result_io import result_to_document
        return result_to_document(self)

    @classmethod
    def from_dict(cls, document: dict[str, object]) -> "ComparisonResult":
        from .comparison_result_io import result_from_document
        return result_from_document(document)


MEMBER_TRANSITIONS = {"planned": {"running", "invalid", "interrupted"}, "running": {"completed", "invalid", "interrupted"}}
ATTEMPT_TRANSITIONS = {"planned": {"running"}, "running": {"valid", "invalid", "interrupted"}}
BLOCK_TRANSITIONS = {"planned": {"running"}, "running": {"valid", "retry_pending", "exhausted"}, "retry_pending": {"running", "exhausted"}}
EXECUTION_TRANSITIONS = {"ready": {"blocked", "running"}, "running": {"blocked", "completed", "inconclusive", "failed_protocol"}}
ORPHAN_CHECKS = frozenset({"confirmed_clear", "active_process_found", "unknown"})


def transition(entity: object, entity_type: str, entity_id: str, new: str, reason: str, result: ComparisonResult) -> None:
    tables = {"member": MEMBER_TRANSITIONS, "attempt": ATTEMPT_TRANSITIONS, "block": BLOCK_TRANSITIONS, "comparison_execution": EXECUTION_TRANSITIONS}
    previous = getattr(entity, "status")
    if new not in tables[entity_type].get(previous, set()):
        raise ComparisonResultError(f"Transicion {entity_type} no valida: {previous} -> {new}")
    setattr(entity, "status", new)
    result.add_event(entity_type, entity_id, previous, new, reason)


def add_attempt(block: ComparisonBlock, attempt: PairAttempt) -> None:
    if block.status not in {"running", "retry_pending"} or attempt.comparison_execution_id != block.comparison_execution_id:
        raise ComparisonResultError("No se puede agregar el intento")
    if any(item.attempt_id == attempt.attempt_id or item.attempt == attempt.attempt for item in block.attempts):
        raise ComparisonResultError("Intento duplicado")
    block.attempts = [*block.attempts, attempt]


def initialize_blocks(result: ComparisonResult, blocks: list[ComparisonBlock]) -> None:
    if result.status != "ready" or result.blocks or len(blocks) != 8:
        raise ComparisonResultError("Bloques no inicializables")
    if any(block.comparison_execution_id != result.comparison_execution_id for block in blocks):
        raise ComparisonResultError("Bloque de otra ejecucion")
    result.blocks = list(blocks)


def add_member(attempt: PairAttempt, member: ComparisonMember) -> None:
    if attempt.status != "running" or member.comparison_execution_id != attempt.comparison_execution_id:
        raise ComparisonResultError("No se puede agregar el miembro")
    if len(attempt.members) >= 2 or any(item.member_id == member.member_id or item.arm == member.arm for item in attempt.members):
        raise ComparisonResultError("Miembro duplicado o pareja completa")
    attempt.members = [*attempt.members, member]


def attach_preparation(member: ComparisonMember, effective_profile_sha256: str, invocation: InvocationRecord) -> None:
    if member.status != "planned": raise ComparisonResultError("Miembro no planificado")
    member.effective_profile_sha256 = effective_profile_sha256; member.invocation = invocation


def update_reservation(member: ComparisonMember, status: str) -> None:
    if member.status in {"completed", "invalid", "interrupted"}: raise ComparisonResultError("Miembro terminal")
    member.reservation = replace(member.reservation, status=status)


def update_invocation(member: ComparisonMember, invocation: InvocationRecord) -> None:
    if member.status in {"completed", "invalid", "interrupted"}: raise ComparisonResultError("Miembro terminal")
    member.invocation = invocation


def append_member_error(member: ComparisonMember, error: StructuredError) -> None:
    if member.status in {"completed", "invalid", "interrupted"}: raise ComparisonResultError("Miembro terminal")
    member.errors = [*member.errors, error]


def append_member_warning(member: ComparisonMember, warning: StructuredWarning) -> None:
    if member.status in {"completed", "invalid", "interrupted"}: raise ComparisonResultError("Miembro terminal")
    member.warnings = [*member.warnings, warning]


def start_member(member: ComparisonMember, result: ComparisonResult) -> None:
    transition(member, "member", member.member_id, "running", "member_started", result); member.started_at = utc_now()


def assign_member_result(member: ComparisonMember, run_id: str, dps: MemberDps) -> None:
    if member.status != "running": raise ComparisonResultError("Miembro no running")
    if member.run_id is not None and member.run_id != run_id: raise ComparisonResultError("run_id inmutable")
    member.run_id = run_id; member.dps = dps


def attach_execution_details(
    member: ComparisonMember, *, effective_parameters: EffectiveParameters | None,
    observed_simc: SimulationCraftIdentity | None, artifacts: RunArtifactSet,
    integrity: MemberIntegrity, errors: tuple[StructuredError, ...],
    warnings: tuple[StructuredWarning, ...],
) -> None:
    if member.status != "running": raise ComparisonResultError("Miembro no running")
    member.effective_parameters = effective_parameters
    member.observed_simc = observed_simc
    member.artifacts = artifacts
    member.integrity = integrity
    member.errors = [*member.errors, *errors]
    member.warnings = [*member.warnings, *warnings]


def finish_member(member: ComparisonMember, status: str, result: ComparisonResult) -> None:
    transition(member, "member", member.member_id, status, "member_finished", result); member.finished_at = utc_now()


def set_attempt_pause(attempt: PairAttempt, seconds: float) -> None:
    if attempt.status != "running": raise ComparisonResultError("Intento no running")
    attempt.within_pair_pause_seconds = seconds


def set_block_pause(block: ComparisonBlock, seconds: float) -> None:
    if block.status != "running": raise ComparisonResultError("Bloque no running")
    block.between_block_pause_seconds = seconds


def select_attempt(block: ComparisonBlock, attempt_number: int) -> None:
    if block.selected_attempt is not None or not any(item.attempt == attempt_number and item.status == "valid" for item in block.attempts):
        raise ComparisonResultError("Intento seleccionado invalido")
    block.selected_attempt = attempt_number


def append_protocol_failure(result: ComparisonResult, error: StructuredError) -> None:
    result.protocol_failures = [*result.protocol_failures, error]


def append_analysis_warning(result: ComparisonResult, warning: StructuredWarning) -> None:
    result.analysis_warnings = [*result.analysis_warnings, warning]


def store_analysis(result: ComparisonResult, analysis: ComparisonAnalysis) -> None:
    if result.status != "running" or result.analysis.status != "not_run": raise ComparisonResultError("Analisis no asignable")
    result.analysis = analysis


def store_validation(result: ComparisonResult, validation: ComparisonValidation) -> None:
    if result.status != "running": raise ComparisonResultError("Validacion no asignable")
    result.validation = validation


def validate_result(result: ComparisonResult) -> None:
    if result.software is None or result.inputs is None or result.normalization is None or result.precision is None or result.protocol is None:
        raise ComparisonResultError("comparison_result incompleto")
    if result.protocol.blocks != 8 or len(result.blocks) != 8:
        raise ComparisonResultError("Se requieren exactamente ocho bloques")
    if any(block.comparison_execution_id != result.comparison_execution_id for block in result.blocks):
        raise ComparisonResultError("Bloque de otra ejecucion")
    event_ids: set[str] = set()
    for sequence, event in enumerate(result.events, 1):
        if event.sequence != sequence or event.event_id in event_ids:
            raise ComparisonResultError("Registro de eventos no es append-only")
        event_ids.add(event.event_id)
    run_ids: set[str] = set()
    reservations: set[str] = set()
    for block in result.blocks:
        if block.selected_attempt is not None and not any(a.attempt == block.selected_attempt and a.status == "valid" for a in block.attempts):
            raise ComparisonResultError("selected_attempt no apunta a intento valido")
        for attempt in block.attempts:
            if attempt.comparison_execution_id != result.comparison_execution_id:
                raise ComparisonResultError("Intento de otra ejecucion")
            for member in attempt.members:
                if member.comparison_execution_id != result.comparison_execution_id or member.comparison_spec_sha256 != result.spec_sha256:
                    raise ComparisonResultError("Miembro de otra ejecucion o spec")
                owner = f"{member.reservation.owner_execution_id}:{member.reservation.owner_member_id}"
                if owner in reservations:
                    raise ComparisonResultError("Reserva duplicada")
                reservations.add(owner)
                if member.run_id is not None and member.status == "completed":
                    if member.run_id in run_ids:
                        raise ComparisonResultError("run_id duplicado")
                    run_ids.add(member.run_id)


def recover_interrupted(result: ComparisonResult, orphan_check: Callable[[], str]) -> str:
    check = orphan_check()
    if check not in ORPHAN_CHECKS:
        raise ComparisonResultError("Resultado de comprobacion de procesos no valido")
    if check != "confirmed_clear":
        if result.status in {"ready", "running"}:
            result.transition_execution("blocked", f"orphan_check_{check}")
        return "blocked"
    changed = False
    for block in result.blocks:
        if block.status not in {"running", "retry_pending"} or not block.attempts:
            continue
        attempt = block.attempts[-1]
        if attempt.status != "running":
            continue
        for member in attempt.members:
            if member.status == "running":
                transition(member, "member", member.member_id, "interrupted", "recovered_after_restart", result)
                changed = True
        transition(attempt, "attempt", attempt.attempt_id, "interrupted", "pair_interrupted", result)
        transition(block, "block", f"{result.comparison_execution_id}:block-{block.block_index}", "retry_pending" if len(block.attempts) < result.protocol.max_pair_attempts else "exhausted", "full_pair_retry_required" if len(block.attempts) < result.protocol.max_pair_attempts else "attempts_exhausted", result)
        changed = True
    return "recovered" if changed else "unchanged"


def recover_from_json(path: Path, *, expected_spec_sha256: str, expected_execution_id: str, orphan_check: Callable[[], str]) -> ComparisonResult:
    from .comparison_result_io import ComparisonResultStore
    store = ComparisonResultStore(path)
    result = store.read()
    if result.spec_sha256 != expected_spec_sha256 or result.comparison_execution_id != expected_execution_id:
        raise ComparisonResultError("Identidad de spec o ejecucion incorrecta")
    before = tuple(result.events)
    recover_interrupted(result, orphan_check)
    if tuple(result.events) != before:
        store.write(result)
    return result


class AtomicComparisonStore:
    """Compatibility name for the single JSON boundary."""

    def __new__(cls, path: Path):
        from .comparison_result_io import ComparisonResultStore
        return ComparisonResultStore(path)


def validate_result_document(document: dict[str, object]) -> None:
    ComparisonResult.from_dict(document)


def execution_transition_candidate(previous: ComparisonResult, new: str, reason: str) -> ComparisonResult:
    candidate = deepcopy(previous)
    candidate.transition_execution(new, reason)
    return candidate
