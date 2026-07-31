"""Deterministic conversion of a closed structured patch dialect."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import hashlib
import json
import re
from typing import Any, Mapping

from .patch_evidence import calculate_evidence_sha256, validate_patch_evidence


class PatchFormatError(ValueError):
    pass


_TOKEN = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
_SHA = re.compile(r"^[0-9a-f]{64}$")
_ROOT = {"schema_version", "identity", "source", "changes", "integrity"}
_IDENTITY = {"input_id", "created_at", "lifecycle"}
_SOURCE = {"source_owner", "source_family", "source_revision", "published_at", "captured_at", "media_type", "content_sha256", "acquisition_class", "license_class", "authenticity_class", "wow_product", "build_min", "build_max", "interface_min", "interface_max", "supersedes_evidence_id"}
_CHANGE = {"change_id", "semantic_kind", "operation", "subject_tokens", "old_token", "new_token", "citation_token", "certainty", "invalidation_kinds"}
_INTEGRITY = {"hash_algorithm", "input_sha256"}


def _fail(reason: str) -> None:
    raise PatchFormatError(reason)


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
        return datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise PatchFormatError(f"{label}_invalid") from exc


def canonical_input_bytes(document: Mapping[str, Any]) -> bytes:
    return (json.dumps(document, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def calculate_input_sha256(document: Mapping[str, Any]) -> str:
    projection = deepcopy(dict(document)); projection["integrity"]["input_sha256"] = ""
    return hashlib.sha256(canonical_input_bytes(projection)).hexdigest()


def validate_structured_patch_input(document: Mapping[str, Any]) -> dict[str, Any]:
    root = _closed(dict(document), _ROOT, "root")
    if root["schema_version"] != "0.1": _fail("schema_version_invalid")
    identity = _closed(root["identity"], _IDENTITY, "identity")
    _token(identity["input_id"], "input_id")
    created = _timestamp(identity["created_at"], "created_at")
    if identity["lifecycle"] not in {"current", "historical"}: _fail("lifecycle_invalid")
    source = _closed(root["source"], _SOURCE, "source")
    for field in ("source_owner", "source_family", "source_revision"): _token(source[field], field)
    published = _timestamp(source["published_at"], "published_at")
    captured = _timestamp(source["captured_at"], "captured_at")
    if published > captured or captured > created: _fail("timestamp_order_invalid")
    if source["media_type"] not in {"structured_patch_note", "structured_hotfix"}: _fail("media_type_invalid")
    if source["acquisition_class"] not in {"manual", "injected_adapter"}: _fail("acquisition_class_invalid")
    if source["license_class"] not in {"first_party_reference", "permitted_derived_use"}: _fail("license_class_invalid")
    if source["authenticity_class"] not in {"human_attested", "adapter_verified"}: _fail("authenticity_class_invalid")
    if source["supersedes_evidence_id"] is not None:
        _token(source["supersedes_evidence_id"], "supersedes_evidence_id")
        if source["supersedes_evidence_id"] == identity["input_id"]: _fail("self_supersession_invalid")
    if source["wow_product"] != "retail": _fail("wow_product_invalid")
    if not isinstance(source["content_sha256"], str) or _SHA.fullmatch(source["content_sha256"]) is None: _fail("content_sha256_invalid")
    for field in ("build_min", "build_max", "interface_min", "interface_max"):
        if isinstance(source[field], bool) or not isinstance(source[field], int) or source[field] < 0: _fail(f"{field}_invalid")
    if source["build_min"] > source["build_max"] or source["interface_min"] > source["interface_max"]: _fail("range_invalid")
    if not isinstance(root["changes"], list): _fail("changes_invalid")
    ids: set[str] = set(); targets: set[tuple[str, tuple[str, ...]]] = set()
    for raw in root["changes"]:
        change = _closed(raw, _CHANGE, "change")
        change_id = _token(change["change_id"], "change_id")
        kind = _token(change["semantic_kind"], "semantic_kind")
        if change_id in ids: _fail("change_id_duplicate")
        ids.add(change_id)
        if change["operation"] not in {"add", "change", "remove", "invalidate"}: _fail("operation_invalid")
        if not isinstance(change["subject_tokens"], list) or not change["subject_tokens"]: _fail("subject_tokens_invalid")
        subjects = tuple(_token(value, "subject_token") for value in change["subject_tokens"])
        target = (kind, subjects)
        if target in targets: _fail("change_conflict")
        targets.add(target)
        for field in ("old_token", "new_token"):
            if change[field] is not None: _token(change[field], field)
        _token(change["citation_token"], "citation_token")
        if change["certainty"] not in {"exact", "ambiguous"}: _fail("certainty_invalid")
        if not isinstance(change["invalidation_kinds"], list): _fail("invalidation_kinds_invalid")
        for value in change["invalidation_kinds"]: _token(value, "invalidation_kind")
    integrity = _closed(root["integrity"], _INTEGRITY, "integrity")
    if integrity["hash_algorithm"] != "sha256" or not isinstance(integrity["input_sha256"], str) or _SHA.fullmatch(integrity["input_sha256"]) is None: _fail("integrity_invalid")
    if calculate_input_sha256(root) != integrity["input_sha256"]: _fail("input_sha256_mismatch")
    return deepcopy(root)


def convert_structured_patch(document: Mapping[str, Any], semantic_mapping: Mapping[str, str]) -> dict[str, Any]:
    value = validate_structured_patch_input(document)
    if not isinstance(semantic_mapping, Mapping) or not semantic_mapping: _fail("semantic_mapping_invalid")
    mapping: dict[str, str] = {}
    for kind, family in semantic_mapping.items(): mapping[_token(kind, "mapping_kind")] = _token(family, "mapping_family")
    assertions = []
    for change in value["changes"]:
        if change["semantic_kind"] not in mapping: _fail("semantic_kind_unknown")
        if change["certainty"] != "exact": _fail("ambiguous_change")
        invalidations = []
        for kind in change["invalidation_kinds"]:
            if kind not in mapping: _fail("invalidation_kind_unknown")
            invalidations.append(mapping[kind])
        assertions.append({
            "assertion_id": change["change_id"], "parameter_family_id": mapping[change["semantic_kind"]],
            "operation": change["operation"], "subject_tokens": sorted(change["subject_tokens"]),
            "old_token": change["old_token"], "new_token": change["new_token"],
            "citation_token": change["citation_token"], "certainty": change["certainty"],
            "invalidation_families": sorted(set(invalidations)),
        })
    source = deepcopy(value["source"])
    evidence = {"schema_version":"0.1", "identity":{"evidence_id":value["identity"]["input_id"], "created_at":value["identity"]["created_at"], "lifecycle":value["identity"]["lifecycle"]}, "source":source, "assertions":sorted(assertions, key=lambda item:item["assertion_id"]), "integrity":{"hash_algorithm":"sha256", "evidence_sha256":""}}
    evidence["integrity"]["evidence_sha256"] = calculate_evidence_sha256(evidence)
    try:
        return validate_patch_evidence(evidence)
    except ValueError as exc:
        raise PatchFormatError("evidence_handoff_invalid") from exc
