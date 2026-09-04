"""Strict parser for a synthetic DpsLab training-dummy session."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib, json
from typing import Any, Mapping

PREFIX = "DPSLAB-SYNTHETIC-TRAINING-0.1\n"
MAX_BYTES = 4096
class TrainingDummySessionTransportError(ValueError): pass
@dataclass(frozen=True, repr=False)
class TrainingDummySession:
    state: str; duration_seconds: int; target_classification: str; action_count: int; resource_cap_count: int; inactivity_seconds: int; receipt_sha256: str
def _fail(reason: str): raise TrainingDummySessionTransportError(reason)
def _integer(value: Any, name: str, low: int, high: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high: _fail(f"training_{name}_invalid")
    return value
def _closed(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys: _fail(f"training_{label}_invalid")
    return value
def _pairs(values):
    result = {}
    for key, value in values:
        if key in result: _fail("training_duplicate_json_key")
        result[key] = value
    return result
def _constant(_: str): _fail("training_nonfinite_number")
def canonical_training_dummy_session_bytes(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
def parse_synthetic_training_dummy_session(text: str) -> TrainingDummySession:
    if not isinstance(text, str) or not text.startswith(PREFIX): _fail("training_prefix_invalid")
    raw = text[len(PREFIX):].encode()
    if not 1 <= len(raw) <= MAX_BYTES: _fail("training_payload_size_invalid")
    try: value = json.loads(raw.decode(), object_pairs_hook=_pairs, parse_constant=_constant)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc: raise TrainingDummySessionTransportError("training_json_invalid") from exc
    root = _closed(value, {"metrics","observation_type","safety","schema_version","state","target_classification","duration_seconds"}, "root")
    if root["schema_version"] != "0.1" or root["observation_type"] != "synthetic_training_dummy_session": _fail("training_schema_incompatible")
    if raw != canonical_training_dummy_session_bytes(value): _fail("training_json_noncanonical")
    if root["state"] not in {"completed", "cancelled", "incomplete"}: _fail("training_state_invalid")
    if root["target_classification"] not in {"confirmed", "unconfirmed_target"}: _fail("training_target_invalid")
    duration = _integer(root["duration_seconds"], "duration_seconds", 0, 900)
    metrics = _closed(root["metrics"], {"action_count","resource_cap_count","inactivity_seconds"}, "metrics")
    action = _integer(metrics["action_count"], "action_count", 0, 100000); cap = _integer(metrics["resource_cap_count"], "resource_cap_count", 0, 100000); idle = _integer(metrics["inactivity_seconds"], "inactivity_seconds", 0, duration)
    safety = _closed(root["safety"], {"executable","no_automation","synthetic"}, "safety")
    if safety != {"synthetic": True, "executable": False, "no_automation": True}: _fail("training_safety_invalid")
    return TrainingDummySession(root["state"], duration, root["target_classification"], action, cap, idle, hashlib.sha256(raw).hexdigest())
