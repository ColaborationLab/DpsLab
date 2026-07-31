"""Pure, fail-closed validation for the synthetic static-template catalog."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any, Mapping

from .knowledge_envelope import (
    CompatibilityContext,
    KnowledgeEnvelopeError,
    canonical_json_bytes,
    load_knowledge_envelope,
    select_guidance,
)


class StaticTemplateCatalogError(ValueError):
    """The catalog is malformed, ambiguous, stale, or unverifiable."""


@dataclass(frozen=True)
class ApprovalEvidence:
    catalog_id: str
    catalog_content_version: str
    entry_id: str
    package_id: str
    envelope_sha256: str
    decision: str
    decision_id: str
    reviewer_id: str
    decided_at: datetime


@dataclass(frozen=True)
class CatalogSelection:
    status: str
    reason: str | None
    entry_id: str | None
    statements: tuple[Mapping[str, Any], ...]


_ROOT_FIELDS = {"catalog_version", "identity", "entries", "integrity"}
_IDENTITY_FIELDS = {"catalog_id", "content_version", "channel", "created_at"}
_INTEGRITY_FIELDS = {"catalog_sha256", "hash_algorithm"}
_ENTRY_FIELDS = {
    "entry_id", "envelope_path", "envelope_sha256", "index",
    "lifecycle_state", "review", "supersedes_entry_ids",
    "invalidation_reasons", "source_coverage_complete", "role_policy",
}
_INDEX_FIELDS = {
    "wow_product", "build_min", "build_max", "interface_min", "interface_max",
    "class_id", "specialization_id", "race_ids", "level_min", "level_max",
    "role", "content_contexts",
}
_REVIEW_FIELDS = {
    "decision_id", "reviewer_id", "decided_at", "notes",
    "prior_approval_decision_id", "transition_reason",
}
_ROLE_POLICY_FIELDS = {"policy_id", "dynamic_safety_satisfied"}
_STATES = {"draft", "pending_review", "approved", "rejected", "deprecated", "withdrawn"}
_ROLES = {"damage", "tank", "healer"}
_TOKEN = re.compile(r"[a-z0-9][a-z0-9_.:-]{0,127}")
_VERSION = re.compile(r"(?:0|[1-9][0-9]*)(?:\.[0-9]+){0,3}")
_SHA256 = re.compile(r"[0-9a-f]{64}")


def _fail(reason: str) -> None:
    raise StaticTemplateCatalogError(f"catalog_{reason}")


def _object(value: Any, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        _fail(f"{label}_fields_invalid")
    return value


def _token(value: Any, label: str) -> str:
    if not isinstance(value, str) or _TOKEN.fullmatch(value) is None:
        _fail(f"{label}_invalid")
    return value


def _timestamp(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        _fail(f"{label}_invalid")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        _fail(f"{label}_invalid")
    if parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        _fail(f"{label}_invalid")
    return parsed


def _tokens(value: Any, label: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        _fail(f"{label}_invalid")
    result = tuple(_token(item, label) for item in value)
    if len(result) != len(set(result)):
        _fail(f"{label}_duplicate")
    return result


def canonical_catalog_bytes(document: Mapping[str, Any]) -> bytes:
    try:
        return canonical_json_bytes(document)
    except KnowledgeEnvelopeError as exc:
        raise StaticTemplateCatalogError("catalog_json_not_canonicalizable") from exc


def unsigned_catalog_bytes(document: Mapping[str, Any]) -> bytes:
    projected = deepcopy(dict(document))
    integrity = projected.get("integrity")
    if not isinstance(integrity, dict) or set(integrity) != _INTEGRITY_FIELDS:
        _fail("integrity_fields_invalid")
    del integrity["catalog_sha256"]
    return canonical_catalog_bytes(projected)


def calculate_catalog_sha256(document: Mapping[str, Any]) -> str:
    return sha256(unsigned_catalog_bytes(document)).hexdigest()


def _validate_review(state: str, review: dict[str, Any]) -> None:
    notes = _tokens(review["notes"], "review_note")
    del notes
    final = (review["decision_id"], review["reviewer_id"], review["decided_at"])
    if state in {"draft", "pending_review"}:
        if any(value is not None for value in final) or review["prior_approval_decision_id"] is not None or review["transition_reason"] is not None:
            _fail("review_state_contradiction")
        return
    if any(value is None for value in final):
        _fail("review_state_contradiction")
    _token(review["decision_id"], "decision_id")
    _token(review["reviewer_id"], "reviewer_id")
    _timestamp(review["decided_at"], "decided_at")
    prior = review["prior_approval_decision_id"]
    reason = review["transition_reason"]
    if state == "approved" and (prior is not None or reason is not None):
        _fail("review_state_contradiction")
    if state == "rejected" and (prior is not None or reason is None):
        _fail("review_state_contradiction")
    if state in {"deprecated", "withdrawn"} and (prior is None or reason is None):
        _fail("review_state_contradiction")
    if prior is not None:
        _token(prior, "prior_approval_decision_id")
    if reason is not None:
        _token(reason, "transition_reason")


def _validate_path(value: Any) -> str:
    if not isinstance(value, str) or "\\" in value:
        _fail("envelope_path_invalid")
    path = PurePosixPath(value)
    if path.is_absolute() or path.suffix != ".json" or ".." in path.parts:
        _fail("envelope_path_invalid")
    if len(path.parts) != 3 or path.parts[:2] != ("knowledge", "fixtures"):
        _fail("envelope_path_outside_fixture_root")
    return value


def _validate_entry(entry_value: Any) -> dict[str, Any]:
    entry = _object(entry_value, _ENTRY_FIELDS, "entry")
    _token(entry["entry_id"], "entry_id")
    _validate_path(entry["envelope_path"])
    if not isinstance(entry["envelope_sha256"], str) or _SHA256.fullmatch(entry["envelope_sha256"]) is None:
        _fail("envelope_sha256_invalid")
    index = _object(entry["index"], _INDEX_FIELDS, "index")
    if index["wow_product"] != "retail" or index["role"] not in _ROLES:
        _fail("index_subject_invalid")
    for name in ("build_min", "build_max", "interface_min", "interface_max", "class_id", "specialization_id", "level_min", "level_max"):
        if isinstance(index[name], bool) or not isinstance(index[name], int) or index[name] < 1:
            _fail(f"index_{name}_invalid")
    if index["build_min"] > index["build_max"] or index["interface_min"] > index["interface_max"] or index["level_min"] > index["level_max"]:
        _fail("index_range_invalid")
    if index["race_ids"] is not None:
        races = index["race_ids"]
        if not isinstance(races, list) or not races or any(isinstance(x, bool) or not isinstance(x, int) or x < 1 for x in races) or len(races) != len(set(races)):
            _fail("index_race_ids_invalid")
    if not _tokens(index["content_contexts"], "content_context"):
        _fail("content_context_invalid")
    state = entry["lifecycle_state"]
    if state not in _STATES:
        _fail("lifecycle_state_invalid")
    _validate_review(state, _object(entry["review"], _REVIEW_FIELDS, "review"))
    _tokens(entry["supersedes_entry_ids"], "supersedes_entry_id")
    _tokens(entry["invalidation_reasons"], "invalidation_reason")
    if not isinstance(entry["source_coverage_complete"], bool):
        _fail("source_coverage_complete_invalid")
    policy = _object(entry["role_policy"], _ROLE_POLICY_FIELDS, "role_policy")
    if policy["policy_id"] != f"{index['role']}.safety_first.0_1":
        _fail("role_policy_mismatch")
    if not isinstance(policy["dynamic_safety_satisfied"], bool):
        _fail("dynamic_safety_invalid")
    return entry


def validate_static_template_catalog(document: Mapping[str, Any]) -> dict[str, Any]:
    root = _object(dict(document), _ROOT_FIELDS, "root")
    if root["catalog_version"] != "0.1":
        _fail("version_invalid")
    identity = _object(root["identity"], _IDENTITY_FIELDS, "identity")
    _token(identity["catalog_id"], "catalog_id")
    if not isinstance(identity["content_version"], str) or _VERSION.fullmatch(identity["content_version"]) is None:
        _fail("content_version_invalid")
    if identity["channel"] not in {"stable", "beta"}:
        _fail("channel_invalid")
    _timestamp(identity["created_at"], "created_at")
    entries = root["entries"]
    if not isinstance(entries, list) or not entries:
        _fail("entries_invalid")
    validated = [_validate_entry(item) for item in entries]
    entry_ids = [item["entry_id"] for item in validated]
    if len(entry_ids) != len(set(entry_ids)):
        _fail("entry_id_duplicate")
    approved_dimensions: set[str] = set()
    for entry in validated:
        if entry["lifecycle_state"] == "approved":
            dimensions = json.dumps(entry["index"], sort_keys=True, separators=(",", ":"))
            if dimensions in approved_dimensions:
                _fail("approved_entry_overlap")
            approved_dimensions.add(dimensions)
    for entry in validated:
        supersedes = set(entry["supersedes_entry_ids"])
        if entry["entry_id"] in supersedes or not supersedes.issubset(set(entry_ids)):
            _fail("supersession_invalid")
    graph = {item["entry_id"]: item["supersedes_entry_ids"] for item in validated}
    def visit(node: str, trail: set[str]) -> None:
        if node in trail:
            _fail("supersession_cycle")
        for target in graph[node]:
            visit(target, trail | {node})
    for node in graph:
        visit(node, set())
    integrity = _object(root["integrity"], _INTEGRITY_FIELDS, "integrity")
    if integrity["hash_algorithm"] != "sha256":
        _fail("hash_algorithm_invalid")
    if not isinstance(integrity["catalog_sha256"], str) or _SHA256.fullmatch(integrity["catalog_sha256"]) is None:
        _fail("sha256_invalid")
    if calculate_catalog_sha256(root) != integrity["catalog_sha256"]:
        _fail("sha256_mismatch")
    return deepcopy(root)


def load_static_template_catalog(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
        document = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise StaticTemplateCatalogError("catalog_load_failed") from exc
    if not isinstance(document, dict):
        _fail("root_fields_invalid")
    validated = validate_static_template_catalog(document)
    if raw != canonical_catalog_bytes(validated):
        _fail("bytes_noncanonical")
    return validated


def _index_matches(entry: Mapping[str, Any], envelope: Mapping[str, Any]) -> bool:
    index = entry["index"]
    compatibility = envelope["compatibility"]
    subject = envelope["subject"]
    expected = {
        "wow_product": compatibility["wow_product"], "build_min": compatibility["build_min"],
        "build_max": compatibility["build_max"], "interface_min": compatibility["interface_min"],
        "interface_max": compatibility["interface_max"], "class_id": subject["class_id"],
        "specialization_id": subject["specialization_id"], "race_ids": subject["race_ids"],
        "level_min": subject["level_min"], "level_max": subject["level_max"],
        "role": subject["role"], "content_contexts": subject["content_contexts"],
    }
    return index == expected


def select_catalog_guidance(
    catalog: Mapping[str, Any], repository_root: Path,
    context: CompatibilityContext, approval: ApprovalEvidence | None,
) -> CatalogSelection:
    validated = validate_static_template_catalog(catalog)
    candidates: list[tuple[dict[str, Any], dict[str, Any]]] = []
    package_ids: set[str] = set()
    for entry in validated["entries"]:
        envelope_path = repository_root / PurePosixPath(entry["envelope_path"])
        try:
            raw = envelope_path.read_bytes()
            envelope = load_knowledge_envelope(envelope_path)
        except (OSError, KnowledgeEnvelopeError) as exc:
            raise StaticTemplateCatalogError("catalog_envelope_invalid") from exc
        if sha256(raw).hexdigest() != entry["envelope_sha256"]:
            _fail("envelope_sha256_mismatch")
        package_id = envelope["identity"]["package_id"]
        if package_id in package_ids:
            _fail("package_id_duplicate")
        package_ids.add(package_id)
        if not _index_matches(entry, envelope):
            _fail("index_envelope_mismatch")
        if envelope["evidence"]["tier"] != "static_fallback_template":
            continue
        if entry["lifecycle_state"] != "approved" or entry["invalidation_reasons"] or not entry["source_coverage_complete"]:
            continue
        if entry["index"]["role"] in {"tank", "healer"} and not entry["role_policy"]["dynamic_safety_satisfied"]:
            continue
        selected = select_guidance(envelope, context)
        if selected.status == "guidance_available":
            candidates.append((entry, envelope))
    if not candidates:
        return CatalogSelection("guidance_unavailable", "no_eligible_entry", None, ())
    if len(candidates) != 1:
        return CatalogSelection("guidance_unavailable", "ambiguous_entries", None, ())
    entry, envelope = candidates[0]
    if approval is None:
        return CatalogSelection("guidance_unavailable", "approval_missing", None, ())
    expected = (
        validated["identity"]["catalog_id"], validated["identity"]["content_version"],
        entry["entry_id"], envelope["identity"]["package_id"], entry["envelope_sha256"], "approved",
    )
    actual = (
        approval.catalog_id, approval.catalog_content_version, approval.entry_id,
        approval.package_id, approval.envelope_sha256, approval.decision,
    )
    review = entry["review"]
    if (
        actual != expected
        or approval.decision_id != review["decision_id"]
        or approval.reviewer_id != review["reviewer_id"]
        or not approval.decision_id
        or not approval.reviewer_id
    ):
        return CatalogSelection("guidance_unavailable", "approval_mismatch", None, ())
    if (
        not isinstance(approval.decided_at, datetime)
        or approval.decided_at.tzinfo is None
        or approval.decided_at.utcoffset() != timezone.utc.utcoffset(approval.decided_at)
        or approval.decided_at != _timestamp(review["decided_at"], "decided_at")
    ):
        return CatalogSelection("guidance_unavailable", "approval_mismatch", None, ())
    result = select_guidance(envelope, context)
    return CatalogSelection(result.status, result.reason, entry["entry_id"], result.statements)
