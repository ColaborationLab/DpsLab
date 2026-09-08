"""Create two in-memory SimulationCraft profiles from one real Restoration export."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from .addon_live_analysis_transport import LiveAnalysisSnapshot

_RESTORATION = (11, 105, "healer")
_RACES = {4: "night_elf"}
_SLOTS = {
    1: "head", 2: "neck", 3: "shoulder", 5: "chest", 6: "waist",
    7: "legs", 8: "feet", 9: "wrist", 10: "hands", 11: "finger1",
    12: "finger2", 13: "trinket1", 14: "trinket2", 15: "back",
    16: "main_hand", 17: "off_hand",
}


class DruidRestorationProfileError(ValueError):
    """The real export cannot produce the narrow Restoration profile pair."""


@dataclass(frozen=True, repr=False)
class DruidRestorationProfilePair:
    active_profile: str
    comparison_profile: str
    source_receipt_sha256: str


def _profile(snapshot: LiveAnalysisSnapshot, talent_string: str) -> str:
    race = _RACES.get(snapshot.race_id)
    if race is None:
        raise DruidRestorationProfileError("restoration_race_unavailable")
    lines = [
        "# DpsLab Restoration profile from a player-pasted live export.",
        'druid="DpsLab_Restoration"',
        f"level={snapshot.level}",
        f"race={race}",
        "role=attack",
        "spec=restoration",
        f"talents={talent_string}",
    ]
    for item in snapshot.equipped:
        slot = _SLOTS.get(item.location)
        if slot is not None:
            lines.append(f"{slot}=,id={item.item_id},ilevel={item.item_level}")
    return "\n".join(lines) + "\n"


def build_druid_restoration_profiles(snapshot: object) -> DruidRestorationProfilePair:
    """Return active and saved-loadout profiles; no files are written or executed."""
    if not isinstance(snapshot, LiveAnalysisSnapshot):
        raise DruidRestorationProfileError("restoration_export_invalid")
    if (snapshot.class_id, snapshot.specialization_id, snapshot.role) != _RESTORATION:
        raise DruidRestorationProfileError("restoration_required")
    loadouts = snapshot.restoration_talent_loadouts
    if loadouts is None:
        raise DruidRestorationProfileError("restoration_loadouts_unavailable")
    active = _profile(snapshot, loadouts.active_talent_string)
    comparison = _profile(snapshot, loadouts.comparison_talent_string)
    if active == comparison:
        raise DruidRestorationProfileError("restoration_comparison_invalid")
    return DruidRestorationProfilePair(active, comparison, snapshot.receipt_sha256)


def profile_sha256(profile: str) -> str:
    """Stable in-memory profile fingerprint for the later runner handoff."""
    return sha256(profile.encode("utf-8")).hexdigest()
