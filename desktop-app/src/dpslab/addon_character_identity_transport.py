"""Strict, non-executing decoder for manual character identity snapshots."""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Any, Mapping


class CharacterIdentityTransportError(ValueError):
    """The identity transport is malformed, unsafe, or incompatible."""


@dataclass(frozen=True)
class CharacterIdentitySnapshot:
    build: int
    interface_version: int
    class_id: int
    specialization_id: int
    role: str
    level: int
    race_id: int
    captured_at: int


MAX_PAYLOAD_BYTES = 4096
_ASSIGNMENT = re.compile(
    rb'(?:\r\n)?DpsLabObservationExport = "([0-9a-f]+)"(?:\r\n|\n)?\Z'
)
_ROOT = {"schema_version", "observation_type", "compatibility", "subject", "capture", "safety"}
_COMPATIBILITY = {"wow_product", "build", "interface_version"}
_SUBJECT = {"class_id", "specialization_id", "role", "level", "race_id"}
_CAPTURE = {"captured_at", "mode"}
_SAFETY = {
    "contains_character_data",
    "contains_direct_identifiers",
    "actionable",
    "executable",
    "no_automation",
}


def _fail(reason: str) -> None:
    raise CharacterIdentityTransportError(reason)


def _closed(value: Any, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        _fail(f"character_identity_{label}_fields_invalid")
    return value


def _integer(value: Any, label: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        _fail(f"character_identity_{label}_invalid")
    return value


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _fail("character_identity_duplicate_json_key")
        result[key] = value
    return result


def _nonfinite(_: str) -> None:
    _fail("character_identity_nonfinite_number")


def canonical_character_identity_bytes(document: Mapping[str, Any]) -> bytes:
    try:
        text = json.dumps(
            document,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as exc:
        raise CharacterIdentityTransportError("character_identity_not_canonicalizable") from exc
    return (text + "\n").encode("utf-8")


def _validate(document: Mapping[str, Any]) -> CharacterIdentitySnapshot:
    root = _closed(dict(document), _ROOT, "root")
    if root["schema_version"] != "0.1":
        _fail("character_identity_schema_incompatible")
    if root["observation_type"] != "character_identity_snapshot":
        _fail("character_identity_type_unsupported")

    compatibility = _closed(root["compatibility"], _COMPATIBILITY, "compatibility")
    if compatibility["wow_product"] != "retail":
        _fail("character_identity_product_unsupported")
    build = _integer(compatibility["build"], "build", 1, 9_999_999)
    interface_version = _integer(
        compatibility["interface_version"], "interface_version", 1, 9_999_999
    )

    subject = _closed(root["subject"], _SUBJECT, "subject")
    class_id = _integer(subject["class_id"], "class_id", 1, 1000)
    specialization_id = _integer(
        subject["specialization_id"], "specialization_id", 1, 100_000
    )
    role = subject["role"]
    if role not in {"damage", "tank", "healer"}:
        _fail("character_identity_role_invalid")
    level = _integer(subject["level"], "level", 1, 1000)
    race_id = _integer(subject["race_id"], "race_id", 1, 1000)

    capture = _closed(root["capture"], _CAPTURE, "capture")
    if capture["mode"] != "manual_command":
        _fail("character_identity_capture_mode_invalid")
    captured_at = _integer(capture["captured_at"], "captured_at", 1, 9_999_999_999)

    safety = _closed(root["safety"], _SAFETY, "safety")
    if safety != {
        "contains_character_data": True,
        "contains_direct_identifiers": False,
        "actionable": False,
        "executable": False,
        "no_automation": True,
    }:
        _fail("character_identity_safety_invalid")

    return CharacterIdentitySnapshot(
        build,
        interface_version,
        class_id,
        specialization_id,
        role,
        level,
        race_id,
        captured_at,
    )


def parse_character_identity_saved_variable(raw: bytes) -> CharacterIdentitySnapshot:
    """Parse one exact identity assignment without evaluating any Lua."""
    if not isinstance(raw, bytes):
        _fail("character_identity_transport_bytes_required")
    if len(raw) > 2 * MAX_PAYLOAD_BYTES + 64:
        _fail("character_identity_transport_too_large")
    match = _ASSIGNMENT.fullmatch(raw)
    if match is None or len(match.group(1)) % 2:
        _fail("character_identity_assignment_invalid")
    try:
        payload = bytes.fromhex(match.group(1).decode("ascii"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise CharacterIdentityTransportError("character_identity_hex_invalid") from exc
    if not 1 <= len(payload) <= MAX_PAYLOAD_BYTES:
        _fail("character_identity_payload_size_invalid")
    try:
        document = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_pairs,
            parse_constant=_nonfinite,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CharacterIdentityTransportError("character_identity_json_invalid") from exc
    if not isinstance(document, dict):
        _fail("character_identity_root_invalid")
    snapshot = _validate(document)
    if payload != canonical_character_identity_bytes(document):
        _fail("character_identity_json_noncanonical")
    return snapshot
