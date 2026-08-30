"""Fail-closed binding from a validated identity to Druid role context."""

from __future__ import annotations

from dataclasses import dataclass

from .addon_character_identity_transport import CharacterIdentitySnapshot
from .druid_role_context import DruidRolePolicy, select_druid_role_context


@dataclass(frozen=True)
class DruidSpecializationBinding:
    specialization_id: int
    specialization: str
    role: str


@dataclass(frozen=True)
class DruidIdentityRegistry:
    class_id: int
    bindings: tuple[DruidSpecializationBinding, ...]


@dataclass(frozen=True)
class DruidIdentityContextSelection:
    status: str
    reason: str | None
    policy: DruidRolePolicy | None


_SPECIALIZATIONS = {"balance", "feral", "guardian", "restoration"}


def _bounded_integer(value: object, minimum: int, maximum: int) -> bool:
    return not isinstance(value, bool) and isinstance(value, int) and minimum <= value <= maximum


def _valid_registry(registry: object) -> bool:
    if not isinstance(registry, DruidIdentityRegistry):
        return False
    if not _bounded_integer(registry.class_id, 1, 1000):
        return False
    if not isinstance(registry.bindings, tuple) or len(registry.bindings) != 4:
        return False
    if any(not isinstance(item, DruidSpecializationBinding) for item in registry.bindings):
        return False
    identifiers: list[int] = []
    specializations: list[str] = []
    for binding in registry.bindings:
        if not _bounded_integer(binding.specialization_id, 1, 100_000):
            return False
        context = select_druid_role_context(binding.specialization, binding.role)
        if context.status != "context_available":
            return False
        identifiers.append(binding.specialization_id)
        specializations.append(binding.specialization)
    return (
        len(identifiers) == len(set(identifiers))
        and set(specializations) == _SPECIALIZATIONS
        and len(specializations) == len(set(specializations))
    )


def _valid_snapshot(snapshot: object) -> bool:
    if not isinstance(snapshot, CharacterIdentitySnapshot):
        return False
    return (
        _bounded_integer(snapshot.build, 1, 9_999_999)
        and _bounded_integer(snapshot.interface_version, 1, 9_999_999)
        and _bounded_integer(snapshot.class_id, 1, 1000)
        and _bounded_integer(snapshot.specialization_id, 1, 100_000)
        and snapshot.role in {"damage", "tank", "healer"}
        and _bounded_integer(snapshot.level, 1, 1000)
        and _bounded_integer(snapshot.race_id, 1, 1000)
        and _bounded_integer(snapshot.captured_at, 1, 9_999_999_999)
    )


def bind_druid_identity_context(
    snapshot: object, registry: object
) -> DruidIdentityContextSelection:
    """Return a semantic policy only for an exact injected identity mapping."""

    if not _valid_registry(registry):
        return DruidIdentityContextSelection(
            "context_unavailable", "registry_invalid", None
        )
    if not _valid_snapshot(snapshot):
        return DruidIdentityContextSelection(
            "context_unavailable", "observation_invalid", None
        )
    if snapshot.class_id != registry.class_id:
        return DruidIdentityContextSelection(
            "context_unavailable", "class_mismatch", None
        )
    matches = [
        binding
        for binding in registry.bindings
        if binding.specialization_id == snapshot.specialization_id
    ]
    if len(matches) != 1:
        return DruidIdentityContextSelection(
            "context_unavailable", "specialization_unmapped", None
        )
    binding = matches[0]
    if binding.role != snapshot.role:
        return DruidIdentityContextSelection(
            "context_unavailable", "role_mismatch", None
        )
    context = select_druid_role_context(binding.specialization, snapshot.role)
    if context.status != "context_available" or context.policy is None:
        return DruidIdentityContextSelection(
            "context_unavailable", "policy_unavailable", None
        )
    return DruidIdentityContextSelection("context_available", None, context.policy)
