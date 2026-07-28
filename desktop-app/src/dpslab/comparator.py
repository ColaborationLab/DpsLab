"""Typed orchestration for the frozen comparison protocol."""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from hashlib import sha256
from pathlib import Path
from time import monotonic, sleep
from typing import Callable

from .comparison_adapter import ComparisonMemberExecutionResponse
from .comparison_models import (
    AnalysisDiagnostics, ComparisonAnalysis, ComparisonBlock, ComparisonInputs,
    ComparisonMember, ComparisonNormalization, ComparisonPrecision,
    ComparisonProtocol, ComparisonResult, ComparisonSoftware, ComparisonValidation,
    EffectiveParameters, InputFile, InvocationRecord, MemberDps, MemberIntegrity, PairAttempt,
    PairedSensitivityResult, PlannedParameters, PrimaryAnalysisResult,
    RunArtifactReference, RunArtifactSet, RunReservationRecord, SimulationCraftIdentity,
    StructuredError, StructuredWarning, add_attempt, add_member, append_analysis_warning,
    append_member_error, append_member_warning, append_protocol_failure,
    assign_member_result, attach_execution_details, attach_preparation, finish_member, initialize_blocks, select_attempt,
    set_attempt_pause, set_block_pause, start_member, store_analysis,
    store_validation, transition, update_invocation, update_reservation, utc_now, execution_transition_candidate,
)
from .comparison_result_io import ComparisonResultStore
from .comparison_spec import ComparisonSpec
from .comparison_stats import ComparisonAnalysisError, analyze
from .runner import RunReservation


@dataclass(frozen=True, slots=True)
class MemberPlan:
    comparison_id: str
    comparison_execution_id: str
    block_index: int
    seed: int
    planned_order: str
    arm: str
    order_position: int
    attempt: int
    candidate_item_id: int
    member_id: str
    planned_run_id: str | None = None


@dataclass(frozen=True, slots=True)
class MemberPreparation:
    effective_profile_sha256: str
    invocation: InvocationRecord


def _wait_minimum(seconds: float, clock: Callable[[], float], sleeper: Callable[[float], None]) -> float:
    started = clock(); sleeper(seconds); elapsed = clock() - started
    if elapsed < seconds:
        sleeper(seconds - elapsed); elapsed = clock() - started
    if elapsed < seconds:
        raise RuntimeError("minimum_pause_not_met")
    return elapsed


def _error(code: str, stage: str) -> StructuredError:
    return StructuredError(code, code.replace("_", " "), stage)


def _warning(code: str, level: str = "advisory_warning") -> StructuredWarning:
    return StructuredWarning(code, code.replace("_", " "), level)


def _new_result(
    spec: ComparisonSpec,
    execution_id: str,
    software: ComparisonSoftware,
) -> ComparisonResult:
    root = spec.source_file.parents[1]
    evidence = InputFile(spec.evidence_manifest.relative_to(root).as_posix(), spec.evidence_sha256, True)
    result = ComparisonResult(
        spec.comparison_id, execution_id, spec.source_file.name, spec.source_sha256,
        software,
        ComparisonInputs(
            InputFile(spec.base_profile.relative_to(root).as_posix(), spec.base_profile_sha256, True),
            InputFile(spec.scenario.relative_to(root).as_posix(), spec.scenario_sha256, True), evidence,
        ),
        ComparisonNormalization("normalized", "approved", evidence),
        ComparisonPrecision("comparison_spec", "fixed_iterations", 5000, None),
        ComparisonProtocol(spec.protocol.blocks, spec.protocol.threads, spec.protocol.within_pair_pause_seconds, spec.protocol.between_block_pause_seconds, spec.protocol.timeout_seconds, spec.protocol.max_pair_attempts, True, True, False, False),
    )
    initialize_blocks(result, [ComparisonBlock(index, seed, order, execution_id) for index, (seed, order) in enumerate(zip(spec.protocol.seeds, spec.protocol.orders), 1)])
    result.add_event("comparison_execution", execution_id, None, "ready", "comparison_execution_created")
    return result


def _analysis_failure(result: ComparisonResult, store: ComparisonResultStore, exc: Exception, stage: str) -> ComparisonResult:
    store_analysis(result, ComparisonAnalysis(status="failed"))
    code = f"statistical_error:{type(exc).__name__}"
    append_protocol_failure(result, StructuredError(code, code, stage))
    store.write(result)
    result = store.commit_execution(result, execution_transition_candidate(result, "failed_protocol", "statistical_analysis_failed"))
    return result


def validate_analysis_preconditions(result: ComparisonResult, spec: ComparisonSpec) -> tuple[list[float], list[float], tuple[str, ...]]:
    errors: list[str] = []
    a_values: list[float] = []; b_values: list[float] = []; run_ids: list[str] = []
    identities: set[tuple[str, str, str]] = set()
    if len(result.blocks) != 8: errors.append("block_count")
    for expected_index, block in enumerate(result.blocks, 1):
        if block.block_index != expected_index or block.seed != spec.protocol.seeds[expected_index - 1] or block.planned_order != spec.protocol.orders[expected_index - 1] or block.status != "valid":
            errors.append(f"block_{expected_index}_identity")
        selected = [attempt for attempt in block.attempts if attempt.attempt == block.selected_attempt and attempt.status == "valid"]
        if len(selected) != 1: errors.append(f"block_{expected_index}_selected_attempt"); continue
        attempt = selected[0]
        if len(attempt.members) != 2 or {member.arm for member in attempt.members} != {"a", "b"}:
            errors.append(f"block_{expected_index}_arms"); continue
        by_arm = {member.arm: member for member in attempt.members}
        for position, arm in enumerate(block.planned_order.lower(), 1):
            member = by_arm.get(arm)
            expected_item = spec.arm_a.item_id if arm == "a" else spec.arm_b.item_id
            if member is None or member.status != "completed" or member.order_position != position or member.block_index != block.block_index or member.attempt != attempt.attempt or member.seed != block.seed or member.candidate_item_id != expected_item:
                errors.append(f"block_{expected_index}_{arm}_association"); continue
            if member.comparison_id != result.comparison_id or member.comparison_execution_id != result.comparison_execution_id or member.comparison_spec_sha256 != result.spec_sha256:
                errors.append(f"block_{expected_index}_{arm}_provenance")
            expected_parameters = EffectiveParameters(block.seed, 5000, 2, None, spec.protocol.timeout_seconds)
            if member.effective_parameters != expected_parameters or member.planned_parameters != PlannedParameters(block.seed, 5000, 2, None, spec.protocol.timeout_seconds):
                errors.append(f"block_{expected_index}_{arm}_parameters")
            identity = member.observed_simc
            if identity is None or not identity.version or not identity.revision or not identity.executable_sha256:
                errors.append(f"block_{expected_index}_{arm}_simc")
            else: identities.add((identity.version, identity.revision, identity.executable_sha256))
            refs = member.artifacts.references
            if len(refs) != 6 or len({ref.kind for ref in refs}) != 6 or any(not ref.exists or ref.sha256 is None or len(ref.sha256) != 64 or ref.valid is False for ref in refs):
                errors.append(f"block_{expected_index}_{arm}_artifacts")
            if member.integrity is None or not member.integrity.valid or member.errors or member.run_id is None or member.dps is None or member.dps.mean is None:
                errors.append(f"block_{expected_index}_{arm}_integrity")
            else:
                (a_values if arm == "a" else b_values).append(member.dps.mean); run_ids.append(member.run_id)
    if len(identities) != 1: errors.append("simc_not_uniform")
    if len(run_ids) != 16 or len(set(run_ids)) != 16: errors.append("run_ids_not_unique")
    if len(a_values) != 8 or len(b_values) != 8: errors.append("dps_count")
    if errors: raise ComparisonAnalysisError("analysis_preconditions_failed:" + ",".join(errors))
    return a_values, b_values, tuple(run_ids)


def orchestrate(
    spec: ComparisonSpec, execution_id: str, output: Path,
    run_member: Callable[[MemberPlan, RunReservation], ComparisonMemberExecutionResponse], *,
    reserve_member: Callable[[MemberPlan], RunReservation],
    prepare_member: Callable[[MemberPlan, RunReservation], MemberPreparation],
    software: ComparisonSoftware,
    analyzer: Callable[..., object] = analyze,
    clock: Callable[[], float] = monotonic,
    sleeper: Callable[[float], None] = sleep,
) -> ComparisonResult:
    result = _new_result(spec, execution_id, software)
    store = ComparisonResultStore(output); result = store.create(result)
    result = store.commit_execution(result, execution_transition_candidate(result, "running", "protocol_started"))
    a_values: list[float] = []; b_values: list[float] = []; used_runs: set[str] = set(); selected_runs: list[str] = []
    for block in result.blocks:
        block_id = f"{execution_id}:block-{block.block_index}"
        transition(block, "block", block_id, "running", "block_started", result)
        block_valid = False
        for attempt_number in range(1, spec.protocol.max_pair_attempts + 1):
            attempt_id = f"{block_id}:attempt-{attempt_number}"
            attempt = PairAttempt(attempt_number, attempt_id, execution_id, previous_attempt_id=f"{block_id}:attempt-{attempt_number-1}" if attempt_number > 1 else None)
            add_attempt(block, attempt)
            transition(attempt, "attempt", attempt_id, "running", "pair_started", result); store.write(result)
            outcomes: dict[str, ComparisonMemberExecutionResponse] = {}
            for position, upper_arm in enumerate(block.planned_order, 1):
                arm = upper_arm.lower(); spec_arm = spec.arm_a if arm == "a" else spec.arm_b
                member_id = f"{attempt_id}:{arm}"
                base_plan = MemberPlan(spec.comparison_id, execution_id, block.block_index, block.seed, block.planned_order, arm, position, attempt_number, spec_arm.item_id, member_id)
                try:
                    reservation = reserve_member(base_plan)
                    if (
                        not isinstance(reservation, RunReservation)
                        or reservation.status != "reserved"
                        or reservation.comparison_execution_id != execution_id
                        or reservation.member_id != member_id
                    ):
                        if (
                            isinstance(reservation, RunReservation)
                            and reservation.status == "reserved"
                        ):
                            reservation.abandon(
                                comparison_execution_id=reservation.comparison_execution_id,
                                member_id=reservation.member_id,
                            )
                        raise ValueError("reservation_contract_invalid")
                except Exception:
                    transition(
                        attempt,
                        "attempt",
                        attempt_id,
                        "invalid",
                        "reservation_failed",
                        result,
                    )
                    transition(
                        block,
                        "block",
                        block_id,
                        "exhausted",
                        "reservation_failed",
                        result,
                    )
                    append_protocol_failure(
                        result,
                        _error("reservation_failed", "reservation"),
                    )
                    store.write(result)
                    return store.commit_execution(
                        result,
                        execution_transition_candidate(
                            result,
                            "failed_protocol",
                            "reservation_failed",
                        ),
                    )
                plan = replace(base_plan, planned_run_id=reservation.run_id)
                reservation_record = RunReservationRecord(reservation.run_id, execution_id, member_id, sha256(reservation.reservation_token.encode()).hexdigest(), reservation.status, reservation.created_at)
                member = ComparisonMember(
                    member_id, spec.comparison_id, execution_id, spec.source_sha256,
                    block.block_index, attempt_number, arm, position, block.seed, spec_arm.item_id,
                    reservation_record, spec.base_profile_sha256, None, spec.scenario_sha256,
                    spec.evidence_sha256, PlannedParameters(block.seed, 5000, 2, None, spec.protocol.timeout_seconds),
                    None, InvocationRecord("not_built"), SimulationCraftIdentity(None, None, None), None,
                    RunArtifactSet(), None, None, [], [],
                )
                add_member(attempt, member); store.write(result)
                try:
                    preparation = prepare_member(plan, reservation)
                except Exception as exc:
                    reservation.abandon(comparison_execution_id=execution_id, member_id=member_id)
                    update_reservation(member, reservation.status)
                    update_invocation(member, InvocationRecord("failed_before_start", failure_stage="before_argv", failure_reason=type(exc).__name__))
                    append_member_error(member, _error(f"preparation_exception:{type(exc).__name__}", "preparation"))
                    transition(member, "member", member_id, "invalid", "preparation_failed", result); store.write(result)
                    continue
                attach_preparation(member, preparation.effective_profile_sha256, preparation.invocation); store.write(result)
                start_member(member, result); store.write(result)
                try:
                    outcome = run_member(plan, reservation)
                except Exception as exc:
                    missing_metadata = RunArtifactReference("metadata", "metadata.json", None, False, False)
                    missing_summary = RunArtifactReference("summary", "run_summary.json", None, False, False)
                    outcome = ComparisonMemberExecutionResponse(reservation.run_id, "invalid", False, member.invocation, missing_metadata, missing_summary, (), None, None, None, None, MemberIntegrity(False, False, False, False, False, False, False, False, False), (_error(f"adapter_exception:{type(exc).__name__}", "adapter"),), ())
                if reservation.status == "reserved":
                    reservation.abandon(comparison_execution_id=execution_id, member_id=member_id)
                    update_invocation(member, replace(member.invocation, status="failed_before_start", failure_stage="adapter_before_process"))
                else:
                    update_invocation(member, outcome.invocation)
                update_reservation(member, reservation.status)
                assign_member_result(member, outcome.run_id, outcome.dps or MemberDps(None))
                attach_execution_details(member, effective_parameters=outcome.effective_parameters, observed_simc=outcome.observed_simc, artifacts=RunArtifactSet(outcome.artifacts), integrity=outcome.integrity, errors=outcome.errors, warnings=outcome.warnings)
                duplicate = outcome.run_id in used_runs
                if outcome.run_id != reservation.run_id: append_member_error(member, _error("reserved_run_id_mismatch", "integrity"))
                if duplicate: append_member_error(member, _error("duplicate_run_id", "integrity"))
                used_runs.add(outcome.run_id)
                final = "completed" if outcome.status == "completed" and outcome.integrity.valid and not duplicate and outcome.run_id == reservation.run_id and reservation.status == "consumed" and not member.errors else "invalid"
                if position == 1:
                    try: set_attempt_pause(attempt, _wait_minimum(spec.protocol.within_pair_pause_seconds, clock, sleeper))
                    except RuntimeError: append_member_error(member, _error("minimum_pause_not_met", "pause")); final = "invalid"
                finish_member(member, final, result); outcomes[arm] = outcome; store.write(result)
            valid_pair = len(outcomes) == 2 and all(item.status == "completed" and item.integrity.valid for item in outcomes.values()) and not any(member.errors for member in attempt.members)
            transition(attempt, "attempt", attempt_id, "valid" if valid_pair else "invalid", "pair_validated", result)
            if valid_pair:
                select_attempt(block, attempt_number); block_valid = True
                if block.block_index < spec.protocol.blocks:
                    try: set_block_pause(block, _wait_minimum(spec.protocol.between_block_pause_seconds, clock, sleeper))
                    except RuntimeError:
                        transition(block, "block", block_id, "exhausted", "minimum_pause_not_met", result)
                        append_protocol_failure(result, _error("minimum_pause_not_met", "protocol"))
                        store.write(result); return store.commit_execution(result, execution_transition_candidate(result, "failed_protocol", "minimum_pause_not_met"))
                transition(block, "block", block_id, "valid", "valid_pair_selected", result); store.write(result); break
            if attempt_number < spec.protocol.max_pair_attempts:
                transition(block, "block", block_id, "retry_pending", "pair_retry_required", result)
                try: _wait_minimum(spec.protocol.between_block_pause_seconds, clock, sleeper)
                except RuntimeError:
                    transition(block, "block", block_id, "exhausted", "minimum_pause_not_met", result)
                    append_protocol_failure(result, _error("minimum_pause_not_met", "protocol"))
                    store.write(result); return store.commit_execution(result, execution_transition_candidate(result, "failed_protocol", "minimum_pause_not_met"))
                transition(block, "block", block_id, "running", "pair_retry_started", result); store.write(result)
            else:
                transition(block, "block", block_id, "exhausted", "pair_attempts_exhausted", result)
                append_protocol_failure(result, _error(f"block_{block.block_index}_exhausted", "protocol")); store.write(result)
        if not block_valid:
            store.write(result); return store.commit_execution(result, execution_transition_candidate(result, "failed_protocol", "block_exhausted"))
    try:
        a_values, b_values, selected = validate_analysis_preconditions(result, spec)
        selected_runs = list(selected)
    except Exception as exc:
        return _analysis_failure(result, store, exc, "preconditions")
    try:
        stats = analyzer(a_values, b_values, confidence_level=spec.analysis.confidence_level, epsilon_percent=spec.analysis.epsilon_percent)
        numeric = (stats.primary.estimate_percent, stats.primary.standard_error, stats.primary.degrees_of_freedom, stats.primary.t_critical, stats.primary.ci_low, stats.primary.ci_high, stats.paired_sensitivity.estimate_percent, stats.paired_sensitivity.t_critical)
        if any(not math.isfinite(float(value)) for value in numeric) or stats.primary.degrees_of_freedom <= 0:
            raise ComparisonAnalysisError("invalid_analysis_result")
        if getattr(stats.primary, "method", "welch_delta") != "welch_delta" or getattr(stats.paired_sensitivity, "method", "paired_t") != "paired_t":
            raise ComparisonAnalysisError("incorrect_analysis_method")
    except Exception as exc:
        return _analysis_failure(result, store, exc, "analysis")
    primary = PrimaryAnalysisResult("welch_delta", stats.primary.estimate_percent, stats.primary.standard_error, stats.primary.degrees_of_freedom, stats.primary.t_critical, stats.primary.ci_low, stats.primary.ci_high, stats.primary.classification)
    paired = PairedSensitivityResult("paired_t", stats.paired_sensitivity.estimate_percent, stats.paired_sensitivity.standard_error, stats.paired_sensitivity.degrees_of_freedom, stats.paired_sensitivity.t_critical, stats.paired_sensitivity.ci_low, stats.paired_sensitivity.ci_high, stats.paired_sensitivity.classification)
    store_analysis(result, ComparisonAnalysis("completed", None, False, primary, paired, AnalysisDiagnostics(stats.estimate_difference_percent_points, stats.classification_disagreement), stats.final_classification))
    if stats.classification_disagreement: append_analysis_warning(result, _warning("primary_and_paired_classifications_differ", "analysis_warning"))
    store_validation(result, ComparisonValidation(8, 8, tuple(sorted(selected_runs)), (), True, True, True, True, True))
    store.write(result)
    return store.commit_execution(result, execution_transition_candidate(result, "inconclusive" if stats.final_classification == "inconclusive" else "completed", "analysis_completed"))
