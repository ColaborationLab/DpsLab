"""Pure validation for versioned DpsLab knowledge envelopes."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any, Mapping


class KnowledgeEnvelopeError(ValueError):
    """A knowledge envelope is malformed, incompatible, or unverifiable."""


@dataclass(frozen=True)
class CompatibilityContext:
    wow_product: str
    build: int
    interface: int
    class_id: int
    specialization_id: int
    race_id: int | None
    level: int
    content_context: str
    observed_at: datetime
    character_fingerprint: str | None = None


@dataclass(frozen=True)
class GuidanceSelection:
    status: str
    reason: str | None
    statements: tuple[Mapping[str, Any], ...]


_ROOT_FIELDS = {
    "schema_version",
    "identity",
    "compatibility",
    "subject",
    "guidance",
    "evidence",
    "safety",
    "integrity",
}
_IDENTITY_FIELDS = {
    "package_id",
    "content_version",
    "channel",
    "created_at",
}
_COMPATIBILITY_FIELDS = {
    "wow_product",
    "build_min",
    "build_max",
    "interface_min",
    "interface_max",
    "addon_min",
    "addon_max",
    "desktop_min",
    "desktop_max",
}
_SUBJECT_FIELDS = {
    "class_id",
    "specialization_id",
    "race_ids",
    "level_min",
    "level_max",
    "role",
    "content_contexts",
    "character_fingerprint",
}
_GUIDANCE_FIELDS = {"statements", "unsupported_variables"}
_STATEMENT_FIELDS = {
    "order",
    "type",
    "text_key",
    "prerequisites",
    "alternatives",
}
_EVIDENCE_FIELDS = {
    "tier",
    "source_ids",
    "source_hashes",
    "method",
    "run_count",
    "confidence_interval_percent",
    "expires_at",
    "limitations",
}
_SAFETY_FIELDS = {
    "no_automation",
    "required_warnings",
    "degradation_policy",
    "invalidation_reasons",
}
_INTEGRITY_FIELDS = {
    "payload_sha256",
    "signature_algorithm",
    "signature",
    "publisher_key_id",
}
_TIERS = {
    "static_fallback_template",
    "imported_analytical_evidence",
    "character_observation",
}
_STATEMENT_TYPES = {"priority", "check", "explanation", "alternative"}
_ROLES = {"damage", "tank", "healer"}
_TOKEN = re.compile(r"[a-z0-9][a-z0-9_.:-]{0,127}")
_VERSION = re.compile(r"(?:0|[1-9][0-9]*)(?:\.[0-9]+){0,3}")
_SHA256 = re.compile(r"[0-9a-f]{64}")


def canonical_json_bytes(document: Mapping[str, Any]) -> bytes:
    """Return the one canonical JSON representation used by schema 0.1."""
    try:
        text = json.dumps(
            document,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as exc:
        raise KnowledgeEnvelopeError("knowledge_json_not_canonicalizable") from exc
    return (text + "\n").encode("utf-8")


def unsigned_payload_bytes(document: Mapping[str, Any]) -> bytes:
    """Project an envelope to the exact bytes covered by payload_sha256."""
    projected = deepcopy(dict(document))
    integrity = projected.get("integrity")
    if not isinstance(integrity, dict):
        raise KnowledgeEnvelopeError("knowledge_integrity_invalid")
    if set(integrity) != _INTEGRITY_FIELDS:
        raise KnowledgeEnvelopeError("knowledge_integrity_fields_invalid")
    del integrity["payload_sha256"]
    del integrity["signature"]
    return canonical_json_bytes(projected)


def calculate_payload_sha256(document: Mapping[str, Any]) -> str:
    return sha256(unsigned_payload_bytes(document)).hexdigest()


def _object(value: Any, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        raise KnowledgeEnvelopeError(f"knowledge_{label}_fields_invalid")
    return value


def _integer(value: Any, label: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise KnowledgeEnvelopeError(f"knowledge_{label}_invalid")
    return value


def _text(value: Any, label: str, *, token: bool = False) -> str:
    if not isinstance(value, str) or not value:
        raise KnowledgeEnvelopeError(f"knowledge_{label}_invalid")
    if token and _TOKEN.fullmatch(value) is None:
        raise KnowledgeEnvelopeError(f"knowledge_{label}_invalid")
    return value


def _optional_version(value: Any, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or _VERSION.fullmatch(value) is None:
        raise KnowledgeEnvelopeError(f"knowledge_{label}_invalid")
    return value


def _timestamp(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise KnowledgeEnvelopeError(f"knowledge_{label}_invalid")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise KnowledgeEnvelopeError(f"knowledge_{label}_invalid") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise KnowledgeEnvelopeError(f"knowledge_{label}_invalid")
    return parsed


def _token_list(value: Any, label: str, *, allow_empty: bool = True) -> tuple[str, ...]:
    if not isinstance(value, list) or (not allow_empty and not value):
        raise KnowledgeEnvelopeError(f"knowledge_{label}_invalid")
    result = tuple(_text(item, label, token=True) for item in value)
    if len(result) != len(set(result)):
        raise KnowledgeEnvelopeError(f"knowledge_{label}_duplicate")
    return result


def validate_knowledge_envelope(document: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a closed schema 0.1 envelope and its payload hash."""
    root = _object(dict(document), _ROOT_FIELDS, "root")
    if root["schema_version"] != "0.1":
        raise KnowledgeEnvelopeError("knowledge_schema_version_invalid")

    identity = _object(root["identity"], _IDENTITY_FIELDS, "identity")
    _text(identity["package_id"], "package_id", token=True)
    if _VERSION.fullmatch(_text(identity["content_version"], "content_version")) is None:
        raise KnowledgeEnvelopeError("knowledge_content_version_invalid")
    if identity["channel"] not in {"stable", "beta"}:
        raise KnowledgeEnvelopeError("knowledge_channel_invalid")
    _timestamp(identity["created_at"], "created_at")

    compatibility = _object(
        root["compatibility"], _COMPATIBILITY_FIELDS, "compatibility"
    )
    if compatibility["wow_product"] != "retail":
        raise KnowledgeEnvelopeError("knowledge_wow_product_unsupported")
    build_min = _integer(compatibility["build_min"], "build_min", minimum=1)
    build_max = _integer(compatibility["build_max"], "build_max", minimum=1)
    interface_min = _integer(
        compatibility["interface_min"], "interface_min", minimum=1
    )
    interface_max = _integer(
        compatibility["interface_max"], "interface_max", minimum=1
    )
    if build_min > build_max or interface_min > interface_max:
        raise KnowledgeEnvelopeError("knowledge_compatibility_range_invalid")
    for name in ("addon_min", "addon_max", "desktop_min", "desktop_max"):
        _optional_version(compatibility[name], name)

    subject = _object(root["subject"], _SUBJECT_FIELDS, "subject")
    _integer(subject["class_id"], "class_id", minimum=1)
    _integer(subject["specialization_id"], "specialization_id", minimum=1)
    if subject["race_ids"] is not None:
        races = subject["race_ids"]
        if not isinstance(races, list) or not races:
            raise KnowledgeEnvelopeError("knowledge_race_ids_invalid")
        normalized_races = tuple(
            _integer(item, "race_id", minimum=1) for item in races
        )
        if len(normalized_races) != len(set(normalized_races)):
            raise KnowledgeEnvelopeError("knowledge_race_ids_duplicate")
    level_min = _integer(subject["level_min"], "level_min", minimum=1)
    level_max = _integer(subject["level_max"], "level_max", minimum=1)
    if level_min > level_max:
        raise KnowledgeEnvelopeError("knowledge_level_range_invalid")
    if subject["role"] not in _ROLES:
        raise KnowledgeEnvelopeError("knowledge_role_invalid")
    _token_list(subject["content_contexts"], "content_context", allow_empty=False)
    fingerprint = subject["character_fingerprint"]
    if fingerprint is not None and (
        not isinstance(fingerprint, str) or _SHA256.fullmatch(fingerprint) is None
    ):
        raise KnowledgeEnvelopeError("knowledge_character_fingerprint_invalid")

    guidance = _object(root["guidance"], _GUIDANCE_FIELDS, "guidance")
    statements = guidance["statements"]
    if not isinstance(statements, list) or not statements:
        raise KnowledgeEnvelopeError("knowledge_statements_invalid")
    for expected_order, statement_value in enumerate(statements, 1):
        statement = _object(statement_value, _STATEMENT_FIELDS, "statement")
        if statement["order"] != expected_order:
            raise KnowledgeEnvelopeError("knowledge_statement_order_invalid")
        if statement["type"] not in _STATEMENT_TYPES:
            raise KnowledgeEnvelopeError("knowledge_statement_type_invalid")
        _text(statement["text_key"], "statement_text_key", token=True)
        _token_list(statement["prerequisites"], "prerequisite")
        _token_list(statement["alternatives"], "alternative")
    _token_list(guidance["unsupported_variables"], "unsupported_variable")

    evidence = _object(root["evidence"], _EVIDENCE_FIELDS, "evidence")
    tier = evidence["tier"]
    if tier not in _TIERS:
        raise KnowledgeEnvelopeError("knowledge_evidence_tier_invalid")
    source_ids = _token_list(evidence["source_ids"], "source_id")
    hashes = evidence["source_hashes"]
    if not isinstance(hashes, dict):
        raise KnowledgeEnvelopeError("knowledge_source_hashes_invalid")
    for key, value in hashes.items():
        _text(key, "source_hash_key", token=True)
        if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
            raise KnowledgeEnvelopeError("knowledge_source_hash_invalid")
    method = evidence["method"]
    if method is not None:
        _text(method, "evidence_method", token=True)
    run_count = evidence["run_count"]
    if run_count is not None:
        _integer(run_count, "run_count", minimum=1)
    interval = evidence["confidence_interval_percent"]
    if interval is not None:
        if (
            not isinstance(interval, list)
            or len(interval) != 2
            or any(isinstance(item, bool) or not isinstance(item, (int, float)) for item in interval)
            or interval[0] > interval[1]
        ):
            raise KnowledgeEnvelopeError("knowledge_confidence_interval_invalid")
    if tier == "imported_analytical_evidence" and (
        method is None
        or run_count is None
        or interval is None
        or not hashes
        or not source_ids
    ):
        raise KnowledgeEnvelopeError("knowledge_imported_evidence_incomplete")
    if tier == "static_fallback_template" and (
        method is not None or run_count is not None or interval is not None
    ):
        raise KnowledgeEnvelopeError("knowledge_static_evidence_overclaimed")
    _timestamp(evidence["expires_at"], "expires_at")
    if not isinstance(evidence["limitations"], list) or not evidence["limitations"]:
        raise KnowledgeEnvelopeError("knowledge_limitations_invalid")
    for limitation in evidence["limitations"]:
        _text(limitation, "limitation", token=True)

    safety = _object(root["safety"], _SAFETY_FIELDS, "safety")
    if safety["no_automation"] is not True:
        raise KnowledgeEnvelopeError("knowledge_no_automation_required")
    _token_list(safety["required_warnings"], "required_warning", allow_empty=False)
    if safety["degradation_policy"] != "fail_closed":
        raise KnowledgeEnvelopeError("knowledge_degradation_policy_invalid")
    _token_list(safety["invalidation_reasons"], "invalidation_reason")

    integrity = _object(root["integrity"], _INTEGRITY_FIELDS, "integrity")
    payload_hash = integrity["payload_sha256"]
    if not isinstance(payload_hash, str) or _SHA256.fullmatch(payload_hash) is None:
        raise KnowledgeEnvelopeError("knowledge_payload_sha256_invalid")
    if integrity["signature_algorithm"] != "placeholder-none":
        raise KnowledgeEnvelopeError("knowledge_signature_algorithm_invalid")
    if integrity["signature"] is not None:
        raise KnowledgeEnvelopeError("knowledge_signature_must_be_null")
    _text(integrity["publisher_key_id"], "publisher_key_id", token=True)
    if calculate_payload_sha256(root) != payload_hash:
        raise KnowledgeEnvelopeError("knowledge_payload_sha256_mismatch")
    return deepcopy(root)


def load_knowledge_envelope(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
        document = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise KnowledgeEnvelopeError("knowledge_envelope_load_failed") from exc
    if not isinstance(document, dict):
        raise KnowledgeEnvelopeError("knowledge_root_invalid")
    validated = validate_knowledge_envelope(document)
    if raw != canonical_json_bytes(validated):
        raise KnowledgeEnvelopeError("knowledge_envelope_bytes_noncanonical")
    return validated


def select_guidance(
    document: Mapping[str, Any],
    context: CompatibilityContext,
) -> GuidanceSelection:
    """Return guidance only when every compatibility condition is satisfied."""
    envelope = validate_knowledge_envelope(document)
    compatibility = envelope["compatibility"]
    subject = envelope["subject"]
    evidence = envelope["evidence"]
    if context.wow_product != "retail":
        return GuidanceSelection("guidance_unavailable", "wow_product", ())
    for field in ("build", "interface", "class_id", "specialization_id", "level"):
        value = getattr(context, field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise KnowledgeEnvelopeError(f"knowledge_context_{field}_invalid")
    if context.race_id is not None and (
        isinstance(context.race_id, bool)
        or not isinstance(context.race_id, int)
        or context.race_id < 1
    ):
        raise KnowledgeEnvelopeError("knowledge_context_race_id_invalid")
    _text(context.content_context, "context_content_context", token=True)
    if not isinstance(context.observed_at, datetime) or context.observed_at.tzinfo is None:
        raise KnowledgeEnvelopeError("knowledge_observed_at_invalid")
    try:
        observed_offset = context.observed_at.utcoffset()
    except (ValueError, OverflowError) as exc:
        raise KnowledgeEnvelopeError("knowledge_observed_at_invalid") from exc
    if observed_offset is None:
        raise KnowledgeEnvelopeError("knowledge_observed_at_invalid")
    if context.character_fingerprint is not None and (
        not isinstance(context.character_fingerprint, str)
        or _SHA256.fullmatch(context.character_fingerprint) is None
    ):
        raise KnowledgeEnvelopeError("knowledge_context_character_fingerprint_invalid")
    if evidence["tier"] == "character_observation":
        return GuidanceSelection(
            "guidance_unavailable", "evidence_tier_reserved", ()
        )
    if not compatibility["build_min"] <= context.build <= compatibility["build_max"]:
        return GuidanceSelection("guidance_unavailable", "build", ())
    if not (
        compatibility["interface_min"]
        <= context.interface
        <= compatibility["interface_max"]
    ):
        return GuidanceSelection("guidance_unavailable", "interface", ())
    if context.class_id != subject["class_id"]:
        return GuidanceSelection("guidance_unavailable", "class", ())
    if context.specialization_id != subject["specialization_id"]:
        return GuidanceSelection("guidance_unavailable", "specialization", ())
    if not subject["level_min"] <= context.level <= subject["level_max"]:
        return GuidanceSelection("guidance_unavailable", "level", ())
    if context.content_context not in subject["content_contexts"]:
        return GuidanceSelection("guidance_unavailable", "content_context", ())
    race_ids = subject["race_ids"]
    if race_ids is not None and context.race_id not in race_ids:
        return GuidanceSelection("guidance_unavailable", "race", ())
    fingerprint = subject["character_fingerprint"]
    if fingerprint is not None and context.character_fingerprint != fingerprint:
        return GuidanceSelection(
            "guidance_unavailable", "character_fingerprint", ()
        )
    observed_at = context.observed_at
    try:
        normalized = observed_at.astimezone(timezone.utc)
    except (ValueError, OverflowError) as exc:
        raise KnowledgeEnvelopeError("knowledge_observed_at_invalid") from exc
    if normalized >= _timestamp(evidence["expires_at"], "expires_at"):
        return GuidanceSelection("guidance_unavailable", "expired", ())
    return GuidanceSelection(
        "guidance_available",
        None,
        tuple(deepcopy(envelope["guidance"]["statements"])),
    )
