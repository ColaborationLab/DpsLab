"""Run two to four real Balance loadouts and write the best bounded result."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .addon_live_analysis_transport import parse_live_analysis_export
from .balance_stat_weights import BalanceStatWeights, load_balance_stat_weights
from .druid_balance_profiles import build_druid_balance_profiles
from .druid_restoration_recommendation import (
    DruidRestorationRecommendation,
    DruidRestorationRecommendationError,
    _mean,
    write_addon_recommendation,
)
from .config import SimulationConfig
from .result_parser import summarize_run
from .runner import run_simulation

DruidBalanceRecommendation = DruidRestorationRecommendation
DruidBalanceRecommendationError = DruidRestorationRecommendationError


@dataclass(frozen=True, repr=False)
class DruidBalanceComparison:
    message: str
    loadouts: tuple[tuple[int, float], ...]
    preferred_loadout: int
    stat_weights: BalanceStatWeights | None = None


def _recommendation(results: tuple[tuple[int, float], ...], names: dict[int, str] | None = None) -> DruidBalanceComparison:
    names = names or {}
    label = lambda identifier: names.get(identifier, f"la build importada {-identifier}" if identifier < 0 else f"el loadout {identifier}")
    reference_id, reference_dps = results[0]
    if len(results) == 1:
        return DruidBalanceComparison(f"Simulación individual de {label(reference_id)}: {reference_dps:.0f} DPS.", results, reference_id)
    preferred_id, preferred_dps = max(results, key=lambda item: item[1])
    if preferred_dps <= reference_dps:
        message = f"{label(reference_id)} sigue primero: {reference_dps:.0f} DPS."
    else:
        percent = (preferred_dps - reference_dps) / reference_dps * 100
        message = f"Usa {label(preferred_id)}: {preferred_dps:.0f} DPS frente a {reference_dps:.0f} DPS ({percent:.1f}% mejor)."
    return DruidBalanceComparison(message, results, preferred_id)


def run_druid_balance_recommendation(
    export_text: str,
    simc_exe: Path,
    addon_directory: Path,
    *,
    root: Path,
    selected_config_ids: tuple[int, ...] | None = None,
    imported_talent_strings: tuple[str, ...] = (),
    runner: Callable = run_simulation,
    summary_loader: Callable = summarize_run,
) -> DruidBalanceComparison:
    snapshot = parse_live_analysis_export(export_text)
    profiles = build_druid_balance_profiles(snapshot, selected_config_ids, imported_talent_strings)
    executable = simc_exe.resolve()
    if not executable.is_file():
        raise DruidBalanceRecommendationError("balance_simc_unavailable")
    import tempfile
    with tempfile.TemporaryDirectory(prefix="dpslab-balance-") as workspace:
        directory = Path(workspace)
        config = SimulationConfig(simc_exe=executable, runs_dir=directory / "runs", threads=4, iterations=1000, max_time=300, fight_style="Patchwerk", generate_html=False, calculate_scale_factors=True)
        results = []
        weights_by_loadout = {}
        for loadout in profiles.loadouts:
            profile = directory / f"loadout-{loadout.config_id}.simc"
            profile.write_text(loadout.profile, encoding="utf-8")
            run = runner(profile, config, root=root)
            results.append((loadout.config_id, _mean(summary_loader(run.artifacts.run_dir, root=root))))
            weights_by_loadout[loadout.config_id] = load_balance_stat_weights(run.artifacts.run_dir)
        comparison = _recommendation(tuple(results), {loadout.config_id: loadout.name for loadout in profiles.loadouts})
        comparison = DruidBalanceComparison(comparison.message, comparison.loadouts, comparison.preferred_loadout, weights_by_loadout.get(comparison.preferred_loadout))
    advisor_weights = comparison.stat_weights.values if comparison.stat_weights is not None else ()
    write_addon_recommendation(addon_directory, DruidRestorationRecommendation(comparison.message, results[0][1], max(results, key=lambda item: item[1])[1], "comparison"), advisor_weights)
    return comparison
