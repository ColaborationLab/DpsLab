"""Shared profile builder for one to four player-selected class/spec loadouts."""
from __future__ import annotations

from dataclasses import dataclass
import re

from .addon_live_analysis_transport import LiveAnalysisSnapshot, TalentLoadout
from .loadout_capabilities import RACE_TOKENS, LoadoutCapability, capability_for

_TALENT = re.compile(r"[A-Za-z0-9+/=]{1,2048}\Z")
_SLOTS = {1: "head", 2: "neck", 3: "shoulder", 5: "chest", 6: "waist", 7: "legs", 8: "feet", 9: "wrist", 10: "hands", 11: "finger1", 12: "finger2", 13: "trinket1", 14: "trinket2", 15: "back", 16: "main_hand", 17: "off_hand"}


class LoadoutProfileError(ValueError):
    pass


@dataclass(frozen=True, repr=False)
class ProfileLoadout:
    config_id: int
    name: str
    talent_string: str
    profile: str


@dataclass(frozen=True, repr=False)
class LoadoutProfileSet:
    capability: LoadoutCapability
    loadouts: tuple[ProfileLoadout, ...]
    source_receipt_sha256: str


def _profile(snapshot: LiveAnalysisSnapshot, capability: LoadoutCapability, talent_string: str) -> str:
    race = RACE_TOKENS.get(snapshot.race_id)
    if race is None:
        raise LoadoutProfileError("loadout_race_unavailable")
    lines = [
        "# DpsLab player-selected loadout; no gear is inferred.",
        f'{capability.class_token}="DpsLab_{capability.specialization_token}"',
        f"level={snapshot.level}", f"race={race}", "role=attack",
        f"spec={capability.specialization_token}", f"talents={talent_string}",
    ]
    for item in snapshot.equipped:
        slot = _SLOTS.get(item.location)
        if slot is not None:
            lines.append(f"{slot}=,id={item.item_id},ilevel={item.item_level}")
    return "\n".join(lines) + "\n"


def build_loadout_profiles(
    snapshot: object,
    selected_config_ids: tuple[int, ...] | None = None,
    imported_loadouts: tuple[tuple[str, str], ...] = (),
) -> LoadoutProfileSet:
    if not isinstance(snapshot, LiveAnalysisSnapshot):
        raise LoadoutProfileError("loadout_export_invalid")
    capability = capability_for(snapshot.class_id, snapshot.specialization_id, snapshot.role)
    if capability is None:
        raise LoadoutProfileError("loadout_specialization_unavailable")
    available = snapshot.balance_talent_loadouts
    if not available:
        raise LoadoutProfileError("loadout_talents_unavailable")
    by_id = {item.config_id: item for item in available}
    if len(by_id) != len(available):
        raise LoadoutProfileError("loadout_talents_invalid")
    if selected_config_ids is None:
        selected = available[:4]
    else:
        if not 1 <= len(selected_config_ids) <= 4 or len(set(selected_config_ids)) != len(selected_config_ids):
            raise LoadoutProfileError("loadout_selection_invalid")
        try:
            selected = tuple(by_id[item] for item in selected_config_ids)
        except KeyError as exc:
            raise LoadoutProfileError("loadout_selection_invalid") from exc
    if not isinstance(imported_loadouts, tuple) or any(
        not isinstance(item, tuple) or len(item) != 2 or not isinstance(item[0], str)
        or not 1 <= len(item[0].strip()) <= 80 or not isinstance(item[1], str)
        or _TALENT.fullmatch(item[1]) is None for item in imported_loadouts
    ):
        raise LoadoutProfileError("loadout_import_invalid")
    if not 1 <= len(selected) + len(imported_loadouts) <= 4:
        raise LoadoutProfileError("loadout_selection_invalid")
    candidates = tuple(ProfileLoadout(item.config_id, item.name or f"Loadout {item.config_id}", item.talent_string, _profile(snapshot, capability, item.talent_string)) for item in selected)
    imported = tuple(ProfileLoadout(-index, name.strip(), talent, _profile(snapshot, capability, talent)) for index, (name, talent) in enumerate(imported_loadouts, 1))
    values = candidates + imported
    if len({item.config_id for item in values}) != len(values) or len({item.profile for item in values}) != len(values):
        raise LoadoutProfileError("loadout_comparison_invalid")
    return LoadoutProfileSet(capability, values, snapshot.receipt_sha256)
