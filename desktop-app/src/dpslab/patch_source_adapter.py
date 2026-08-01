"""Pure capture boundary for injected patch-source responses."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import re
from typing import Any, Mapping

from .patch_evidence import PatchContext, PatchIntakeResult, intake_patch_evidence


class PatchSourceError(ValueError):
    pass


@dataclass(frozen=True)
class InjectedResponse:
    status_code: int
    final_host: str
    media_type: str
    body: bytes
    complete: bool
    etag: str | None = None
    last_modified: str | None = None


@dataclass(frozen=True)
class PreviousCapture:
    content_sha256: str
    etag: str | None
    last_modified: str | None


@dataclass(frozen=True)
class CaptureOutcome:
    status: str
    reason: str | None
    source_id: str
    content_sha256: str | None
    byte_count: int
    reused_previous: bool


_TOKEN = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
_HOST = re.compile(r"^[a-z0-9][a-z0-9.-]{0,252}$")
_SHA = re.compile(r"^[0-9a-f]{64}$")
_ROOT = {"schema_version", "identity", "sources", "integrity"}
_IDENTITY = {"registry_id", "created_at", "wow_product"}
_SOURCE = {"source_id", "owner", "canonical_host", "redirect_hosts", "media_types", "max_bytes", "locale_policy", "review_owner"}
_INTEGRITY = {"hash_algorithm", "registry_sha256"}


def _fail(reason: str) -> None:
    raise PatchSourceError(reason)


def _closed(value: Any, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        _fail(f"{label}_fields_invalid")
    return value


def _token(value: Any, label: str) -> str:
    if not isinstance(value, str) or _TOKEN.fullmatch(value) is None:
        _fail(f"{label}_invalid")
    return value


def _host(value: Any, label: str) -> str:
    if not isinstance(value, str) or _HOST.fullmatch(value) is None or ".." in value:
        _fail(f"{label}_invalid")
    return value


def _timestamp(value: Any, label: str) -> None:
    if not isinstance(value, str) or not value.endswith("Z"):
        _fail(f"{label}_invalid")
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise PatchSourceError(f"{label}_invalid") from exc


def _validator(value: Any) -> bool:
    return value is None or (isinstance(value, str) and 1 <= len(value) <= 256 and "\r" not in value and "\n" not in value)


def canonical_registry_bytes(document: Mapping[str, Any]) -> bytes:
    return (json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def calculate_registry_sha256(document: Mapping[str, Any]) -> str:
    projection = deepcopy(dict(document))
    projection["integrity"]["registry_sha256"] = ""
    return hashlib.sha256(canonical_registry_bytes(projection)).hexdigest()


def validate_source_registry(document: Mapping[str, Any]) -> dict[str, Any]:
    root = _closed(dict(document), _ROOT, "root")
    if root["schema_version"] != "0.1":
        _fail("schema_version_invalid")
    identity = _closed(root["identity"], _IDENTITY, "identity")
    _token(identity["registry_id"], "registry_id")
    _timestamp(identity["created_at"], "created_at")
    if identity["wow_product"] != "retail":
        _fail("wow_product_invalid")
    if not isinstance(root["sources"], list) or not root["sources"]:
        _fail("sources_invalid")
    ids: set[str] = set()
    for raw in root["sources"]:
        source = _closed(raw, _SOURCE, "source")
        source_id = _token(source["source_id"], "source_id")
        if source_id in ids:
            _fail("source_id_duplicate")
        ids.add(source_id)
        _token(source["owner"], "owner")
        canonical = _host(source["canonical_host"], "canonical_host")
        if not isinstance(source["redirect_hosts"], list):
            _fail("redirect_hosts_invalid")
        redirects = [_host(value, "redirect_host") for value in source["redirect_hosts"]]
        if len(redirects) != len(set(redirects)) or canonical in redirects:
            _fail("redirect_hosts_invalid")
        if not isinstance(source["media_types"], list) or not source["media_types"]:
            _fail("media_types_invalid")
        for media in source["media_types"]:
            if media not in {"application/json", "text/plain", "text/html"}:
                _fail("media_type_invalid")
        if len(source["media_types"]) != len(set(source["media_types"])):
            _fail("media_types_invalid")
        if isinstance(source["max_bytes"], bool) or not isinstance(source["max_bytes"], int) or not 1 <= source["max_bytes"] <= 1_048_576:
            _fail("max_bytes_invalid")
        if source["locale_policy"] not in {"locale_neutral", "en_us_canonical"}:
            _fail("locale_policy_invalid")
        _token(source["review_owner"], "review_owner")
    integrity = _closed(root["integrity"], _INTEGRITY, "integrity")
    if integrity["hash_algorithm"] != "sha256" or not isinstance(integrity["registry_sha256"], str) or _SHA.fullmatch(integrity["registry_sha256"]) is None:
        _fail("integrity_invalid")
    if calculate_registry_sha256(root) != integrity["registry_sha256"]:
        _fail("registry_sha256_mismatch")
    return deepcopy(root)


def capture_injected_response(registry: Mapping[str, Any], source_id: str, response: InjectedResponse, previous: PreviousCapture | None = None) -> CaptureOutcome:
    value = validate_source_registry(registry)
    _token(source_id, "source_id")
    source = next((item for item in value["sources"] if item["source_id"] == source_id), None)
    if source is None:
        return CaptureOutcome("evidence_unavailable", "source_not_allowlisted", source_id, None, 0, False)
    if not isinstance(response.status_code, int) or isinstance(response.status_code, bool):
        return CaptureOutcome("evidence_unavailable", "status_invalid", source_id, None, 0, False)
    try:
        final_host = _host(response.final_host, "final_host")
    except PatchSourceError:
        return CaptureOutcome("evidence_unavailable", "host_invalid", source_id, None, 0, False)
    if final_host not in {source["canonical_host"], *source["redirect_hosts"]}:
        return CaptureOutcome("evidence_unavailable", "redirect_not_allowlisted", source_id, None, 0, False)
    if response.media_type not in source["media_types"]:
        return CaptureOutcome("evidence_unavailable", "media_type_invalid", source_id, None, 0, False)
    if not _validator(response.etag) or not _validator(response.last_modified):
        return CaptureOutcome("evidence_unavailable", "cache_validator_invalid", source_id, None, 0, False)
    if response.status_code == 304:
        if previous is None or not _valid_previous(previous):
            return CaptureOutcome("evidence_unavailable", "not_modified_without_verified_previous", source_id, None, 0, False)
        validator_matches = ((response.etag is not None and response.etag == previous.etag) or
                             (response.last_modified is not None and response.last_modified == previous.last_modified))
        if not validator_matches or response.body or not response.complete:
            return CaptureOutcome("evidence_unavailable", "not_modified_invalid", source_id, None, 0, False)
        return CaptureOutcome("not_modified", None, source_id, previous.content_sha256, 0, True)
    if response.status_code != 200:
        return CaptureOutcome("evidence_unavailable", "status_not_success", source_id, None, 0, False)
    if not isinstance(response.body, bytes):
        return CaptureOutcome("evidence_unavailable", "body_type_invalid", source_id, None, 0, False)
    size = len(response.body)
    if not response.complete:
        return CaptureOutcome("evidence_unavailable", "partial_transfer", source_id, None, size, False)
    if size == 0 or size > source["max_bytes"]:
        return CaptureOutcome("evidence_unavailable", "body_size_invalid", source_id, None, size, False)
    digest = hashlib.sha256(response.body).hexdigest()
    if previous is not None and _valid_previous(previous) and previous.content_sha256 == digest:
        return CaptureOutcome("duplicate", None, source_id, digest, size, True)
    return CaptureOutcome("captured_pending_review", None, source_id, digest, size, False)


def _valid_previous(previous: PreviousCapture) -> bool:
    return (isinstance(previous.content_sha256, str) and _SHA.fullmatch(previous.content_sha256) is not None
            and _validator(previous.etag) and _validator(previous.last_modified))


def handoff_structured_evidence(document: Mapping[str, Any], context: PatchContext, allowed_families: frozenset[str]) -> PatchIntakeResult:
    """Delegate only to the existing quarantine; never approve or publish."""
    return intake_patch_evidence(document, context, allowed_families)
