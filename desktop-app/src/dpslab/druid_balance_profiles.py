"""Create two in-memory SimulationCraft profiles from one real Balance export."""
from __future__ import annotations

from dataclasses import dataclass
import re

from .addon_live_analysis_transport import LiveAnalysisSnapshot, TalentLoadout
from .druid_restoration_profiles import _RACES, _SLOTS

_BALANCE = (11, 102, "damage")
_TALENT_STRING = re.compile(r"[A-Za-z0-9+/=]{1,2048}\Z")


class DruidBalanceProfileError(ValueError):
    """The real export cannot produce the narrow Balance profile pair."""


@dataclass(frozen=True, repr=False)
class DruidBalanceProfile:
    config_id: int
    talent_string: str
    profile: str
    name: str = ""


@dataclass(frozen=True, repr=False)
class DruidBalanceProfileSet:
    loadouts: tuple[DruidBalanceProfile, ...]
    source_receipt_sha256: str

    @property
    def active_profile(self) -> str:
        return self.loadouts[0].profile

    @property
    def comparison_profile(self) -> str:
        return self.loadouts[1].profile


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


def build_druid_balance_profiles(
    snapshot: object, selected_config_ids: tuple[int, ...] | None = None,
    imported_talent_strings: tuple[str, ...] = (),
) -> DruidBalanceProfileSet:
    if not isinstance(snapshot, LiveAnalysisSnapshot):
        raise DruidBalanceProfileError("balance_export_invalid")
    if (snapshot.class_id, snapshot.specialization_id, snapshot.role) != _BALANCE:
        raise DruidBalanceProfileError("balance_required")
    available = snapshot.balance_talent_loadouts
    if not available:
        raise DruidBalanceProfileError("balance_loadouts_unavailable")
    if selected_config_ids is None:
        selected = available
    else:
        if not 1 <= len(selected_config_ids) <= 4 or len(set(selected_config_ids)) != len(selected_config_ids):
            raise DruidBalanceProfileError("balance_selection_invalid")
        by_id = {item.config_id: item for item in available}
        try:
            selected = tuple(by_id[item] for item in selected_config_ids)
        except KeyError as exc:
            raise DruidBalanceProfileError("balance_selection_invalid") from exc
    if not isinstance(imported_talent_strings, tuple) or any(not isinstance(item, str) or _TALENT_STRING.fullmatch(item) is None for item in imported_talent_strings):
        raise DruidBalanceProfileError("balance_import_invalid")
    if len(set(imported_talent_strings)) != len(imported_talent_strings) or set(imported_talent_strings) & {item.talent_string for item in selected}:
        raise DruidBalanceProfileError("balance_import_invalid")
    if not 1 <= len(selected) + len(imported_talent_strings) <= 4:
        raise DruidBalanceProfileError("balance_selection_invalid")
    profiles = tuple(DruidBalanceProfile(item.config_id, item.talent_string, _profile(snapshot, item.talent_string), item.name or f"Loadout {item.config_id}") for item in selected) + tuple(DruidBalanceProfile(-index, item, _profile(snapshot, item), f"Importada {index}") for index, item in enumerate(imported_talent_strings, 1))
    if len({item.profile for item in profiles}) != len(profiles):
        raise DruidBalanceProfileError("balance_comparison_invalid")
    return DruidBalanceProfileSet(profiles, snapshot.receipt_sha256)
