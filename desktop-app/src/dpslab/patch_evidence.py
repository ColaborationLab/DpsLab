"""Pure, fail-closed intake for injected patch evidence.

This module deliberately does not acquire or parse remote patch notes.  It
validates already captured structured evidence and can only produce review
candidates; it cannot approve or publish knowledge.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import re
from typing import Any, Mapping


class PatchEvidenceError(ValueError):
    pass


@dataclass(frozen=True)
class PatchContext:
    wow_product: str
    build: int
    interface: int


@dataclass(frozen=True)
class PatchIntakeResult:
    status: str
    reason: str | None
    candidate_ids: tuple[str, ...]
    invalidated_families: tuple[str, ...]


_TOKEN = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
_SHA = re.compile(r"^[0-9a-f]{64}$")
_ROOT = {"schema_version", "identity", "source", "assertions", "integrity"}
_IDENTITY = {"evidence_id", "created_at", "lifecycle"}
_SOURCE = {
    "source_owner", "source_family", "source_revision", "published_at",
    "captured_at", "media_type", "content_sha256", "acquisition_class",
    "license_class", "authenticity_class", "wow_product", "build_min",
    "build_max", "interface_min", "interface_max", "supersedes_evidence_id",
}
_ASSERTION = {
    "assertion_id", "parameter_family_id", "operation", "subject_tokens",
    "old_token", "new_token", "citation_token", "certainty",
    "invalidation_families",
}
_INTEGRITY = {"hash_algorithm", "evidence_sha256"}


def _fail(reason: str) -> None:
    raise PatchEvidenceError(reason)


def _closed(value: Any, fields: set[str], label: str) -> dict[str, Any]:
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
    except ValueError as exc:
        raise PatchEvidenceError(f"{label}_invalid") from exc
    return parsed


def canonical_patch_bytes(document: Mapping[str, Any]) -> bytes:
    return (json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def calculate_evidence_sha256(document: Mapping[str, Any]) -> str:
    projection = deepcopy(dict(document))
    projection["integrity"]["evidence_sha256"] = ""
    return hashlib.sha256(canonical_patch_bytes(projection)).hexdigest()


def validate_patch_evidence(document: Mapping[str, Any]) -> dict[str, Any]:
    root = _closed(dict(document), _ROOT, "root")
    if root["schema_version"] != "0.1":
        _fail("schema_version_invalid")
    identity = _closed(root["identity"], _IDENTITY, "identity")
    _token(identity["evidence_id"], "evidence_id")
    _timestamp(identity["created_at"], "created_at")
    if identity["lifecycle"] not in {"current", "historical"}:
        _fail("lifecycle_invalid")
    source = _closed(root["source"], _SOURCE, "source")
    for field in ("source_owner", "source_family", "source_revision"):
        _token(source[field], field)
    published = _timestamp(source["published_at"], "published_at")
    captured = _timestamp(source["captured_at"], "captured_at")
    created = _timestamp(identity["created_at"], "created_at")
    if published > captured or captured > created:
        _fail("timestamp_order_invalid")
    if source["media_type"] not in {"structured_patch_note", "structured_hotfix"}:
        _fail("media_type_invalid")
    if source["acquisition_class"] not in {"manual", "injected_adapter"}:
        _fail("acquisition_class_invalid")
    if source["license_class"] not in {"first_party_reference", "permitted_derived_use"}:
        _fail("license_class_invalid")
    if source["authenticity_class"] not in {"human_attested", "adapter_verified"}:
        _fail("authenticity_class_invalid")
    if source["wow_product"] != "retail" or not isinstance(source["content_sha256"], str) or _SHA.fullmatch(source["content_sha256"]) is None:
        _fail("source_identity_invalid")
    for field in ("build_min", "build_max", "interface_min", "interface_max"):
        if isinstance(source[field], bool) or not isinstance(source[field], int) or source[field] < 0:
            _fail(f"{field}_invalid")
    if source["build_min"] > source["build_max"] or source["interface_min"] > source["interface_max"]:
        _fail("source_range_invalid")
    if source["supersedes_evidence_id"] is not None:
        _token(source["supersedes_evidence_id"], "supersedes_evidence_id")
        if source["supersedes_evidence_id"] == identity["evidence_id"]:
            _fail("self_supersession_invalid")
    assertions = root["assertions"]
    if not isinstance(assertions, list):
        _fail("assertions_invalid")
    ids: set[str] = set()
    family_operations: set[tuple[str, str]] = set()
    for raw in assertions:
        item = _closed(raw, _ASSERTION, "assertion")
        assertion_id = _token(item["assertion_id"], "assertion_id")
        family = _token(item["parameter_family_id"], "parameter_family_id")
        if assertion_id in ids:
            _fail("assertion_id_duplicate")
        ids.add(assertion_id)
        if item["operation"] not in {"add", "change", "remove", "invalidate"}:
            _fail("operation_invalid")
        if not isinstance(item["subject_tokens"], list) or not item["subject_tokens"]:
            _fail("subject_tokens_invalid")
        for value in item["subject_tokens"]:
            _token(value, "subject_token")
        key = (family, "|".join(item["subject_tokens"]))
        if key in family_operations:
            _fail("assertion_conflict")
        family_operations.add(key)
        for field in ("old_token", "new_token"):
            if item[field] is not None:
                _token(item[field], field)
        if item["operation"] == "add" and (item["old_token"] is not None or item["new_token"] is None):
            _fail("assertion_value_invalid")
        if item["operation"] == "remove" and (item["old_token"] is None or item["new_token"] is not None):
            _fail("assertion_value_invalid")
        if item["operation"] == "change" and (item["old_token"] is None or item["new_token"] is None or item["old_token"] == item["new_token"]):
            _fail("assertion_value_invalid")
        if item["operation"] == "invalidate" and (item["old_token"] is not None or item["new_token"] is not None):
            _fail("assertion_value_invalid")
        _token(item["citation_token"], "citation_token")
        if item["certainty"] not in {"exact", "ambiguous"}:
            _fail("certainty_invalid")
        if not isinstance(item["invalidation_families"], list):
            _fail("invalidation_families_invalid")
        for value in item["invalidation_families"]:
            _token(value, "invalidation_family")
    integrity = _closed(root["integrity"], _INTEGRITY, "integrity")
    if integrity["hash_algorithm"] != "sha256" or not isinstance(integrity["evidence_sha256"], str) or _SHA.fullmatch(integrity["evidence_sha256"]) is None:
        _fail("integrity_invalid")
    if calculate_evidence_sha256(root) != integrity["evidence_sha256"]:
        _fail("evidence_sha256_mismatch")
    return deepcopy(root)


def intake_patch_evidence(document: Mapping[str, Any], context: PatchContext, allowed_families: frozenset[str]) -> PatchIntakeResult:
    value = validate_patch_evidence(document)
    if (context.wow_product != "retail" or isinstance(context.build, bool)
            or not isinstance(context.build, int) or context.build < 0
            or isinstance(context.interface, bool)
            or not isinstance(context.interface, int) or context.interface < 0):
        return PatchIntakeResult("evidence_unavailable", "context_invalid", (), ())
    source = value["source"]
    if not (source["build_min"] <= context.build <= source["build_max"] and source["interface_min"] <= context.interface <= source["interface_max"]):
        return PatchIntakeResult("evidence_unavailable", "build_mismatch", (), ())
    if value["identity"]["lifecycle"] == "historical":
        return PatchIntakeResult("evidence_unavailable", "historical_only", (), ())
    if any(item["certainty"] == "ambiguous" for item in value["assertions"]):
        return PatchIntakeResult("evidence_unavailable", "ambiguous_assertion", (), ())
    referenced_families = {item["parameter_family_id"] for item in value["assertions"]}
    referenced_families.update(family for item in value["assertions"] for family in item["invalidation_families"])
    if not referenced_families <= allowed_families:
        return PatchIntakeResult("evidence_unavailable", "unknown_family", (), ())
    invalidated = sorted({family for item in value["assertions"] for family in item["invalidation_families"]} | {item["parameter_family_id"] for item in value["assertions"] if item["operation"] == "invalidate"})
    if invalidated:
        return PatchIntakeResult("coverage_invalidated", None, (), tuple(invalidated))
    candidates = tuple(sorted(f"{value['identity']['evidence_id']}.{item['assertion_id']}" for item in value["assertions"]))
    if not candidates:
        return PatchIntakeResult("no_relevant_change", None, (), ())
    return PatchIntakeResult("pending_review", None, candidates, ())
