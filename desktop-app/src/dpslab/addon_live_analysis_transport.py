"""Strict decoder for player-pasted DpsLab live analysis exports."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Any, Mapping

PREFIX = "DPSLAB-LIVE-ANALYSIS-0.1\n"
MAX_BYTES = 65536
_TALENT_STRING = re.compile(r"[A-Za-z0-9+/=]{1,2048}\Z")


class LiveAnalysisTransportError(ValueError):
    pass


@dataclass(frozen=True, repr=False)
class LiveAnalysisItem:
    item_id: int
    item_level: int
    item_link: str
    location: int
    slot: str
    source: str
    expansion_id: int | None = None


@dataclass(frozen=True, repr=False)
class TalentLoadoutContext:
    state: str
    loadout_token: str | None
    selected_entry_ids: tuple[int, ...]
    reason: str | None


@dataclass(frozen=True, repr=False)
class RestorationTalentLoadouts:
    active_config_id: int
    active_talent_string: str
    comparison_config_id: int
    comparison_talent_string: str


@dataclass(frozen=True, repr=False)
class LiveAnalysisSnapshot:
    build: int
    interface_version: int
    class_id: int
    specialization_id: int
    role: str
    level: int
    race_id: int
    equipped: tuple[LiveAnalysisItem, ...]
    bag: tuple[LiveAnalysisItem, ...]
    receipt_sha256: str
    item_eligibility_basis: str | None = None
    current_expansion_id: int | None = None
    talent_loadout: TalentLoadoutContext | None = None
    restoration_talent_loadouts: RestorationTalentLoadouts | None = None


def _fail(reason: str) -> None:
    raise LiveAnalysisTransportError(reason)


def _integer(value: Any, name: str, low: int, high: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        _fail(f"live_analysis_{name}_invalid")
    return value


def _closed(value: Any, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        _fail(f"live_analysis_{label}_fields_invalid")
    return value


def _pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in values:
        if key in result:
            _fail("live_analysis_duplicate_json_key")
        result[key] = value
    return result


def _nonfinite(_: str) -> None:
    _fail("live_analysis_nonfinite_number")


def canonical_live_analysis_bytes(document: Mapping[str, Any]) -> bytes:
    try:
        return (json.dumps(document, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")) + "\n").encode()
    except (TypeError, ValueError) as exc:
        raise LiveAnalysisTransportError("live_analysis_not_canonicalizable") from exc


def _item(value: Any, source: str, schema_version: str) -> LiveAnalysisItem:
    fields = {"item_id", "item_level", "item_link", "location", "slot", "source"}
    if schema_version in {"0.2", "0.3"}:
        fields.add("expansion_id")
    item = _closed(value, fields, "item")
    if item["source"] != source or not isinstance(item["item_link"], str) or not 1 <= len(item["item_link"]) <= 2048:
        _fail("live_analysis_item_invalid")
    if not isinstance(item["slot"], str) or not item["slot"]:
        _fail("live_analysis_item_invalid")
    expansion_id = None if schema_version in {"0.1", "0.4"} else _integer(item["expansion_id"], "expansion_id", 0, 100)
    return LiveAnalysisItem(
        _integer(item["item_id"], "item_id", 1, 9_999_999),
        _integer(item["item_level"], "item_level", 1, 9_999),
        item["item_link"],
        _integer(item["location"], "location", 0, 40),
        item["slot"], source, expansion_id,
    )


def _legacy_talent_context(value: Any) -> TalentLoadoutContext:
    context = _closed(value, {"talent_loadout"}, "analysis_context")
    loadout = context["talent_loadout"]
    if not isinstance(loadout, dict) or not isinstance(loadout.get("state"), str):
        _fail("live_analysis_talent_context_invalid")
    if loadout["state"] == "unavailable":
        closed = _closed(loadout, {"state", "reason"}, "talent_loadout")
        if not isinstance(closed["reason"], str) or not 1 <= len(closed["reason"]) <= 64:
            _fail("live_analysis_talent_context_invalid")
        return TalentLoadoutContext("unavailable", None, (), closed["reason"])
    closed = _closed(loadout, {"state", "loadout_token", "selected_entry_ids"}, "talent_loadout")
    if closed["state"] != "available" or not isinstance(closed["loadout_token"], str):
        _fail("live_analysis_talent_context_invalid")
    if not isinstance(closed["selected_entry_ids"], list):
        _fail("live_analysis_talent_context_invalid")
    values = tuple(_integer(item, "talent_entry_id", 1, 9_999_999) for item in closed["selected_entry_ids"])
    if not 1 <= len(values) <= 256 or tuple(sorted(values)) != values or len(set(values)) != len(values):
        _fail("live_analysis_talent_context_invalid")
    return TalentLoadoutContext("available", closed["loadout_token"], values, None)


def _restoration_loadouts(value: Any) -> RestorationTalentLoadouts:
    context = _closed(value, {"talent_loadouts"}, "analysis_context")
    loadouts = _closed(context["talent_loadouts"], {"active", "comparison"}, "talent_loadouts")

    def read(label: str) -> tuple[int, str]:
        item = _closed(loadouts[label], {"config_id", "talent_string"}, "talent_loadout")
        text = item["talent_string"]
        if not isinstance(text, str) or _TALENT_STRING.fullmatch(text) is None:
            _fail("live_analysis_talent_loadout_invalid")
        return _integer(item["config_id"], "talent_config_id", 1, 2_147_483_647), text

    active_id, active = read("active")
    comparison_id, comparison = read("comparison")
    if active_id == comparison_id or active == comparison:
        _fail("live_analysis_talent_loadout_invalid")
    return RestorationTalentLoadouts(active_id, active, comparison_id, comparison)


def parse_live_analysis_export(text: str) -> LiveAnalysisSnapshot:
    if not isinstance(text, str) or not text.startswith(PREFIX):
        _fail("live_analysis_prefix_invalid")
    raw = text[len(PREFIX):].encode("utf-8")
    if not 1 <= len(raw) <= MAX_BYTES:
        _fail("live_analysis_payload_size_invalid")
    try:
        document = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_nonfinite)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LiveAnalysisTransportError("live_analysis_json_invalid") from exc
    if not isinstance(document, dict) or document.get("schema_version") not in {"0.1", "0.2", "0.3", "0.4"}:
        _fail("live_analysis_schema_incompatible")
    schema_version = document["schema_version"]
    root_fields = {"compatibility", "equipment", "observation_type", "safety", "schema_version", "subject"}
    if schema_version in {"0.2", "0.3"}:
        root_fields.add("item_eligibility")
    if schema_version in {"0.3", "0.4"}:
        root_fields.add("analysis_context")
    root = _closed(document, root_fields, "root")
    if root["observation_type"] != "live_manual_analysis_export":
        _fail("live_analysis_schema_incompatible")
    if raw != canonical_live_analysis_bytes(document):
        _fail("live_analysis_json_noncanonical")
    compatibility = _closed(root["compatibility"], {"build", "interface_version", "wow_product"}, "compatibility")
    if compatibility["wow_product"] != "retail":
        _fail("live_analysis_product_unsupported")
    subject = _closed(root["subject"], {"class_id", "level", "race_id", "role", "specialization_id"}, "subject")
    if subject["role"] not in {"damage", "healer", "tank"}:
        _fail("live_analysis_role_invalid")
    equipment_fields = {"equipped"} if schema_version == "0.4" else {"bag", "equipped"}
    equipment = _closed(root["equipment"], equipment_fields, "equipment")
    if not isinstance(equipment["equipped"], list) or not 1 <= len(equipment["equipped"]) <= 19:
        _fail("live_analysis_items_invalid")
    bag_values = [] if schema_version == "0.4" else equipment["bag"]
    if not isinstance(bag_values, list) or len(bag_values) > 40:
        _fail("live_analysis_items_invalid")
    equipped = tuple(_item(item, "equipped", schema_version) for item in equipment["equipped"])
    bag = tuple(_item(item, "designated_bag", schema_version) for item in bag_values)
    if len({(item.source, item.location) for item in (*equipped, *bag)}) != len(equipped) + len(bag):
        _fail("live_analysis_item_duplicate")
    safety = _closed(root["safety"], {"contains_direct_identifiers", "executable", "no_automation"}, "safety")
    if safety != {"contains_direct_identifiers": False, "executable": False, "no_automation": True}:
        _fail("live_analysis_safety_invalid")
    eligibility_basis = current_expansion_id = None
    if schema_version in {"0.2", "0.3"}:
        eligibility = _closed(root["item_eligibility"], {"basis", "current_expansion_id"}, "item_eligibility")
        if eligibility["basis"] != "blizzard_client_item_api":
            _fail("live_analysis_item_eligibility_invalid")
        eligibility_basis = eligibility["basis"]
        current_expansion_id = _integer(eligibility["current_expansion_id"], "current_expansion_id", 1, 100)
    legacy = _legacy_talent_context(root["analysis_context"]) if schema_version == "0.3" else None
    restoration = _restoration_loadouts(root["analysis_context"]) if schema_version == "0.4" else None
    return LiveAnalysisSnapshot(
        _integer(compatibility["build"], "build", 1, 9_999_999),
        _integer(compatibility["interface_version"], "interface_version", 1, 9_999_999),
        _integer(subject["class_id"], "class_id", 1, 1000),
        _integer(subject["specialization_id"], "specialization_id", 1, 100000),
        subject["role"], _integer(subject["level"], "level", 1, 1000),
        _integer(subject["race_id"], "race_id", 1, 1000), equipped, bag,
        hashlib.sha256(raw).hexdigest(), eligibility_basis, current_expansion_id,
        legacy, restoration,
    )
