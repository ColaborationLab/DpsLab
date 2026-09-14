"""Local character/spec/build score profiles backed only by real SimC output."""
from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import re
import tempfile
from uuid import uuid4

from .addon_live_analysis_transport import PREFIX, LiveAnalysisItem, LiveAnalysisSnapshot, canonical_live_analysis_bytes
from .balance_stat_weights import BalanceStatWeights, load_balance_stat_weights
from .loadout_capabilities import CAPABILITIES


class ItemScoreProfileError(ValueError):
    pass


_STATS = {"Strength", "Intellect", "Agility", "CritRating", "HasteRating", "MasteryRating", "VersatilityRating"}
_TALENT = re.compile(r"[A-Za-z0-9+/=]{1,2048}\Z")
_PROFILE_IMPORT_OFFSET = 2_000_000_000


@dataclass(frozen=True, repr=False)
class ScoreWeights:
    source: str  # personalized/generic originate in SimC; manual is user-edited.
    class_id: int
    specialization_id: int
    build_id: int | None
    values: tuple[tuple[str, float], ...]
    simc_version: str
    scenario: str
    reference_profile_sha256: str


@dataclass(frozen=True, repr=False)
class SimulationRecord:
    build_id: int
    metric: str
    value: float
    simc_version: str | None
    scenario: str
    relative_error_percent: float | None = None
    run_id: str | None = None


@dataclass(frozen=True, repr=False)
class BuildScoreProfile:
    build_id: int
    name: str
    talent_string: str
    weights: tuple[ScoreWeights, ...] = ()
    simulations: tuple[SimulationRecord, ...] = ()


@dataclass(frozen=True, repr=False)
class CharacterScoreProfile:
    character_id: str
    name: str
    realm: str
    class_id: int
    specs: tuple[tuple[int, tuple[BuildScoreProfile, ...]], ...] = ()
    equipped: tuple[LiveAnalysisItem, ...] = ()
    profile_name: str = ""
    level: int = 0
    race_id: int = 0


@dataclass(frozen=True, repr=False)
class ItemScore:
    equipped: float
    candidate: float
    delta: float
    source: str


def _valid_text(value: object, maximum: int = 80) -> bool:
    return isinstance(value, str) and 1 <= len(value.strip()) <= maximum


def _valid_weights(value: ScoreWeights) -> bool:
    return (
        value.source in {"personalized", "generic", "manual"}
        and isinstance(value.class_id, int) and not isinstance(value.class_id, bool) and value.class_id > 0
        and isinstance(value.specialization_id, int) and not isinstance(value.specialization_id, bool) and value.specialization_id > 0
        and (value.build_id is None or isinstance(value.build_id, int) and not isinstance(value.build_id, bool) and value.build_id != 0)
        and _valid_text(value.simc_version, 160) and _valid_text(value.scenario, 160)
        and isinstance(value.reference_profile_sha256, str) and len(value.reference_profile_sha256) == 64
        and len(value.values) > 0 and len({name for name, _ in value.values}) == len(value.values)
        and all(name in _STATS and isinstance(weight, float) and math.isfinite(weight) and weight > 0 for name, weight in value.values)
    )


def weights_from_simc_run(run_dir: Path, *, source: str, class_id: int, specialization_id: int, build_id: int | None, scenario: str, reference_profile: str) -> ScoreWeights | None:
    """Read scale factors from an already completed run; this never invokes SimC."""
    parsed: BalanceStatWeights | None = load_balance_stat_weights(run_dir)
    if parsed is None:
        return None
    try:
        metadata = json.loads((run_dir / "run_metadata.json").read_text(encoding="utf-8"))
        version = metadata.get("simc_version") or metadata.get("simc_revision")
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    value = ScoreWeights(source, class_id, specialization_id, build_id, parsed.values, str(version).strip() if version is not None else "", scenario, sha256(reference_profile.encode("utf-8")).hexdigest())
    return value if _valid_weights(value) else None


def effective_weights(character: CharacterScoreProfile, specialization_id: int, build_id: int) -> ScoreWeights | None:
    """Prefer an exact personal build; generic fallback is always same class/spec."""
    for spec_id, builds in character.specs:
        if spec_id != specialization_id:
            continue
        for build in builds:
            if build.build_id == build_id:
                for weight in build.weights:
                    if weight.source in {"personalized", "manual"} and _valid_weights(weight):
                        return weight
        for build in builds:
            for weight in build.weights:
                if weight.source == "generic" and weight.class_id == character.class_id and weight.specialization_id == specialization_id and weight.build_id in {None, build_id} and _valid_weights(weight):
                    return weight
    return None


def score_replacement(weights: ScoreWeights, equipped: tuple[LiveAnalysisItem, ...], candidates: tuple[LiveAnalysisItem, ...]) -> ItemScore:
    if not _valid_weights(weights) or not candidates or any(not isinstance(item, LiveAnalysisItem) for item in equipped + candidates):
        raise ItemScoreProfileError("item_score_input_invalid")
    factors = dict(weights.values)
    score = lambda items: sum(factors.get(stat, 0.0) * amount for item in items for stat, amount in item.stats)
    candidate_locations = {item.location for item in candidates}
    if len(candidate_locations) != len(candidates):
        raise ItemScoreProfileError("item_score_duplicate_slot")
    baseline = score(tuple(item for item in equipped if item.location in candidate_locations))
    proposed = score(candidates)
    return ItemScore(baseline, proposed, proposed - baseline, weights.source)


def _path(root: Path) -> Path:
    if not root.is_absolute():
        raise ItemScoreProfileError("character_profile_root_invalid")
    return root / "character-score-profiles.json"


def _item(item: LiveAnalysisItem) -> dict[str, object]:
    return {"item_id": item.item_id, "item_level": item.item_level, "item_link": item.item_link, "location": item.location, "slot": item.slot, "source": item.source, "stats": dict(item.stats)}


def _read_item(value: object) -> LiveAnalysisItem:
    if not isinstance(value, dict) or set(value) != {"item_id", "item_level", "item_link", "location", "slot", "source", "stats"} or not isinstance(value["stats"], dict):
        raise ValueError
    return LiveAnalysisItem(value["item_id"], value["item_level"], value["item_link"], value["location"], value["slot"], value["source"], None, tuple(sorted(value["stats"].items())))


def _weight(value: ScoreWeights) -> dict[str, object]:
    return {"source": value.source, "class_id": value.class_id, "specialization_id": value.specialization_id, "build_id": value.build_id, "values": dict(value.values), "simc_version": value.simc_version, "scenario": value.scenario, "reference_profile_sha256": value.reference_profile_sha256}


def _simulation(value: SimulationRecord) -> dict[str, object]:
    return {"build_id": value.build_id, "metric": value.metric, "value": value.value, "simc_version": value.simc_version, "scenario": value.scenario,
            "relative_error_percent": value.relative_error_percent, "run_id": value.run_id}


def _read_simulation(value: object) -> SimulationRecord:
    legacy = {"build_id", "metric", "value", "simc_version", "scenario"}
    current = legacy | {"relative_error_percent", "run_id"}
    if not isinstance(value, dict) or frozenset(value) not in {frozenset(legacy), frozenset(current)}:
        raise ValueError
    error = value.get("relative_error_percent")
    result = SimulationRecord(value["build_id"], value["metric"], float(value["value"]), value["simc_version"], value["scenario"], None if error is None else float(error), value.get("run_id"))
    if not isinstance(result.build_id, int) or isinstance(result.build_id, bool) or result.build_id == 0 or result.metric != "DPS" or not math.isfinite(result.value) or result.value <= 0 or result.simc_version is not None and not _valid_text(result.simc_version, 160) or not _valid_text(result.scenario, 160) or result.relative_error_percent is not None and (not math.isfinite(result.relative_error_percent) or result.relative_error_percent < 0) or result.run_id is not None and not _valid_text(result.run_id, 160):
        raise ValueError
    return result


def _read_weight(value: object) -> ScoreWeights:
    if not isinstance(value, dict) or set(value) != {"source", "class_id", "specialization_id", "build_id", "values", "simc_version", "scenario", "reference_profile_sha256"} or not isinstance(value["values"], dict):
        raise ValueError
    result = ScoreWeights(value["source"], value["class_id"], value["specialization_id"], value["build_id"], tuple(sorted((name, float(weight)) for name, weight in value["values"].items())), value["simc_version"], value["scenario"], value["reference_profile_sha256"])
    if not _valid_weights(result): raise ValueError
    return result


def _document(profiles: tuple[CharacterScoreProfile, ...]) -> dict[str, object]:
    characters = []
    for character in profiles:
        specs = []
        for spec_id, builds in character.specs:
            specs.append({"specialization_id": spec_id, "builds": [
                {"build_id": build.build_id, "name": build.name, "talent_string": build.talent_string,
                 "weights": [_weight(weight) for weight in build.weights], "simulations": [_simulation(value) for value in build.simulations]} for build in builds
            ]})
        characters.append({"character_id": character.character_id, "name": character.name, "realm": character.realm, "profile_name": character.profile_name,
                           "class_id": character.class_id, "level": character.level, "race_id": character.race_id, "equipped": [_item(item) for item in character.equipped], "specs": specs})
    return {"schema_version": "0.5", "characters": characters}


def load_profiles(root: Path) -> tuple[CharacterScoreProfile, ...]:
    path = _path(root)
    if not path.exists(): return ()
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(document, dict) or set(document) != {"schema_version", "characters"} or document["schema_version"] not in {"0.1", "0.2", "0.3", "0.4", "0.5"} or not isinstance(document["characters"], list): raise ValueError
        output = []
        for value in document["characters"]:
            character_fields = {"character_id", "name", "realm", "class_id", "equipped", "specs"}
            if document["schema_version"] in {"0.3", "0.4", "0.5"}: character_fields.add("profile_name")
            if document["schema_version"] in {"0.4", "0.5"}: character_fields |= {"level", "race_id"}
            if not isinstance(value, dict) or set(value) != character_fields or not isinstance(value["specs"], list) or not isinstance(value["equipped"], list): raise ValueError
            specs = []
            for spec in value["specs"]:
                if not isinstance(spec, dict) or set(spec) != {"specialization_id", "builds"} or not isinstance(spec["builds"], list): raise ValueError
                build_fields = {"build_id", "name", "talent_string", "weights"} if document["schema_version"] == "0.1" else {"build_id", "name", "talent_string", "weights", "simulations"}
                builds = tuple(BuildScoreProfile(item["build_id"], item["name"], item["talent_string"], tuple(_read_weight(weight) for weight in item["weights"]), tuple(_read_simulation(entry) for entry in item.get("simulations", ()))) for item in spec["builds"] if isinstance(item, dict) and set(item) == build_fields and isinstance(item["weights"], list) and isinstance(item.get("simulations", ()), list))
                if len(builds) != len(spec["builds"]): raise ValueError
                specs.append((spec["specialization_id"], builds))
            character = CharacterScoreProfile(value["character_id"], value["name"], value["realm"], value["class_id"], tuple(specs), tuple(_read_item(item) for item in value["equipped"]), value.get("profile_name", ""), value.get("level", 0), value.get("race_id", 0))
            if not (len(character.character_id) == 32 and _valid_text(character.name) and _valid_text(character.realm) and (not character.profile_name or _valid_text(character.profile_name)) and isinstance(character.class_id, int) and character.class_id > 0 and isinstance(character.level, int) and 0 <= character.level <= 1000 and isinstance(character.race_id, int) and 0 <= character.race_id <= 1000): raise ValueError
            output.append(character)
        if len({item.character_id for item in output}) != len(output): raise ValueError
        return tuple(output)
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ItemScoreProfileError("character_profile_invalid") from exc


def save_profiles(root: Path, profiles: tuple[CharacterScoreProfile, ...]) -> None:
    if not isinstance(profiles, tuple) or len({item.character_id for item in profiles}) != len(profiles):
        raise ItemScoreProfileError("character_profile_invalid")
    path = _path(root); path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, prefix=".character-profiles-", suffix=".tmp", delete=False) as temporary:
        temporary.write(json.dumps(_document(profiles), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"); temporary_name = temporary.name
    os.replace(temporary_name, path)


def create_character(name: str, realm: str, class_id: int, profile_name: str = "") -> CharacterScoreProfile:
    if not _valid_text(name) or not _valid_text(realm) or (profile_name and not _valid_text(profile_name)) or isinstance(class_id, bool) or not isinstance(class_id, int) or class_id < 1:
        raise ItemScoreProfileError("character_profile_identity_invalid")
    return CharacterScoreProfile(uuid4().hex, name.strip(), realm.strip(), class_id, profile_name=profile_name.strip())


def rename_profile(character: CharacterScoreProfile, profile_name: str) -> CharacterScoreProfile:
    if not isinstance(character, CharacterScoreProfile) or not _valid_text(profile_name):
        raise ItemScoreProfileError("character_profile_name_invalid")
    return replace(character, profile_name=profile_name.strip())


def update_from_export(character: CharacterScoreProfile, snapshot: LiveAnalysisSnapshot) -> CharacterScoreProfile:
    if not isinstance(snapshot, LiveAnalysisSnapshot) or character.class_id != snapshot.class_id:
        raise ItemScoreProfileError("character_profile_export_incompatible")
    builds = tuple(BuildScoreProfile(item.config_id, item.name or f"Loadout {item.config_id}", item.talent_string) for item in snapshot.balance_talent_loadouts)
    existing = dict(character.specs); old = {build.build_id: build for build in existing.get(snapshot.specialization_id, ())}
    imported = tuple(build for build in existing.get(snapshot.specialization_id, ()) if build.build_id < 0)
    existing[snapshot.specialization_id] = tuple(replace(old.get(build.build_id, build), name=build.name, talent_string=build.talent_string) for build in builds) + imported
    return replace(character, specs=tuple(sorted(existing.items())), equipped=snapshot.equipped, level=snapshot.level, race_id=snapshot.race_id)


def store_imported_build(character: CharacterScoreProfile, specialization_id: int, name: str, talent_string: str) -> CharacterScoreProfile:
    if not isinstance(character, CharacterScoreProfile) or not isinstance(specialization_id, int) or specialization_id < 1 or not _valid_text(name) or not isinstance(talent_string, str) or _TALENT.fullmatch(talent_string) is None:
        raise ItemScoreProfileError("character_profile_import_invalid")
    specs = dict(character.specs); builds = list(specs.get(specialization_id, ()))
    for index, build in enumerate(builds):
        if build.build_id < 0 and build.name == name.strip() and build.talent_string == talent_string:
            return character
    build_id = min((build.build_id for build in builds if build.build_id < 0), default=0) - 1
    builds.append(BuildScoreProfile(build_id, name.strip(), talent_string))
    specs[specialization_id] = tuple(builds)
    return replace(character, specs=tuple(sorted(specs.items())))


def remove_builds(character: CharacterScoreProfile, specialization_id: int, build_ids: tuple[int, ...]) -> CharacterScoreProfile:
    if not isinstance(character, CharacterScoreProfile) or not isinstance(specialization_id, int) or specialization_id < 1 or not build_ids or any(not isinstance(value, int) or isinstance(value, bool) or value == 0 for value in build_ids):
        raise ItemScoreProfileError("character_profile_build_remove_invalid")
    specs = dict(character.specs); existing = specs.get(specialization_id, ())
    selected = set(build_ids)
    if not selected <= {build.build_id for build in existing}:
        raise ItemScoreProfileError("character_profile_build_unavailable")
    specs[specialization_id] = tuple(build for build in existing if build.build_id not in selected)
    return replace(character, specs=tuple(sorted(specs.items())))


def store_weight(character: CharacterScoreProfile, weight: ScoreWeights) -> CharacterScoreProfile:
    if not _valid_weights(weight) or weight.class_id != character.class_id or weight.build_id is None:
        raise ItemScoreProfileError("character_profile_weight_incompatible")
    specs = dict(character.specs); builds = list(specs.get(weight.specialization_id, ()))
    for index, build in enumerate(builds):
        if build.build_id == weight.build_id:
            retained = tuple(item for item in build.weights if item.source != weight.source)
            builds[index] = replace(build, weights=retained + (weight,)); specs[weight.specialization_id] = tuple(builds)
            return replace(character, specs=tuple(sorted(specs.items())))
    raise ItemScoreProfileError("character_profile_build_unavailable")


def store_simulation_results(character: CharacterScoreProfile, specialization_id: int, results: tuple[tuple[int, float], ...], weights: tuple[ScoreWeights, ...], relative_errors: tuple[tuple[int, float | None], ...] = (), run_ids: tuple[tuple[int, str], ...] = ()) -> CharacterScoreProfile:
    """Keep result values with their spec/build; no result is inferred from a score."""
    if not results or any(not isinstance(build_id, int) or isinstance(build_id, bool) or build_id == 0 or not isinstance(value, float) or not math.isfinite(value) or value <= 0 for build_id, value in results):
        raise ItemScoreProfileError("character_profile_simulation_invalid")
    versions = {value.build_id: value for value in weights if _valid_weights(value)}
    errors = dict(relative_errors); runs = dict(run_ids)
    if any(identifier not in {build_id for build_id, _ in results} or error is not None and (not isinstance(error, float) or not math.isfinite(error) or error < 0) for identifier, error in relative_errors):
        raise ItemScoreProfileError("character_profile_simulation_invalid")
    if any(identifier not in {build_id for build_id, _ in results} or not _valid_text(run_id, 160) for identifier, run_id in run_ids):
        raise ItemScoreProfileError("character_profile_simulation_invalid")
    specs = dict(character.specs); builds = list(specs.get(specialization_id, ()))
    by_id = {build.build_id: index for index, build in enumerate(builds)}
    if any(build_id not in by_id for build_id, _ in results):
        raise ItemScoreProfileError("character_profile_build_unavailable")
    for build_id, value in results:
        weight = versions.get(build_id)
        record = SimulationRecord(build_id, "DPS", value, weight.simc_version if weight else None, weight.scenario if weight else "Patchwerk", errors.get(build_id), runs.get(build_id))
        build = builds[by_id[build_id]]
        builds[by_id[build_id]] = replace(build, simulations=(record,))
    specs[specialization_id] = tuple(builds)
    return replace(character, specs=tuple(sorted(specs.items())))


def profile_details(character: CharacterScoreProfile) -> tuple[str, ...]:
    """Stable UI lines for browsing saved specs, builds and their real results."""
    output = [f"Equipo exportado: {len(character.equipped)} pieza(s)."]
    if character.equipped:
        output.append("  " + ", ".join(f"{item.slot}: #{item.item_id} ilvl {item.item_level}" for item in character.equipped))
    for specialization_id, builds in character.specs:
        output.append(f"Spec {specialization_id}")
        for build in builds:
            simulations = ", ".join(f"{entry.value:.0f} {entry.metric}" + (f" · error {entry.relative_error_percent:.3g}%" if entry.relative_error_percent is not None else "") for entry in build.simulations) or "sin simulación guardada"
            sources = ", ".join(weight.source for weight in build.weights) or "sin pesos"
            output.append(f"  {build.name}: {simulations}; pesos: {sources}")
    return tuple(output) or ("Sin specs o builds guardadas.",)


def profile_simulation_id(build_id: int) -> int:
    if build_id > 0:
        return build_id
    if -147_483_647 <= build_id < 0:
        return _PROFILE_IMPORT_OFFSET - build_id
    raise ItemScoreProfileError("character_profile_build_invalid")


def profile_export(character: CharacterScoreProfile, specialization_id: int) -> str:
    """Recreate a local, single-spec simulation input from an attended saved profile."""
    capability = next((item for item in CAPABILITIES if (item.class_id, item.specialization_id) == (character.class_id, specialization_id)), None)
    builds = dict(character.specs).get(specialization_id, ())
    if capability is None or not builds or character.level < 1 or character.race_id < 1 or not character.equipped:
        raise ItemScoreProfileError("character_profile_simulation_context_unavailable")
    document = {"schema_version": "0.7", "observation_type": "live_manual_analysis_export", "compatibility": {"wow_product": "retail", "build": 1, "interface_version": 1}, "subject": {"class_id": character.class_id, "specialization_id": specialization_id, "role": capability.role, "level": character.level, "race_id": character.race_id}, "analysis_context": {"talent_loadouts": [{"config_id": profile_simulation_id(build.build_id), "name": build.name, "talent_string": build.talent_string} for build in builds]}, "equipment": {"equipped": [_item(item) for item in character.equipped]}, "safety": {"contains_direct_identifiers": False, "executable": False, "no_automation": True}}
    return PREFIX + canonical_live_analysis_bytes(document).decode("utf-8")
