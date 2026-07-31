"""Pure current-coverage and historical-evidence validation for DpsLab."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any, Mapping


class SourceCoverageError(ValueError):
    """Coverage evidence is malformed, ambiguous, or unverifiable."""


@dataclass(frozen=True)
class CoverageContext:
    wow_product: str
    build: int
    interface: int
    class_id: int
    specialization_id: int
    role: str
    content_context: str
    observed_at: datetime


@dataclass(frozen=True)
class CoverageAssessment:
    status: str
    reason: str | None
    current_capture_ids: tuple[str, ...]


@dataclass(frozen=True)
class HistoricalComparison:
    family_id: str
    left_capture_id: str
    left_revision: str
    left_sha256: str
    right_capture_id: str
    right_revision: str
    right_sha256: str
    historical_only: bool = True


_MANIFEST_ROOT = {"schema_version", "identity", "subject", "requirements", "integrity"}
_ARCHIVE_ROOT = {"schema_version", "identity", "captures", "integrity"}
_IDENTITY = {"document_id", "content_version", "created_at"}
_SUBJECT = {"wow_product", "build_min", "build_max", "interface_min", "interface_max", "class_id", "specialization_id", "role", "content_contexts"}
_REQUIREMENT = {"family_id", "source_owner", "source_id", "acquisition_classes", "license_classes", "max_age_seconds", "invalidation_triggers", "role_scope"}
_CAPTURE = {"capture_id", "family_id", "lifecycle", "source_owner", "source_id", "acquisition_class", "license_class", "source_revision", "captured_at", "content_sha256", "wow_product", "build_min", "build_max", "interface_min", "interface_max", "class_id", "specialization_id", "role", "content_contexts", "fact_fingerprint", "invalidation_reasons", "supersedes_capture_id"}
_INTEGRITY_MANIFEST = {"manifest_sha256", "hash_algorithm"}
_INTEGRITY_ARCHIVE = {"archive_sha256", "hash_algorithm"}
_ROLES = {"damage", "tank", "healer"}
_ACQUISITION = {"manual", "first_party_api", "signed_artifact", "reviewed_document_snapshot"}
_LICENSES = {"first_party_public", "permitted_derived_use", "synthetic_only"}
_TOKEN = re.compile(r"[a-z0-9][a-z0-9_.:-]{0,127}")
_VERSION = re.compile(r"(?:0|[1-9][0-9]*)(?:\.[0-9]+){0,3}")
_SHA = re.compile(r"[0-9a-f]{64}")


def _fail(reason: str) -> None:
    raise SourceCoverageError(f"coverage_{reason}")


def _object(value: Any, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        _fail(f"{label}_fields_invalid")
    return value


def _token(value: Any, label: str) -> str:
    if not isinstance(value, str) or _TOKEN.fullmatch(value) is None:
        _fail(f"{label}_invalid")
    return value


def _tokens(value: Any, label: str, *, nonempty: bool = False) -> tuple[str, ...]:
    if not isinstance(value, list) or (nonempty and not value):
        _fail(f"{label}_invalid")
    result = tuple(_token(item, label) for item in value)
    if len(result) != len(set(result)):
        _fail(f"{label}_duplicate")
    return result


def _integer(value: Any, label: str, minimum: int = 1) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
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


def canonical_coverage_bytes(document: Mapping[str, Any]) -> bytes:
    try:
        text = json.dumps(document, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))
    except (TypeError, ValueError) as exc:
        raise SourceCoverageError("coverage_json_not_canonicalizable") from exc
    return (text + "\n").encode("utf-8")


def _unsigned(document: Mapping[str, Any], field: str, fields: set[str]) -> bytes:
    projected = deepcopy(dict(document))
    integrity = projected.get("integrity")
    if not isinstance(integrity, dict) or set(integrity) != fields:
        _fail("integrity_fields_invalid")
    del integrity[field]
    return canonical_coverage_bytes(projected)


def calculate_manifest_sha256(document: Mapping[str, Any]) -> str:
    return sha256(_unsigned(document, "manifest_sha256", _INTEGRITY_MANIFEST)).hexdigest()


def calculate_archive_sha256(document: Mapping[str, Any]) -> str:
    return sha256(_unsigned(document, "archive_sha256", _INTEGRITY_ARCHIVE)).hexdigest()


def _validate_identity(value: Any) -> dict[str, Any]:
    identity = _object(value, _IDENTITY, "identity")
    _token(identity["document_id"], "document_id")
    if not isinstance(identity["content_version"], str) or _VERSION.fullmatch(identity["content_version"]) is None:
        _fail("content_version_invalid")
    _timestamp(identity["created_at"], "created_at")
    return identity


def _validate_subject(value: Any) -> dict[str, Any]:
    subject = _object(value, _SUBJECT, "subject")
    if subject["wow_product"] != "retail" or subject["role"] not in _ROLES:
        _fail("subject_invalid")
    for field in ("build_min", "build_max", "interface_min", "interface_max", "class_id", "specialization_id"):
        _integer(subject[field], field)
    if subject["build_min"] > subject["build_max"] or subject["interface_min"] > subject["interface_max"]:
        _fail("subject_range_invalid")
    _tokens(subject["content_contexts"], "content_context", nonempty=True)
    return subject


def validate_source_coverage_manifest(document: Mapping[str, Any]) -> dict[str, Any]:
    root = _object(dict(document), _MANIFEST_ROOT, "manifest_root")
    if root["schema_version"] != "0.1":
        _fail("manifest_version_invalid")
    _validate_identity(root["identity"])
    _validate_subject(root["subject"])
    requirements = root["requirements"]
    if not isinstance(requirements, list) or not requirements:
        _fail("requirements_invalid")
    families: list[str] = []
    for value in requirements:
        item = _object(value, _REQUIREMENT, "requirement")
        families.append(_token(item["family_id"], "family_id"))
        _token(item["source_owner"], "source_owner")
        _token(item["source_id"], "source_id")
        acquisitions = _tokens(item["acquisition_classes"], "acquisition_class", nonempty=True)
        licenses = _tokens(item["license_classes"], "license_class", nonempty=True)
        if not set(acquisitions) <= _ACQUISITION or not set(licenses) <= _LICENSES:
            _fail("requirement_policy_invalid")
        _integer(item["max_age_seconds"], "max_age_seconds")
        _tokens(item["invalidation_triggers"], "invalidation_trigger")
        if item["role_scope"] not in _ROLES | {"all"}:
            _fail("role_scope_invalid")
    if len(families) != len(set(families)):
        _fail("family_id_duplicate")
    integrity = _object(root["integrity"], _INTEGRITY_MANIFEST, "integrity")
    if integrity["hash_algorithm"] != "sha256" or not isinstance(integrity["manifest_sha256"], str) or _SHA.fullmatch(integrity["manifest_sha256"]) is None:
        _fail("manifest_integrity_invalid")
    if calculate_manifest_sha256(root) != integrity["manifest_sha256"]:
        _fail("manifest_sha256_mismatch")
    return deepcopy(root)


def validate_source_capture_archive(document: Mapping[str, Any]) -> dict[str, Any]:
    root = _object(dict(document), _ARCHIVE_ROOT, "archive_root")
    if root["schema_version"] != "0.1":
        _fail("archive_version_invalid")
    _validate_identity(root["identity"])
    captures = root["captures"]
    if not isinstance(captures, list) or not captures:
        _fail("captures_invalid")
    ids: list[str] = []
    current_families: list[str] = []
    for value in captures:
        item = _object(value, _CAPTURE, "capture")
        ids.append(_token(item["capture_id"], "capture_id"))
        family = _token(item["family_id"], "family_id")
        if item["lifecycle"] not in {"current", "historical"}:
            _fail("capture_lifecycle_invalid")
        if item["lifecycle"] == "current":
            current_families.append(family)
        for field in ("source_owner", "source_id", "source_revision"):
            _token(item[field], field)
        if item["acquisition_class"] not in _ACQUISITION or item["license_class"] not in _LICENSES:
            _fail("capture_policy_invalid")
        _timestamp(item["captured_at"], "captured_at")
        for field in ("content_sha256", "fact_fingerprint"):
            if not isinstance(item[field], str) or _SHA.fullmatch(item[field]) is None:
                _fail(f"{field}_invalid")
        if item["wow_product"] != "retail" or item["role"] not in _ROLES:
            _fail("capture_subject_invalid")
        for field in ("build_min", "build_max", "interface_min", "interface_max", "class_id", "specialization_id"):
            _integer(item[field], field)
        if item["build_min"] > item["build_max"] or item["interface_min"] > item["interface_max"]:
            _fail("capture_range_invalid")
        _tokens(item["content_contexts"], "content_context", nonempty=True)
        _tokens(item["invalidation_reasons"], "invalidation_reason")
        if item["supersedes_capture_id"] is not None:
            _token(item["supersedes_capture_id"], "supersedes_capture_id")
    if len(ids) != len(set(ids)):
        _fail("capture_id_duplicate")
    if len(current_families) != len(set(current_families)):
        _fail("current_family_duplicate")
    known = set(ids)
    for item in captures:
        previous = item["supersedes_capture_id"]
        if previous is not None and (previous not in known or previous == item["capture_id"]):
            _fail("supersession_invalid")
    integrity = _object(root["integrity"], _INTEGRITY_ARCHIVE, "integrity")
    if integrity["hash_algorithm"] != "sha256" or not isinstance(integrity["archive_sha256"], str) or _SHA.fullmatch(integrity["archive_sha256"]) is None:
        _fail("archive_integrity_invalid")
    if calculate_archive_sha256(root) != integrity["archive_sha256"]:
        _fail("archive_sha256_mismatch")
    return deepcopy(root)


def _load(path: Path, validator: Any) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
        document = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SourceCoverageError("coverage_load_failed") from exc
    if not isinstance(document, dict):
        _fail("root_invalid")
    validated = validator(document)
    if raw != canonical_coverage_bytes(validated):
        _fail("bytes_noncanonical")
    return validated


def load_source_coverage_manifest(path: Path) -> dict[str, Any]:
    return _load(path, validate_source_coverage_manifest)


def load_source_capture_archive(path: Path) -> dict[str, Any]:
    return _load(path, validate_source_capture_archive)


def assess_source_coverage(manifest: Mapping[str, Any], archive: Mapping[str, Any], context: CoverageContext) -> CoverageAssessment:
    manifest_value = validate_source_coverage_manifest(manifest)
    archive_value = validate_source_capture_archive(archive)
    subject = manifest_value["subject"]
    if context.wow_product != "retail" or context.role not in _ROLES:
        return CoverageAssessment("coverage_unavailable", "subject", ())
    for field in ("build", "interface", "class_id", "specialization_id"):
        _integer(getattr(context, field), f"context_{field}")
    _token(context.content_context, "context_content_context")
    if not isinstance(context.observed_at, datetime) or context.observed_at.tzinfo is None or context.observed_at.utcoffset() is None:
        _fail("context_observed_at_invalid")
    observed = context.observed_at.astimezone(timezone.utc)
    if not (subject["build_min"] <= context.build <= subject["build_max"] and subject["interface_min"] <= context.interface <= subject["interface_max"]):
        return CoverageAssessment("coverage_unavailable", "unknown_build", ())
    if context.class_id != subject["class_id"] or context.specialization_id != subject["specialization_id"] or context.role != subject["role"] or context.content_context not in subject["content_contexts"]:
        return CoverageAssessment("coverage_unavailable", "subject", ())
    current = {item["family_id"]: item for item in archive_value["captures"] if item["lifecycle"] == "current"}
    used: list[str] = []
    for requirement in manifest_value["requirements"]:
        if requirement["role_scope"] not in {"all", context.role}:
            continue
        capture = current.get(requirement["family_id"])
        if capture is None:
            return CoverageAssessment("coverage_unavailable", "missing_family", tuple(sorted(used)))
        if capture["source_owner"] != requirement["source_owner"] or capture["source_id"] != requirement["source_id"]:
            return CoverageAssessment("coverage_unavailable", "source_identity", tuple(sorted(used)))
        if capture["acquisition_class"] not in requirement["acquisition_classes"] or capture["license_class"] not in requirement["license_classes"]:
            return CoverageAssessment("coverage_unavailable", "source_policy", tuple(sorted(used)))
        if capture["invalidation_reasons"]:
            return CoverageAssessment("coverage_unavailable", "invalidated", tuple(sorted(used)))
        captured = _timestamp(capture["captured_at"], "captured_at")
        if observed < captured or (observed - captured).total_seconds() > requirement["max_age_seconds"]:
            return CoverageAssessment("coverage_unavailable", "stale", tuple(sorted(used)))
        if not (capture["build_min"] <= context.build <= capture["build_max"] and capture["interface_min"] <= context.interface <= capture["interface_max"]):
            return CoverageAssessment("coverage_unavailable", "capture_build", tuple(sorted(used)))
        if capture["class_id"] != context.class_id or capture["specialization_id"] != context.specialization_id or capture["role"] != context.role or context.content_context not in capture["content_contexts"]:
            return CoverageAssessment("coverage_unavailable", "capture_subject", tuple(sorted(used)))
        used.append(capture["capture_id"])
    return CoverageAssessment("pending_review", None, tuple(sorted(used)))


def compare_historical_captures(archive: Mapping[str, Any], left_capture_id: str, right_capture_id: str) -> HistoricalComparison:
    archive_value = validate_source_capture_archive(archive)
    _token(left_capture_id, "left_capture_id")
    _token(right_capture_id, "right_capture_id")
    if left_capture_id == right_capture_id:
        _fail("historical_comparison_same_capture")
    by_id = {item["capture_id"]: item for item in archive_value["captures"]}
    if left_capture_id not in by_id or right_capture_id not in by_id:
        _fail("historical_comparison_missing")
    left, right = by_id[left_capture_id], by_id[right_capture_id]
    if left["family_id"] != right["family_id"]:
        _fail("historical_comparison_family_mismatch")
    return HistoricalComparison(left["family_id"], left["capture_id"], left["source_revision"], left["content_sha256"], right["capture_id"], right["source_revision"], right["content_sha256"])
