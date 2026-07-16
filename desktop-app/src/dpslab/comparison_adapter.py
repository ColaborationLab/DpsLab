"""Typed boundary between comparison orchestration and the SimulationCraft runner.

This module deliberately exposes no CLI and does not decide global protocol state.
"""

from __future__ import annotations

import json
import math
from hashlib import sha256
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .config import SimulationConfig
from .runner import RunReservation, RunResult, SimulationRunError, run_simulation
from .comparison_models import (
    EffectiveParameters, InvocationRecord, MemberDps, MemberIntegrity,
    PlannedParameters, RunArtifactReference, SimulationCraftIdentity,
    StructuredError, StructuredWarning,
)


@dataclass(frozen=True, slots=True)
class AdapterMemberRequest:
    planned_run_id: str
    arm: str
    candidate_item_id: int
    seed: int
    iterations: int
    threads: int
    scenario_sha256: str
    base_profile_sha256: str
    effective_profile_sha256: str
    expected_simc_version: str
    expected_simc_revision: str


@dataclass(frozen=True, slots=True)
class AdapterMemberOutcome:
    run_id: str
    valid: bool
    mean_dps: float | None
    metadata: dict[str, object] | None
    summary: dict[str, object] | None
    invalid_reasons: tuple[str, ...]
    invocation: dict[str, object] | None


RunnerBoundary = Callable[..., RunResult]
ALLOWED_EXECUTABLE_SOURCES = frozenset({"explicit", "environment", "local_config", "test"})
REQUIRED_ARTIFACT_KINDS = frozenset({"metadata", "simc_json", "stdout", "stderr", "summary", "effective_profile"})


def validate_simc_identity(expected: SimulationCraftIdentity, observed: SimulationCraftIdentity | None, executable_source: str | None) -> tuple[StructuredError, ...]:
    errors: list[StructuredError] = []
    if observed is None:
        errors.append(StructuredError("simc_identity_missing", "SimulationCraft identity is absent", "identity"))
    else:
        for field_name in ("version", "revision", "executable_sha256"):
            expected_value, observed_value = getattr(expected, field_name), getattr(observed, field_name)
            if observed_value is None:
                errors.append(StructuredError(f"simc_{field_name}_missing", f"SimulationCraft {field_name} is absent", "identity"))
            elif observed_value != expected_value:
                errors.append(StructuredError(f"simc_{field_name}_mismatch", f"SimulationCraft {field_name} differs", "identity"))
    if executable_source not in ALLOWED_EXECUTABLE_SOURCES:
        errors.append(StructuredError("executable_source_invalid", "Executable source is not allowed", "identity"))
    return tuple(errors)


def validate_artifact_references(run_directory: Path, references: tuple[RunArtifactReference, ...]) -> tuple[StructuredError, ...]:
    errors: list[StructuredError] = []
    seen: set[str] = set()
    root = run_directory.resolve()
    for reference in references:
        if reference.kind in seen:
            errors.append(StructuredError("artifact_reference_duplicate", reference.kind, "artifacts"))
        seen.add(reference.kind)
        if reference.kind not in REQUIRED_ARTIFACT_KINDS:
            errors.append(StructuredError("artifact_kind_invalid", reference.kind, "artifacts"))
        path = Path(reference.path)
        if path.is_absolute() or ":" in reference.path:
            errors.append(StructuredError("artifact_path_not_portable", reference.path, "artifacts"))
            continue
        resolved = (root / path).resolve()
        if resolved.parent != root:
            errors.append(StructuredError("artifact_path_outside_run", reference.path, "artifacts"))
            continue
        exists = resolved.is_file()
        if exists != reference.exists:
            errors.append(StructuredError("artifact_existence_mismatch", reference.kind, "artifacts"))
        if reference.sha256 is not None and not __import__("re").fullmatch(r"[0-9a-f]{64}", reference.sha256):
            errors.append(StructuredError("artifact_hash_format_invalid", reference.kind, "artifacts"))
        actual = sha256(resolved.read_bytes()).hexdigest() if exists else None
        if actual != reference.sha256:
            errors.append(StructuredError("artifact_hash_mismatch", reference.kind, "artifacts"))
    for missing in REQUIRED_ARTIFACT_KINDS - seen:
        errors.append(StructuredError("artifact_reference_missing", missing, "artifacts"))
    return tuple(errors)


@dataclass(frozen=True, slots=True)
class ComparisonMemberExecutionRequest:
    comparison_id: str
    comparison_execution_id: str
    comparison_spec_sha256: str
    block_index: int
    attempt: int
    arm: str
    order_position: int
    candidate_item_id: int
    reservation: RunReservation
    base_profile: Path
    effective_profile: Path
    scenario_sha256: str
    evidence_manifest_sha256: str
    source_identity: str
    planned_parameters: PlannedParameters
    expected_simc: SimulationCraftIdentity
    base_profile_sha256: str
    effective_profile_sha256: str


@dataclass(frozen=True, slots=True)
class ComparisonMemberExecutionResponse:
    run_id: str
    status: str
    process_started: bool
    invocation: InvocationRecord
    metadata: RunArtifactReference
    summary: RunArtifactReference
    artifacts: tuple[RunArtifactReference, ...]
    effective_parameters: EffectiveParameters | None
    observed_simc: SimulationCraftIdentity | None
    exit_code: int | None
    dps: MemberDps | None
    integrity: MemberIntegrity
    errors: tuple[StructuredError, ...]
    warnings: tuple[StructuredWarning, ...]


def execute_comparison_member(
    request: ComparisonMemberExecutionRequest,
    config: SimulationConfig,
    *,
    root: Path,
    runner: RunnerBoundary = run_simulation,
) -> ComparisonMemberExecutionResponse:
    """Final typed adapter contract. It never decides pair or global state."""
    legacy = AdapterMemberRequest(
        request.reservation.run_id, request.arm, request.candidate_item_id,
        request.planned_parameters.seed, request.planned_parameters.iterations,
        request.planned_parameters.threads, request.scenario_sha256,
        request.base_profile_sha256, request.effective_profile_sha256,
        request.expected_simc.version or "", request.expected_simc.revision or "",
    )
    outcome = execute_member(legacy, request.reservation, request.base_profile, request.effective_profile, config, root=root, runner=runner)
    run_dir = request.reservation.run_directory
    artifacts = tuple(_artifact_reference(run_dir / name, root, kind, valid_json=kind in {"metadata", "simc_json", "summary"}) for name, kind in (
        ("metadata.json", "metadata"), ("simc.json", "simc_json"),
        ("stdout.txt", "stdout"), ("stderr.txt", "stderr"),
        ("run_summary.json", "summary"), ("effective_profile.simc", "effective_profile"),
    ))
    metadata_ref = next(item for item in artifacts if item.kind == "metadata")
    summary_ref = next(item for item in artifacts if item.kind == "summary")
    raw_invocation = outcome.invocation
    invocation = InvocationRecord(
        status="completed" if outcome.valid else ("failed_after_start" if request.reservation.consumed else "failed_before_start"),
        portable_argv=tuple(raw_invocation.get("portable_argv", ())) if raw_invocation else None,
        portable_argv_sha256=raw_invocation.get("portable_argv_sha256") if raw_invocation else None,
        process_argv_sha256=raw_invocation.get("process_argv_sha256") if raw_invocation else None,
        executable_sha256=raw_invocation.get("executable_sha256") if raw_invocation else None,
        executable_source=raw_invocation.get("executable_source") if raw_invocation else None,
        argument_list=raw_invocation.get("argument_list") if raw_invocation else None,
        shell=raw_invocation.get("shell") if raw_invocation else None,
    )
    metadata = outcome.metadata or {}
    effective = metadata.get("effective_parameters")
    effective_parameters = EffectiveParameters(effective.get("seed"), effective.get("iterations"), effective.get("threads"), effective.get("target_error"), effective.get("timeout_seconds")) if isinstance(effective, dict) else None
    observed = SimulationCraftIdentity(metadata.get("simc_version"), metadata.get("simc_revision"), invocation.executable_sha256) if metadata else None
    identity_errors = validate_simc_identity(request.expected_simc, observed, invocation.executable_source)
    artifact_errors = validate_artifact_references(run_dir, tuple(RunArtifactReference(item.kind, Path(item.path).name, item.sha256, item.exists, item.valid) for item in artifacts))
    integrity = MemberIntegrity(
        outcome.run_id == request.reservation.run_id,
        request.reservation.consumed,
        effective_parameters == EffectiveParameters(request.planned_parameters.seed, 5000, 2, None, request.planned_parameters.timeout_seconds),
        sha256(request.effective_profile.read_bytes()).hexdigest() == request.effective_profile_sha256,
        config.scenario is not None and config.scenario.source_sha256 == request.scenario_sha256,
        True,
        not identity_errors,
        not artifact_errors and all(item.valid is not False for item in artifacts),
        outcome.mean_dps is not None and math.isfinite(outcome.mean_dps) and outcome.mean_dps > 0,
    )
    errors = tuple(StructuredError(code, code, "member_validation") for code in outcome.invalid_reasons) + identity_errors + artifact_errors
    if not integrity.valid and not errors:
        errors = (StructuredError("member_integrity_failed", "Member integrity verification failed", "member_validation"),)
    return ComparisonMemberExecutionResponse(outcome.run_id, "completed" if outcome.valid and integrity.valid else "invalid", request.reservation.consumed, invocation, metadata_ref, summary_ref, artifacts, effective_parameters, observed, metadata.get("exit_code") if metadata else None, MemberDps(outcome.mean_dps) if outcome.mean_dps is not None else None, integrity, errors, ())


def _artifact_reference(path: Path, root: Path, kind: str, *, valid_json: bool) -> RunArtifactReference:
    exists = path.is_file()
    digest = sha256(path.read_bytes()).hexdigest() if exists else None
    valid: bool | None = None
    if valid_json:
        try:
            valid = isinstance(json.loads(path.read_text(encoding="utf-8")), dict) if exists else False
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            valid = False
    try:
        rendered = path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        rendered = path.name
    return RunArtifactReference(kind, rendered, digest, exists, valid)


def execute_member(
    request: AdapterMemberRequest,
    reservation: RunReservation,
    base_profile: Path,
    profile: Path,
    config: SimulationConfig,
    *,
    root: Path,
    runner: RunnerBoundary = run_simulation,
) -> AdapterMemberOutcome:
    """Execute one planned member through an injected runner boundary."""
    reasons: list[str] = []
    if reservation.run_id != request.planned_run_id:
        reasons.append("reserved_run_id_mismatch")
    if request.seed <= 0 or request.seed > 0x7FFFFFFF:
        reasons.append("seed_out_of_range")
    if (request.iterations, request.threads) != (5000, 2) or config.target_error is not None:
        reasons.append("effective_precision_mismatch")
    if (config.seed, config.iterations, config.threads) != (request.seed, 5000, 2):
        reasons.append("effective_parameters_mismatch")
    expected_item = 50228 if request.arm == "a" else 249368 if request.arm == "b" else None
    if request.candidate_item_id != expected_item:
        reasons.append("candidate_mismatch")
    if not base_profile.is_file() or sha256(base_profile.read_bytes()).hexdigest() != request.base_profile_sha256:
        reasons.append("base_profile_hash_mismatch")
    if not profile.is_file() or sha256(profile.read_bytes()).hexdigest() != request.effective_profile_sha256:
        reasons.append("effective_profile_hash_mismatch")
    scenario = config.scenario
    if scenario is None or scenario.source_sha256 != request.scenario_sha256 or not scenario.source_file.is_file() or sha256(scenario.source_file.read_bytes()).hexdigest() != request.scenario_sha256:
        reasons.append("scenario_hash_mismatch")
    if reasons:
        return AdapterMemberOutcome(reservation.run_id, False, None, None, None, tuple(reasons), None)
    result: RunResult | None = None
    caught: SimulationRunError | None = None
    try:
        result = runner(profile, config, root=root, reservation=reservation)
        run_dir = result.artifacts.run_dir
    except SimulationRunError as exc:
        caught = exc
        run_dir = exc.run_dir
    metadata = _read_json(run_dir / "metadata.json") if run_dir else None
    summary = _read_json(run_dir / "run_summary.json") if run_dir else None
    invocation = metadata.get("invocation") if isinstance(metadata, dict) and isinstance(metadata.get("invocation"), dict) else None
    if caught is not None:
        reasons.append(type(caught).__name__)
    actual_run_id = result.run_id if result is not None else (metadata.get("run_id") if isinstance(metadata, dict) else reservation.run_id)
    if actual_run_id != request.planned_run_id:
        reasons.append("actual_run_id_mismatch")
    if not isinstance(metadata, dict):
        reasons.append("metadata_missing_or_invalid")
    else:
        effective = metadata.get("effective_parameters")
        if not isinstance(effective, dict) or (effective.get("iterations"), effective.get("threads"), effective.get("target_error"), effective.get("seed")) != (5000, 2, None, request.seed):
            reasons.append("metadata_parameters_mismatch")
        if metadata.get("simc_version") != request.expected_simc_version:
            reasons.append("simc_version_mismatch")
        if metadata.get("simc_revision") != request.expected_simc_revision:
            reasons.append("simc_revision_mismatch")
        if metadata.get("run_id") != request.planned_run_id:
            reasons.append("metadata_run_id_mismatch")
    mean_dps = _summary_dps(summary)
    if mean_dps is None or not math.isfinite(mean_dps) or mean_dps <= 0:
        reasons.append("dps_invalid")
    return AdapterMemberOutcome(str(actual_run_id), not reasons, mean_dps, metadata, summary, tuple(reasons), invocation)


def _read_json(path: Path) -> dict[str, object] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _summary_dps(summary: dict[str, object] | None) -> float | None:
    if not isinstance(summary, dict):
        return None
    dps = summary.get("dps")
    if isinstance(dps, dict) and isinstance(dps.get("mean"), (int, float)) and not isinstance(dps.get("mean"), bool):
        return float(dps["mean"])
    return None
