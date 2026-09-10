"""One real, ephemeral Restoration comparison and its minimal addon result."""

from __future__ import annotations

import json
import math
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .addon_live_analysis_transport import parse_live_analysis_export
from .config import SimulationConfig
from .druid_restoration_profiles import build_druid_restoration_profiles
from .result_models import RunSummary
from .result_parser import summarize_run
from .runner import RunResult, run_simulation


class DruidRestorationRecommendationError(ValueError):
    """The real comparison could not safely produce a player message."""


@dataclass(frozen=True, repr=False)
class DruidRestorationRecommendation:
    message: str
    active_dps: float
    comparison_dps: float
    preferred_loadout: str


def _mean(summary: RunSummary) -> float:
    value = summary.dps.mean
    if (
        summary.execution.simulation_status != "completed"
        or summary.diagnostics.profile_hash_verified is False
        or isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value <= 0
    ):
        raise DruidRestorationRecommendationError("restoration_result_unavailable")
    return float(value)


def compare_druid_restoration_runs(active: RunSummary, comparison: RunSummary) -> DruidRestorationRecommendation:
    """Prefer the higher real simulated DPS; ties deliberately make no claim."""
    active_dps, comparison_dps = _mean(active), _mean(comparison)
    difference = comparison_dps - active_dps
    if difference == 0:
        raise DruidRestorationRecommendationError("restoration_result_tied")
    if difference > 0:
        preferred, selected, other = "comparison", comparison_dps, active_dps
        label = "el segundo loadout guardado"
    else:
        preferred, selected, other = "active", active_dps, comparison_dps
        label = "el loadout activo"
    percent = abs(selected - other) / other * 100
    return DruidRestorationRecommendation(
        f"Usa {label}: {selected:.0f} DPS frente a {other:.0f} DPS ({percent:.1f}% mejor).",
        active_dps,
        comparison_dps,
        preferred,
    )


def _addon_document(recommendation: DruidRestorationRecommendation, advisor_weights: tuple[tuple[str, float], ...] = ()) -> str:
    message = recommendation.message
    if not isinstance(message, str) or not 1 <= len(message) <= 240:
        raise DruidRestorationRecommendationError("restoration_result_invalid")
    advisor = ""
    if advisor_weights:
        if not all(isinstance(name, str) and name in {"Intellect", "Agility", "CritRating", "HasteRating", "MasteryRating", "VersatilityRating"} and isinstance(value, float) and math.isfinite(value) and value > 0 for name, value in advisor_weights):
            raise DruidRestorationRecommendationError("restoration_result_invalid")
        advisor = "  advisor = { role = \"damage\", specialization_id = 102, weights = { " + ", ".join(f"{name} = {value:.9g}" for name, value in advisor_weights) + " } },\n"
    schema_version = "0.2" if advisor else "0.1"
    return (
        "DpsLabRealRecommendation = {\n"
        + f'  schema_version = "{schema_version}",\n'
        + '  state = "ready",\n'
        + f"  message = {json.dumps(message, ensure_ascii=True)},\n"
        + advisor + "}\n"
    )


def write_addon_recommendation(addon_directory: Path, recommendation: DruidRestorationRecommendation, advisor_weights: tuple[tuple[str, float], ...] = ()) -> Path:
    """Replace only the dedicated data file in a user-selected installed addon."""
    directory = addon_directory.resolve()
    if not (directory / "DpsLab.toc").is_file() or not (directory / "DpsLab.lua").is_file():
        raise DruidRestorationRecommendationError("restoration_addon_unavailable")
    destination = directory / "DpsLabRealRecommendation.lua"
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=directory, prefix=".dpslab-result-", suffix=".tmp", delete=False) as temporary:
            temporary_name = temporary.name
            temporary.write(_addon_document(recommendation, advisor_weights))
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_name, destination)
        temporary_name = None
    except OSError as exc:
        raise DruidRestorationRecommendationError("restoration_addon_write_failed") from exc
    finally:
        if temporary_name is not None:
            Path(temporary_name).unlink(missing_ok=True)
    return destination


Runner = Callable[[Path, SimulationConfig], RunResult]
SummaryLoader = Callable[[Path], RunSummary]


def run_druid_recommendation(
    export_text: str,
    simc_exe: Path,
    addon_directory: Path,
    *,
    root: Path,
    profile_builder: Callable[[object], object],
    runner: Runner = run_simulation,
    summary_loader: SummaryLoader = summarize_run,
) -> DruidRestorationRecommendation:
    """Run two real pasted-loadout profiles without retaining their artifacts."""
    snapshot = parse_live_analysis_export(export_text)
    profiles = profile_builder(snapshot)
    executable = simc_exe.resolve()
    if not executable.is_file():
        raise DruidRestorationRecommendationError("restoration_simc_unavailable")
    with tempfile.TemporaryDirectory(prefix="dpslab-restoration-") as workspace:
        directory = Path(workspace)
        active_profile = directory / "active.simc"
        comparison_profile = directory / "comparison.simc"
        active_profile.write_text(profiles.active_profile, encoding="utf-8")
        comparison_profile.write_text(profiles.comparison_profile, encoding="utf-8")
        config = SimulationConfig(
            simc_exe=executable,
            runs_dir=directory / "runs",
            threads=4,
            iterations=1000,
            max_time=300,
            fight_style="Patchwerk",
            generate_html=False,
        )
        active_run = runner(active_profile, config, root=root)
        comparison_run = runner(comparison_profile, config, root=root)
        active_summary = summary_loader(active_run.artifacts.run_dir, root=root)
        comparison_summary = summary_loader(comparison_run.artifacts.run_dir, root=root)
        recommendation = compare_druid_restoration_runs(active_summary, comparison_summary)
    write_addon_recommendation(addon_directory, recommendation)
    return recommendation


def run_druid_restoration_recommendation(
    export_text: str,
    simc_exe: Path,
    addon_directory: Path,
    *,
    root: Path,
    runner: Runner = run_simulation,
    summary_loader: SummaryLoader = summarize_run,
) -> DruidRestorationRecommendation:
    return run_druid_recommendation(
        export_text, simc_exe, addon_directory, root=root,
        profile_builder=build_druid_restoration_profiles,
        runner=runner, summary_loader=summary_loader,
    )
