"""Bounded parser for non-actionable, synthetic Advisor guidance packages."""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Mapping


PREFIX = "DPSLAB-SYNTHETIC-ADVISOR-0.1\n"
MAX_BYTES = 4096
SCHEMA_VERSION = "0.1"
ROLES = frozenset({"damage", "tank", "healer"})
ROLE_SAFETY_FIRST = {
    "damage": "damage",
    "tank": "survival",
    "healer": "healing",
}


class AdvisorGuidancePackageError(ValueError):
    """Raised when an Advisor package is absent, unsafe, or non-synthetic."""


@dataclass(frozen=True, repr=False)
class AdvisorGuidancePackage:
    """The immutable, role-specific synthetic guidance surface."""

    role: str
    statistic_target: str
    gear_priority: str
    priority_display: str
    safety_first: str


def _fail(reason: str) -> None:
    raise AdvisorGuidancePackageError(reason)


def _closed_object(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        _fail(f"advisor_{label}_invalid")
    return value


def _unique_pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in values:
        if key in result:
            _fail("advisor_duplicate_json_key")
        result[key] = value
    return result


def _reject_nonfinite_number(_: str) -> None:
    _fail("advisor_nonfinite_number")


def _parse_canonical_json(raw: bytes) -> dict[str, Any]:
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_unique_pairs,
            parse_constant=_reject_nonfinite_number,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AdvisorGuidancePackageError("advisor_json_invalid") from exc
    if not isinstance(value, dict):
        _fail("advisor_root_invalid")
    if raw != canonical_advisor_guidance_package_bytes(value):
        _fail("advisor_json_noncanonical")
    return value


def _validate_role_entry(value: Any, role: str) -> dict[str, str]:
    entry = _closed_object(
        value,
        {"statistic_target", "gear_priority", "priority_display", "safety_first"},
        "role",
    )
    if not all(isinstance(item, str) and 1 <= len(item) <= 160 for item in entry.values()):
        _fail("advisor_role_invalid")
    if entry["safety_first"] != ROLE_SAFETY_FIRST[role]:
        _fail("advisor_role_invalid")
    return entry


def canonical_advisor_guidance_package_bytes(value: Mapping[str, Any]) -> bytes:
    """Encode a package in the only accepted JSON representation."""

    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def parse_synthetic_advisor_guidance_package(
    text: str, role: str
) -> AdvisorGuidancePackage:
    """Parse exactly one bounded synthetic package for an allowed role."""

    if not isinstance(text, str) or not text.startswith(PREFIX):
        _fail("advisor_prefix_invalid")
    if role not in ROLES:
        _fail("advisor_role_invalid")

    raw = text[len(PREFIX) :].encode("utf-8")
    if not 1 <= len(raw) <= MAX_BYTES:
        _fail("advisor_payload_size_invalid")

    root = _closed_object(
        _parse_canonical_json(raw),
        {"lifecycle", "roles", "safety", "schema_version", "synthetic"},
        "root",
    )
    if root["schema_version"] != SCHEMA_VERSION or root["synthetic"] is not True:
        _fail("advisor_schema_invalid")
    lifecycle = _closed_object(root["lifecycle"], {"state"}, "lifecycle")
    if lifecycle["state"] != "synthetic_fixture":
        _fail("advisor_lifecycle_invalid")
    safety = _closed_object(root["safety"], {"actionable", "no_automation"}, "safety")
    if safety != {"actionable": False, "no_automation": True}:
        _fail("advisor_safety_invalid")
    roles = _closed_object(root["roles"], set(ROLES), "roles")
    entry = _validate_role_entry(roles[role], role)
    return AdvisorGuidancePackage(role=role, **entry)
