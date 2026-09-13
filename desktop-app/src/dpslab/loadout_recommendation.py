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
from .balance_stat_weights import load_balance_stat_weights
from .item_score_profiles import CharacterScoreProfile, ScoreWeights, effective_weights


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
    score_weights: tuple[ScoreWeights, ...] = ()


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


def _item_scores_document(character: CharacterScoreProfile, selected: tuple[tuple[int, int], ...]) -> str:
    profiles = []
    for specialization_id, build_id in selected:
        build_name = next((build.name for spec_id, builds in character.specs if spec_id == specialization_id for build in builds if build.build_id == build_id), None)
        if build_id < 1 or build_name is None:
            continue
        weight = effective_weights(character, specialization_id, build_id)
        if weight is None:
            continue
        values = ", ".join(f"{name} = {value:g}" for name, value in weight.values)
        profiles.append("{ id = " + json.dumps(f"{specialization_id}:{build_id}") + ", name = " + json.dumps(f"Spec {specialization_id} — {build_name}", ensure_ascii=False) + ", source = " + json.dumps(weight.source) + ", weights = { " + values + " } }")
    return "DpsLabRealRecommendation = {\n  schema_version = \"0.4\",\n  state = \"ready\",\n  message = \"Scores de equipo actualizados en DpsLab.\",\n  character_id = " + json.dumps(character.character_id) + ",\n  item_scores = { profiles = { " + ", ".join(profiles) + " } },\n}\n"


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


def write_item_score_profiles(addon_directory: Path, character: CharacterScoreProfile, selected: tuple[tuple[int, int], ...]) -> Path:
    """Transfer selected local weights to the addon; it does not invoke SimC."""
    directory = addon_directory.resolve()
    if not (directory / "DpsLab.toc").is_file() or not (directory / "DpsLab.lua").is_file():
        raise LoadoutRecommendationError("loadout_addon_unavailable")
    destination = directory / "DpsLabRealRecommendation.lua"
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=directory, prefix=".dpslab-scores-", suffix=".tmp", delete=False) as temporary:
            temporary_name = temporary.name; temporary.write(_item_scores_document(character, selected)); temporary.flush(); os.fsync(temporary.fileno())
        os.replace(temporary_name, destination); temporary_name = None
    except OSError as exc:
        raise LoadoutRecommendationError("loadout_addon_write_failed") from exc
    finally:
        if temporary_name is not None: Path(temporary_name).unlink(missing_ok=True)
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
        config = SimulationConfig(simc_exe=executable, runs_dir=directory / "runs", threads=4, iterations=1000, max_time=300, fight_style="Patchwerk", generate_html=False, calculate_scale_factors=True)
        results = []
        weights = []
        for loadout in profiles.loadouts:
            profile = directory / f"loadout-{loadout.config_id}.simc"
            profile.write_text(loadout.profile, encoding="utf-8")
            run = runner(profile, config, root=root)
            value = _mean(summary_loader(run.artifacts.run_dir, root=root))
            if not math.isfinite(value) or value <= 0:
                raise LoadoutRecommendationError("loadout_result_unavailable")
            results.append((loadout.config_id, value))
            parsed = load_balance_stat_weights(run.artifacts.run_dir)
            version = getattr(run, "simc_version", None)
            if parsed is not None and isinstance(version, str) and version.strip():
                weights.append(ScoreWeights("personalized", profiles.capability.class_id, profiles.capability.specialization_id, loadout.config_id, parsed.values, version.strip(), "Patchwerk", __import__("hashlib").sha256(loadout.profile.encode("utf-8")).hexdigest()))
        base = _comparison(profiles, tuple(results))
        comparison = LoadoutComparison(base.message, base.loadouts, base.preferred_loadout, base.class_id, base.specialization_id, base.role, base.metric, tuple(weights))
    write_loadout_recommendation(addon_directory, comparison)
    return comparison
