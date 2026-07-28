"""Composable, fail-closed readiness boundary for one frozen comparison."""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Callable

from .comparison_models import ComparisonSoftware, SimulationCraftIdentity
from .comparison_preflight import (
    ComparisonExecutionPreflight,
    preflight_comparison_execution,
)
from .comparison_spec import ComparisonSpec
from .config import SimulationConfig
from .simc_identity import (
    SimulationCraftIdentityProbe,
    capture_simulationcraft_identity,
)


class ComparisonReadinessError(RuntimeError):
    """Readiness could not be established without crossing a forbidden boundary."""


IdentityProbe = Callable[..., SimulationCraftIdentityProbe]
PreflightBoundary = Callable[..., ComparisonExecutionPreflight]


@dataclass(frozen=True, slots=True)
class ComparisonReadiness:
    preflight: ComparisonExecutionPreflight
    simulationcraft_branch: str
    executable_source: str
    portable_probe_argv: tuple[str, ...]
    ready: bool = True


_PORTABLE_PROBE_ARGV = ("<SIMC_EXE>", "display_build=2")
_VERSION_PATTERN = re.compile(r"[0-9]{4}-[0-9]{2}")
_REVISION_PATTERN = re.compile(r"[0-9a-f]{7,40}")
_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
_BRANCH_PATTERN = re.compile(r"[A-Za-z0-9._/-]{1,64}")


def _require_probe(
    probe: SimulationCraftIdentityProbe,
    config: SimulationConfig,
) -> None:
    if not isinstance(probe, SimulationCraftIdentityProbe):
        raise ComparisonReadinessError("identity_probe_contract_invalid")
    identity = probe.identity
    if (
        not isinstance(identity, SimulationCraftIdentity)
        or not isinstance(probe.branch, str)
        or not isinstance(probe.executable_source, str)
        or not isinstance(probe.portable_argv, tuple)
        or not all(
            isinstance(value, str) for value in probe.portable_argv
        )
        or probe.isolated is not True
        or probe.portable_argv != _PORTABLE_PROBE_ARGV
        or probe.executable_source != config.executable_source
        or _BRANCH_PATTERN.fullmatch(probe.branch) is None
        or not isinstance(identity.version, str)
        or _VERSION_PATTERN.fullmatch(identity.version) is None
        or not isinstance(identity.revision, str)
        or _REVISION_PATTERN.fullmatch(identity.revision) is None
        or not isinstance(identity.executable_sha256, str)
        or _SHA256_PATTERN.fullmatch(identity.executable_sha256) is None
    ):
        raise ComparisonReadinessError("identity_probe_contract_invalid")


def _require_preflight(
    report: ComparisonExecutionPreflight,
    spec: ComparisonSpec,
    probe: SimulationCraftIdentityProbe,
    software: ComparisonSoftware,
) -> None:
    if not isinstance(report, ComparisonExecutionPreflight):
        raise ComparisonReadinessError(
            "comparison_preflight_contract_invalid"
        )
    if (
        report.ready is not True
        or report.comparison_id != spec.comparison_id
        or report.comparison_spec_sha256 != spec.source_sha256
        or report.base_profile_sha256 != spec.base_profile_sha256
        or report.scenario_sha256 != spec.scenario_sha256
        or report.evidence_manifest_sha256 != spec.evidence_sha256
        or report.software
        != replace(software, simulationcraft=probe.identity)
        or report.runs_dir != "results/runs"
    ):
        raise ComparisonReadinessError("comparison_preflight_contract_invalid")


def assess_comparison_readiness(
    spec: ComparisonSpec,
    config: SimulationConfig,
    software: ComparisonSoftware,
    *,
    root: Path,
    probe_timeout_seconds: float = 30.0,
    identity_probe: IdentityProbe | None = None,
    preflight: PreflightBoundary | None = None,
) -> ComparisonReadiness:
    """Capture identity and validate preflight without reserving or writing a run."""
    identity_boundary = (
        identity_probe
        if identity_probe is not None
        else capture_simulationcraft_identity
    )
    preflight_boundary = (
        preflight if preflight is not None else preflight_comparison_execution
    )

    probe_result: SimulationCraftIdentityProbe | None
    try:
        probe_result = identity_boundary(
            config,
            timeout_seconds=probe_timeout_seconds,
        )
    except Exception:
        probe_result = None
    if probe_result is None:
        raise ComparisonReadinessError("identity_probe_failed")
    _require_probe(probe_result, config)

    preflight_result: ComparisonExecutionPreflight | None
    try:
        preflight_result = preflight_boundary(
            spec,
            config,
            probe_result.identity,
            software,
            root=root,
        )
    except Exception:
        preflight_result = None
    if preflight_result is None:
        raise ComparisonReadinessError("comparison_preflight_failed")
    _require_preflight(preflight_result, spec, probe_result, software)

    return ComparisonReadiness(
        preflight=preflight_result,
        simulationcraft_branch=probe_result.branch,
        executable_source=probe_result.executable_source,
        portable_probe_argv=probe_result.portable_argv,
    )
