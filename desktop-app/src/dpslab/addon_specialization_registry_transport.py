"""Strict decoder for an attended class specialization registry snapshot."""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Any, Mapping


class SpecializationRegistryTransportError(ValueError):
    """The registry transport is malformed, unsafe, or incompatible."""


@dataclass(frozen=True)
class SpecializationRegistryEntry:
    specialization_id: int
    role: str


@dataclass(frozen=True)
class ClassSpecializationRegistrySnapshot:
    build: int
    interface_version: int
    class_id: int
    specializations: tuple[SpecializationRegistryEntry, ...]
    captured_at: int


MAX_PAYLOAD_BYTES = 4096
_ASSIGNMENT = re.compile(
    rb'(?:\r\n)?DpsLabObservationExport = "([0-9a-f]+)"(?:\r\n|\n)?\Z'
)
_ROOT = {
    "schema_version",
    "observation_type",
    "compatibility",
    "subject",
    "specializations",
    "capture",
    "safety",
}
_COMPATIBILITY = {"wow_product", "build", "interface_version"}
_SUBJECT = {"class_id"}
_SPECIALIZATION = {"specialization_id", "role"}
_CAPTURE = {"captured_at", "mode"}
_SAFETY = {
    "contains_character_data",
    "contains_direct_identifiers",
    "actionable",
    "executable",
    "no_automation",
}


def _fail(reason: str) -> None:
    raise SpecializationRegistryTransportError(reason)


def _closed(value: Any, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        _fail(f"specialization_registry_{label}_fields_invalid")
    return value


def _integer(value: Any, label: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        _fail(f"specialization_registry_{label}_invalid")
    return value


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _fail("specialization_registry_duplicate_json_key")
        result[key] = value
    return result


def _nonfinite(_: str) -> None:
    _fail("specialization_registry_nonfinite_number")


def canonical_specialization_registry_bytes(document: Mapping[str, Any]) -> bytes:
    try:
        text = json.dumps(
            document,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as exc:
        raise SpecializationRegistryTransportError(
            "specialization_registry_not_canonicalizable"
        ) from exc
    return (text + "\n").encode("utf-8")


def _validate(document: Mapping[str, Any]) -> ClassSpecializationRegistrySnapshot:
    root = _closed(dict(document), _ROOT, "root")
    if root["schema_version"] != "0.1":
        _fail("specialization_registry_schema_incompatible")
    if root["observation_type"] != "class_specialization_registry_snapshot":
        _fail("specialization_registry_type_unsupported")

    compatibility = _closed(root["compatibility"], _COMPATIBILITY, "compatibility")
    if compatibility["wow_product"] != "retail":
        _fail("specialization_registry_product_unsupported")
    build = _integer(compatibility["build"], "build", 1, 9_999_999)
    interface_version = _integer(
        compatibility["interface_version"], "interface_version", 1, 9_999_999
    )
    subject = _closed(root["subject"], _SUBJECT, "subject")
    class_id = _integer(subject["class_id"], "class_id", 1, 1000)

    values = root["specializations"]
    if not isinstance(values, list) or len(values) != 4:
        _fail("specialization_registry_shape_invalid")
    entries: list[SpecializationRegistryEntry] = []
    seen: set[int] = set()
    counts = {"damage": 0, "tank": 0, "healer": 0}
    for value in values:
        item = _closed(value, _SPECIALIZATION, "entry")
        specialization_id = _integer(
            item["specialization_id"], "specialization_id", 1, 100_000
        )
        if specialization_id in seen:
            _fail("specialization_registry_specialization_duplicate")
        seen.add(specialization_id)
        role = item["role"]
        if role not in counts:
            _fail("specialization_registry_role_invalid")
        counts[role] += 1
        entries.append(SpecializationRegistryEntry(specialization_id, role))
    if counts != {"damage": 2, "tank": 1, "healer": 1}:
        _fail("specialization_registry_role_shape_invalid")

    capture = _closed(root["capture"], _CAPTURE, "capture")
    if capture["mode"] != "manual_command":
        _fail("specialization_registry_capture_mode_invalid")
    captured_at = _integer(capture["captured_at"], "captured_at", 1, 9_999_999_999)
    safety = _closed(root["safety"], _SAFETY, "safety")
    if safety != {
        "contains_character_data": True,
        "contains_direct_identifiers": False,
        "actionable": False,
        "executable": False,
        "no_automation": True,
    }:
        _fail("specialization_registry_safety_invalid")
    return ClassSpecializationRegistrySnapshot(
        build, interface_version, class_id, tuple(entries), captured_at
    )


def parse_specialization_registry_saved_variable(
    raw: bytes,
) -> ClassSpecializationRegistrySnapshot:
    """Parse one exact registry assignment without evaluating any Lua."""
    if not isinstance(raw, bytes):
        _fail("specialization_registry_transport_bytes_required")
    if len(raw) > 2 * MAX_PAYLOAD_BYTES + 64:
        _fail("specialization_registry_transport_too_large")
    match = _ASSIGNMENT.fullmatch(raw)
    if match is None or len(match.group(1)) % 2:
        _fail("specialization_registry_assignment_invalid")
    try:
        payload = bytes.fromhex(match.group(1).decode("ascii"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise SpecializationRegistryTransportError(
            "specialization_registry_hex_invalid"
        ) from exc
    if not 1 <= len(payload) <= MAX_PAYLOAD_BYTES:
        _fail("specialization_registry_payload_size_invalid")
    try:
        document = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_pairs,
            parse_constant=_nonfinite,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SpecializationRegistryTransportError(
            "specialization_registry_json_invalid"
        ) from exc
    if not isinstance(document, dict):
        _fail("specialization_registry_root_invalid")
    snapshot = _validate(document)
    if payload != canonical_specialization_registry_bytes(document):
        _fail("specialization_registry_json_noncanonical")
    return snapshot
