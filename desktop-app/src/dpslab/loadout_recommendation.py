"""Run a homogeneous, player-selected class/spec DPS loadout comparison."""
from __future__ import annotations

from dataclasses import dataclass
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Callable

from .addon_live_analysis_transport import parse_live_analysis_export
from .config import SimulationConfig
from .druid_restoration_recommendation import _mean
from .loadout_profiles import LoadoutProfileError, build_loadout_profiles
from .result_parser import summarize_run
from .runner import run_simulation


class LoadoutRecommendationError(ValueError):
    pass


@dataclass(frozen=True, repr=False)
class LoadoutComparison:
    message: str
    loadouts: tuple[tuple[int, float], ...]
    preferred_loadout: int
    class_id: int
    specialization_id: int
    role: str
    metric: str = "DPS"


def _comparison(profiles, results: tuple[tuple[int, float], ...]) -> LoadoutComparison:
    reference_id, reference = results[0]
    names = {item.config_id: item.name for item in profiles.loadouts}
    label = lambda identifier: names[identifier]
    preferred_id, preferred = max(results, key=lambda value: value[1])
    if len(results) == 1:
        message = f"Simulación individual de {label(reference_id)}: {reference:.0f} DPS."
    elif preferred_id == reference_id:
        message = f"{label(reference_id)} sigue primero: {reference:.0f} DPS."
    else:
        message = f"Usa {label(preferred_id)}: {preferred:.0f} DPS frente a {reference:.0f} DPS ({(preferred - reference) / reference * 100:.1f}% mejor)."
    capability = profiles.capability
    return LoadoutComparison(message, results, preferred_id, capability.class_id, capability.specialization_id, capability.role)


def _addon_document(comparison: LoadoutComparison) -> str:
    if not isinstance(comparison.message, str) or not 1 <= len(comparison.message) <= 240:
        raise LoadoutRecommendationError("loadout_result_invalid")
    if not all(isinstance(value, int) and not isinstance(value, bool) and value > 0 for value in (comparison.class_id, comparison.specialization_id)) or comparison.role not in {"damage", "tank", "healer"}:
        raise LoadoutRecommendationError("loadout_result_invalid")
    return (
        "DpsLabRealRecommendation = {\n  schema_version = \"0.3\",\n"
        "  state = \"ready\",\n  message = " + json.dumps(comparison.message, ensure_ascii=False)
        + ",\n  context = { class_id = " + str(comparison.class_id)
        + ", specialization_id = " + str(comparison.specialization_id)
        + ", role = " + json.dumps(comparison.role)
        + ", metric = " + json.dumps(comparison.metric) + " },\n}\n"
    )


def write_loadout_recommendation(addon_directory: Path, comparison: LoadoutComparison) -> Path:
    directory = addon_directory.resolve()
    if not (directory / "DpsLab.toc").is_file() or not (directory / "DpsLab.lua").is_file():
        raise LoadoutRecommendationError("loadout_addon_unavailable")
    destination = directory / "DpsLabRealRecommendation.lua"
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=directory, prefix=".dpslab-result-", suffix=".tmp", delete=False) as temporary:
            temporary_name = temporary.name
            temporary.write(_addon_document(comparison))
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_name, destination)
        temporary_name = None
    except OSError as exc:
        raise LoadoutRecommendationError("loadout_addon_write_failed") from exc
    finally:
        if temporary_name is not None:
            Path(temporary_name).unlink(missing_ok=True)
    return destination


def run_loadout_recommendation(export_text: str, simc_exe: Path, addon_directory: Path, *, root: Path, selected_config_ids: tuple[int, ...] | None = None, imported_loadouts: tuple[tuple[str, str], ...] = (), runner: Callable = run_simulation, summary_loader: Callable = summarize_run) -> LoadoutComparison:
    try:
        profiles = build_loadout_profiles(parse_live_analysis_export(export_text), selected_config_ids, imported_loadouts)
    except (LoadoutProfileError, ValueError) as exc:
        raise LoadoutRecommendationError(str(exc)) from exc
    executable = simc_exe.resolve()
    if not executable.is_file():
        raise LoadoutRecommendationError("loadout_simc_unavailable")
    with tempfile.TemporaryDirectory(prefix="dpslab-loadout-") as workspace:
        directory = Path(workspace)
        config = SimulationConfig(simc_exe=executable, runs_dir=directory / "runs", threads=4, iterations=1000, max_time=300, fight_style="Patchwerk", generate_html=False)
        results = []
        for loadout in profiles.loadouts:
            profile = directory / f"loadout-{loadout.config_id}.simc"
            profile.write_text(loadout.profile, encoding="utf-8")
            value = _mean(summary_loader(runner(profile, config, root=root).artifacts.run_dir, root=root))
            if not math.isfinite(value) or value <= 0:
                raise LoadoutRecommendationError("loadout_result_unavailable")
            results.append((loadout.config_id, value))
        comparison = _comparison(profiles, tuple(results))
    write_loadout_recommendation(addon_directory, comparison)
    return comparison
