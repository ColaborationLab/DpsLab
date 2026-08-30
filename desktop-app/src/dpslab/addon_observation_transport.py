"""Strict, non-executing decoder for synthetic addon observation exports."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
import re
from typing import Any, Mapping


class AddonObservationTransportError(ValueError):
    """The observation transport is malformed, unsafe, or incompatible."""


@dataclass(frozen=True)
class SyntheticAddonObservation:
    observation_id: str
    captured_at: str
    build: int
    interface_version: int
    class_token: str
    specialization_token: str
    role: str
    sample_window_seconds: int
    damage_events: int
    incoming_damage_events: int
    healing_events: int


MAX_PAYLOAD_BYTES = 4096
_ASSIGNMENT = re.compile(
    rb'(?:\r\n)?DpsLabObservationExport = "([0-9a-f]+)"(?:\r\n|\n)?\Z'
)
_TOKEN = re.compile(r"[a-z0-9][a-z0-9_.-]{0,79}")
_ROOT = {"schema_version", "identity", "producer", "compatibility", "subject", "observation", "safety"}
_IDENTITY = {"observation_id", "captured_at"}
_PRODUCER = {"producer_id", "producer_version"}
_COMPATIBILITY = {"wow_product", "build", "interface_version"}
_SUBJECT = {"synthetic", "class_token", "specialization_token", "role"}
_OBSERVATION = {"state", "sample_window_seconds", "event_count", "byte_count", "signals"}
_SIGNALS = {"damage_events", "incoming_damage_events", "healing_events"}
_SAFETY = {"synthetic", "contains_personal_data", "executable", "actionable", "no_automation"}


def _fail(reason: str) -> None:
    raise AddonObservationTransportError(reason)


def _closed(value: Any, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        _fail(f"addon_observation_{label}_fields_invalid")
    return value


def _integer(value: Any, label: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        _fail(f"addon_observation_{label}_invalid")
    return value


def _token(value: Any, label: str, maximum: int = 80) -> str:
    if not isinstance(value, str) or len(value) > maximum or _TOKEN.fullmatch(value) is None:
        _fail(f"addon_observation_{label}_invalid")
    return value


def _timestamp(value: Any) -> str:
    if not isinstance(value, str) or len(value) > 32 or not value.endswith("Z"):
        _fail("addon_observation_captured_at_invalid")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise AddonObservationTransportError("addon_observation_captured_at_invalid") from exc
    if parsed.utcoffset() is None:
        _fail("addon_observation_captured_at_invalid")
    return value


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _fail("addon_observation_duplicate_json_key")
        result[key] = value
    return result


def _nonfinite(value: str) -> None:
    _fail("addon_observation_nonfinite_number")


def canonical_observation_bytes(document: Mapping[str, Any]) -> bytes:
    try:
        text = json.dumps(document, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))
    except (TypeError, ValueError) as exc:
        raise AddonObservationTransportError("addon_observation_not_canonicalizable") from exc
    return (text + "\n").encode("utf-8")


def _validate(document: Mapping[str, Any], payload_size: int) -> SyntheticAddonObservation:
    root = _closed(dict(document), _ROOT, "root")
    if root["schema_version"] != "0.1":
        _fail("addon_observation_schema_incompatible")
    identity = _closed(root["identity"], _IDENTITY, "identity")
    observation_id = _token(identity["observation_id"], "observation_id")
    captured_at = _timestamp(identity["captured_at"])
    producer = _closed(root["producer"], _PRODUCER, "producer")
    if producer["producer_id"] != "dpslab.addon.synthetic":
        _fail("addon_observation_producer_unsupported")
    _token(producer["producer_version"], "producer_version", 24)
    compatibility = _closed(root["compatibility"], _COMPATIBILITY, "compatibility")
    if compatibility["wow_product"] != "retail":
        _fail("addon_observation_product_unsupported")
    build = _integer(compatibility["build"], "build", 1, 999999)
    interface_version = _integer(compatibility["interface_version"], "interface", 1, 999999)
    subject = _closed(root["subject"], _SUBJECT, "subject")
    if subject["synthetic"] is not True:
        _fail("addon_observation_subject_not_synthetic")
    class_token = _token(subject["class_token"], "class_token", 40)
    specialization_token = _token(subject["specialization_token"], "specialization_token", 48)
    if subject["role"] not in {"damage", "tank", "healer"}:
        _fail("addon_observation_role_invalid")
    observation = _closed(root["observation"], _OBSERVATION, "observation")
    if observation["state"] != "synthetic_fixture":
        _fail("addon_observation_state_invalid")
    sample_window = _integer(observation["sample_window_seconds"], "sample_window", 0, 3600)
    event_count = _integer(observation["event_count"], "event_count", 0, 100000)
    byte_count = _integer(observation["byte_count"], "byte_count", 1, MAX_PAYLOAD_BYTES)
    if byte_count != payload_size:
        _fail("addon_observation_byte_count_mismatch")
    signals = _closed(observation["signals"], _SIGNALS, "signals")
    damage = _integer(signals["damage_events"], "damage_events", 0, 100000)
    incoming = _integer(signals["incoming_damage_events"], "incoming_damage_events", 0, 100000)
    healing = _integer(signals["healing_events"], "healing_events", 0, 100000)
    if damage + incoming + healing != event_count:
        _fail("addon_observation_event_count_mismatch")
    safety = _closed(root["safety"], _SAFETY, "safety")
    if safety != {"synthetic": True, "contains_personal_data": False, "executable": False, "actionable": False, "no_automation": True}:
        _fail("addon_observation_safety_invalid")
    return SyntheticAddonObservation(observation_id, captured_at, build, interface_version, class_token, specialization_token, subject["role"], sample_window, damage, incoming, healing)


def parse_synthetic_saved_variable(raw: bytes) -> SyntheticAddonObservation:
    """Parse one exact synthetic assignment without evaluating any Lua."""
    if not isinstance(raw, bytes):
        _fail("addon_observation_transport_bytes_required")
    if len(raw) > 2 * MAX_PAYLOAD_BYTES + 64:
        _fail("addon_observation_transport_too_large")
    match = _ASSIGNMENT.fullmatch(raw)
    if match is None or len(match.group(1)) % 2:
        _fail("addon_observation_assignment_invalid")
    try:
        payload = bytes.fromhex(match.group(1).decode("ascii"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise AddonObservationTransportError("addon_observation_hex_invalid") from exc
    if not 1 <= len(payload) <= MAX_PAYLOAD_BYTES:
        _fail("addon_observation_payload_size_invalid")
    try:
        document = json.loads(payload.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_nonfinite)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AddonObservationTransportError("addon_observation_json_invalid") from exc
    if not isinstance(document, dict):
        _fail("addon_observation_root_invalid")
    validated = _validate(document, len(payload))
    if payload != canonical_observation_bytes(document):
        _fail("addon_observation_json_noncanonical")
    return validated
