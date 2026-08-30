"""Pure role priorities for the first DpsLab Druid vertical slice.

This module describes objective ordering.  It deliberately contains no game
facts, spell instructions, character data, or recommendation selection.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DruidRolePolicy:
    """Closed semantic policy for one canonical Druid specialization."""

    specialization: str
    role: str
    hard_constraints: tuple[str, ...]
    primary_objectives: tuple[str, ...]
    secondary_objectives: tuple[str, ...]


@dataclass(frozen=True)
class DruidRoleContextSelection:
    """Fail-closed result of resolving a specialization and observed role."""

    status: str
    reason: str | None
    policy: DruidRolePolicy | None


_HARD_CONSTRAINTS = ("encounter_obligations", "character_survival")
_ROLE_OBJECTIVES = {
    "damage": (("damage_output",), ()),
    "tank": (
        ("survival", "active_mitigation", "threat_stability"),
        ("damage_output",),
    ),
    "healer": (
        (
            "ally_survival",
            "healing_stability",
            "dispel_readiness",
            "emergency_capacity",
        ),
        ("damage_output",),
    ),
}
_DRUID_SPECIALIZATION_ROLES = {
    "balance": "damage",
    "feral": "damage",
    "guardian": "tank",
    "restoration": "healer",
}


def select_druid_role_context(
    specialization: object, observed_role: object
) -> DruidRoleContextSelection:
    """Resolve only an exact canonical pair; ambiguity remains unavailable."""

    if not isinstance(specialization, str) or specialization not in _DRUID_SPECIALIZATION_ROLES:
        return DruidRoleContextSelection(
            "context_unavailable", "specialization_unknown", None
        )
    expected_role = _DRUID_SPECIALIZATION_ROLES[specialization]
    if not isinstance(observed_role, str) or observed_role != expected_role:
        return DruidRoleContextSelection(
            "context_unavailable", "role_mismatch", None
        )
    primary, secondary = _ROLE_OBJECTIVES[expected_role]
    policy = DruidRolePolicy(
        specialization=specialization,
        role=expected_role,
        hard_constraints=_HARD_CONSTRAINTS,
        primary_objectives=primary,
        secondary_objectives=secondary,
    )
    return DruidRoleContextSelection("context_available", None, policy)
