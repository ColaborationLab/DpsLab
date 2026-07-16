"""Dataclasses del resumen portable de una ejecución de SimulationCraft."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class RunIdentification:
    run_id: str | None
    simc_version: str | None
    json_report_version: str | None
    character: str
    character_class: str | None
    specialization: str | None
    level: int | None


@dataclass(frozen=True, slots=True)
class RunScenario:
    scenario_id: str | None
    scenario_name: str | None
    scenario_file: str | None
    scenario_sha256: str | None
    scenario_hash_verified: bool | None
    profile: str | None
    threads: int | None
    iteration_mode: str | None
    iterations_parameter: int | None
    iterations_requested: int | None
    iterations_completed: int | None
    dps_sample_count: int | None
    max_time: float | None
    vary_combat_length: float | None
    fight_style: str | None
    desired_targets: int | None
    target_error_percent: float | None
    effective_parameters: dict[str, Any] | None


@dataclass(frozen=True, slots=True)
class DpsResult:
    mean: float | None
    median: float | None
    min: float | None
    max: float | None
    standard_deviation: float | None
    mean_error: float | None
    observed_relative_error_percent: float | None
    simc_displayed_error: SimcDisplayedError | None


@dataclass(frozen=True, slots=True)
class SimcDisplayedError:
    absolute_value: float | None
    value_percent: float
    source: str
    locator: str
    semantic_role: str


@dataclass(frozen=True, slots=True)
class RunVariant:
    variant_id: str | None
    variant_name: str | None
    variant_file: str | None
    variant_sha256: str | None
    variant_hash_verified: bool | None
    base_profile: str | None
    base_simc_checksum: str | None
    base_profile_sha256: str | None
    effective_profile: str | None
    effective_profile_sha256: str | None
    overrides: list[dict[str, Any]] | None


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    simulation_status: str | None
    duration_seconds: float | None
    simc_elapsed_seconds: float | None
    total_simulated_combat_seconds: float | None
    exit_code: int | None


@dataclass(frozen=True, slots=True)
class RunDiagnostics:
    warnings: list[str]
    stderr_nonempty: bool
    requested_iterations_differ_from_sample_count: bool | None
    completed_iterations_differ_from_dps_sample_count: bool | None
    profile_hash_verified: bool | None


@dataclass(frozen=True, slots=True)
class SummaryGeneration:
    status: str
    error: str | None


@dataclass(frozen=True, slots=True)
class RunSummary:
    schema_version: str
    identification: RunIdentification
    scenario: RunScenario
    variant: RunVariant
    dps: DpsResult
    execution: ExecutionResult
    diagnostics: RunDiagnostics
    summary_generation: SummaryGeneration

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
