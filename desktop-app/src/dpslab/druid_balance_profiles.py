"""Create two in-memory SimulationCraft profiles from one real Balance export."""
from __future__ import annotations

from dataclasses import dataclass

from .addon_live_analysis_transport import LiveAnalysisSnapshot
from .druid_restoration_profiles import _RACES, _SLOTS

_BALANCE = (11, 102, "damage")


class DruidBalanceProfileError(ValueError):
    """The real export cannot produce the narrow Balance profile pair."""


@dataclass(frozen=True, repr=False)
class DruidBalanceProfilePair:
    active_profile: str
    comparison_profile: str
    source_receipt_sha256: str


def _profile(snapshot: LiveAnalysisSnapshot, talent_string: str) -> str:
    race = _RACES.get(snapshot.race_id)
    if race is None:
        raise DruidBalanceProfileError("balance_race_unavailable")
    lines = [
        "# DpsLab Balance profile from a player-pasted live export.",
        'druid="DpsLab_Balance"', f"level={snapshot.level}", f"race={race}",
        "role=attack", "spec=balance", f"talents={talent_string}",
    ]
    for item in snapshot.equipped:
        slot = _SLOTS.get(item.location)
        if slot is not None:
            lines.append(f"{slot}=,id={item.item_id},ilevel={item.item_level}")
    return "\n".join(lines) + "\n"


def build_druid_balance_profiles(snapshot: object) -> DruidBalanceProfilePair:
    if not isinstance(snapshot, LiveAnalysisSnapshot):
        raise DruidBalanceProfileError("balance_export_invalid")
    if (snapshot.class_id, snapshot.specialization_id, snapshot.role) != _BALANCE:
        raise DruidBalanceProfileError("balance_required")
    loadouts = snapshot.talent_loadouts
    if loadouts is None:
        raise DruidBalanceProfileError("balance_loadouts_unavailable")
    active = _profile(snapshot, loadouts.active_talent_string)
    comparison = _profile(snapshot, loadouts.comparison_talent_string)
    if active == comparison:
        raise DruidBalanceProfileError("balance_comparison_invalid")
    return DruidBalanceProfilePair(active, comparison, snapshot.receipt_sha256)
