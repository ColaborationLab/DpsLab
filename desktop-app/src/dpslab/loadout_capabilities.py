"""Closed class/spec tokens used to build player-selected SimC profiles.

The table describes the profile vocabulary DpsLab can emit.  It deliberately
does not claim that the bundled executable was tested: that requires a
separately authorized SimC probe against the shipped binary.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, repr=False)
class LoadoutCapability:
    class_id: int
    specialization_id: int
    class_token: str
    specialization_token: str
    role: str

    @property
    def label(self) -> str:
        return f"{self.class_token.replace('_', ' ').title()} — {self.specialization_token.replace('_', ' ').title()}"


_SPECS = (
    (1, "warrior", ((71, "arms", "damage"), (72, "fury", "damage"), (73, "protection", "tank"))),
    (2, "paladin", ((65, "holy", "healer"), (66, "protection", "tank"), (70, "retribution", "damage"))),
    (3, "hunter", ((253, "beast_mastery", "damage"), (254, "marksmanship", "damage"), (255, "survival", "damage"))),
    (4, "rogue", ((259, "assassination", "damage"), (260, "outlaw", "damage"), (261, "subtlety", "damage"))),
    (5, "priest", ((256, "discipline", "healer"), (257, "holy", "healer"), (258, "shadow", "damage"))),
    (6, "deathknight", ((250, "blood", "tank"), (251, "frost", "damage"), (252, "unholy", "damage"))),
    (7, "shaman", ((262, "elemental", "damage"), (263, "enhancement", "damage"), (264, "restoration", "healer"))),
    (8, "mage", ((62, "arcane", "damage"), (63, "fire", "damage"), (64, "frost", "damage"))),
    (9, "warlock", ((265, "affliction", "damage"), (266, "demonology", "damage"), (267, "destruction", "damage"))),
    (10, "monk", ((268, "brewmaster", "tank"), (269, "windwalker", "damage"), (270, "mistweaver", "healer"))),
    (11, "druid", ((102, "balance", "damage"), (103, "feral", "damage"), (104, "guardian", "tank"), (105, "restoration", "healer"))),
    (12, "demonhunter", ((577, "havoc", "damage"), (581, "vengeance", "tank"))),
    (13, "evoker", ((1467, "devastation", "damage"), (1468, "preservation", "healer"), (1473, "augmentation", "damage"))),
)

CAPABILITIES = tuple(
    LoadoutCapability(class_id, specialization_id, class_token, specialization_token, role)
    for class_id, class_token, specs in _SPECS
    for specialization_id, specialization_token, role in specs
)
_BY_ID = {(item.class_id, item.specialization_id): item for item in CAPABILITIES}

# `race=` is a SimC input token. Unknown future race ids fail closed instead
# of being silently replaced with a different race.
RACE_TOKENS = {
    1: "human", 2: "orc", 3: "dwarf", 4: "night_elf", 5: "undead",
    6: "tauren", 7: "gnome", 8: "troll", 9: "goblin", 10: "blood_elf",
    11: "draenei", 22: "worgen", 24: "pandaren", 25: "pandaren",
    26: "pandaren", 27: "nightborne", 28: "highmountain_tauren",
    29: "void_elf", 30: "lightforged_draenei", 31: "zandalari_troll",
    32: "kul_tiran", 34: "dark_iron_dwarf", 35: "vulpera", 36: "maghar_orc",
    37: "mechagnome", 52: "dracthyr", 70: "dracthyr", 84: "earthen", 85: "earthen",
}


def capability_for(class_id: object, specialization_id: object, role: object) -> LoadoutCapability | None:
    if isinstance(class_id, bool) or isinstance(specialization_id, bool):
        return None
    if not isinstance(class_id, int) or not isinstance(specialization_id, int) or role not in {"damage", "tank", "healer"}:
        return None
    capability = _BY_ID.get((class_id, specialization_id))
    return capability if capability is not None and capability.role == role else None


def capability_rows() -> tuple[tuple[int, int, str, str, str], ...]:
    """Stable rows for tests and a later authorized binary capability probe."""
    return tuple((item.class_id, item.specialization_id, item.class_token, item.specialization_token, item.role) for item in CAPABILITIES)
