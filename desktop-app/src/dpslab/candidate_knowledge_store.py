"""Crash-consistent single-writer persistence for candidate knowledge sets."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re
from typing import Any, Mapping
from uuid import uuid4

from .candidate_knowledge_set import (
    calculate_receipt_sha256,
    canonical_receipt_bytes,
    validate_candidate_receipt,
)
from .catalog_change_proposal import validate_catalog_change_proposal
from .knowledge_envelope import canonical_json_bytes, validate_knowledge_envelope
from .proposal_review import calculate_decision_sha256, evaluate_proposal_review
from .static_template_catalog import canonical_catalog_bytes, validate_static_template_catalog


class CandidateKnowledgeStoreError(ValueError):
    """A candidate generation cannot be safely committed or read."""


@dataclass(frozen=True)
class CandidateCommitResult:
    generation_id: str
    generation_path: Path
    commit_sha256: str
    idempotent: bool


_TOKEN = re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$")
_GENERATION = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
_SHA = re.compile(r"^[0-9a-f]{64}$")
_SET_FIELDS = {"schema_version", "candidate_envelope", "candidate_catalog", "receipt"}
_COMMIT_FIELDS = {"schema_version", "identity", "bindings", "consumption", "integrity"}
_IDENTITY_FIELDS = {"generation_id", "committed_at", "status"}
_BINDING_FIELDS = {"candidate_envelope_sha256", "candidate_catalog_sha256", "receipt_sha256"}
_CONSUMPTION_FIELDS = {"decision_id", "proposal_id", "durably_recorded"}
_INTEGRITY_FIELDS = {"hash_algorithm", "commit_sha256"}
_MARKER_FIELDS = {"schema_version", "generation_id", "commit_sha256"}


def _fail(reason: str) -> None:
    raise CandidateKnowledgeStoreError(reason)


def _closed(value: Any, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        _fail(f"{label}_fields_invalid")
    return value


def _token(value: Any, label: str) -> str:
    if not isinstance(value, str) or _TOKEN.fullmatch(value) is None:
        _fail(f"{label}_invalid")
    return value


def _generation_token(value: Any) -> str:
    if not isinstance(value, str) or _GENERATION.fullmatch(value) is None:
        _fail("generation_id_invalid")
    return value


def _utc_text(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        _fail("committed_at_invalid")
    return value.isoformat().replace("+00:00", "Z")


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _commit_projection(document: Mapping[str, Any]) -> bytes:
    value = deepcopy(dict(document))
    value["integrity"]["commit_sha256"] = ""
    return canonical_json_bytes(value)


def calculate_commit_sha256(document: Mapping[str, Any]) -> str:
    return _sha(_commit_projection(document))


def validate_candidate_commit(document: Mapping[str, Any]) -> dict[str, Any]:
    root = _closed(dict(document), _COMMIT_FIELDS, "commit")
    if root["schema_version"] != "0.1":
        _fail("commit_schema_invalid")
    identity = _closed(root["identity"], _IDENTITY_FIELDS, "commit_identity")
    _generation_token(identity["generation_id"])
    if identity["status"] != "candidate_pending_review":
        _fail("commit_status_invalid")
    if not isinstance(identity["committed_at"], str) or not identity["committed_at"].endswith("Z"):
        _fail("committed_at_invalid")
    try:
        parsed = datetime.fromisoformat(identity["committed_at"][:-1] + "+00:00")
    except ValueError as exc:
        raise CandidateKnowledgeStoreError("committed_at_invalid") from exc
    if parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        _fail("committed_at_invalid")
    bindings = _closed(root["bindings"], _BINDING_FIELDS, "commit_bindings")
    if any(not isinstance(value, str) or _SHA.fullmatch(value) is None for value in bindings.values()):
        _fail("commit_binding_invalid")
    consumption = _closed(root["consumption"], _CONSUMPTION_FIELDS, "commit_consumption")
    _token(consumption["decision_id"], "decision_id")
    _token(consumption["proposal_id"], "proposal_id")
    if consumption["durably_recorded"] is not True:
        _fail("consumption_not_durable")
    integrity = _closed(root["integrity"], _INTEGRITY_FIELDS, "commit_integrity")
    if integrity["hash_algorithm"] != "sha256" or not isinstance(integrity["commit_sha256"], str) or _SHA.fullmatch(integrity["commit_sha256"]) is None:
        _fail("commit_integrity_invalid")
    if calculate_commit_sha256(root) != integrity["commit_sha256"]:
        _fail("commit_sha256_mismatch")
    return deepcopy(root)


def _validate_inputs(
    source_envelope: Mapping[str, Any],
    source_catalog: Mapping[str, Any],
    proposal: Mapping[str, Any],
    decision: Mapping[str, Any],
    candidate_set: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    try:
        source_envelope_value = validate_knowledge_envelope(source_envelope)
        source_catalog_value = validate_static_template_catalog(source_catalog)
        proposal_value = validate_catalog_change_proposal(proposal)
        outcome = evaluate_proposal_review(proposal_value, decision)
    except (TypeError, ValueError) as exc:
        raise CandidateKnowledgeStoreError("source_validation_failed") from exc
    if outcome.status != "decision_eligible":
        _fail(f"review_{outcome.reason or outcome.status}")
    root = _closed(dict(candidate_set), _SET_FIELDS, "candidate_set")
    if root["schema_version"] != "0.1":
        _fail("candidate_set_schema_invalid")
    try:
        envelope = validate_knowledge_envelope(root["candidate_envelope"])
        catalog = validate_static_template_catalog(root["candidate_catalog"])
        receipt = validate_candidate_receipt(root["receipt"])
    except (TypeError, ValueError) as exc:
        raise CandidateKnowledgeStoreError("candidate_validation_failed") from exc
    expected = {
        "source_envelope_sha256": _sha(canonical_json_bytes(source_envelope_value)),
        "source_catalog_sha256": source_catalog_value["integrity"]["catalog_sha256"],
        "proposal_sha256": proposal_value["integrity"]["proposal_sha256"],
        "decision_sha256": calculate_decision_sha256(decision),
    }
    if receipt["source_bindings"] != expected:
        _fail("source_binding_mismatch")
    candidate_envelope_sha = _sha(canonical_json_bytes(envelope))
    if receipt["candidate_bindings"] != {
        "candidate_envelope_sha256": candidate_envelope_sha,
        "candidate_catalog_sha256": catalog["integrity"]["catalog_sha256"],
    }:
        _fail("candidate_binding_mismatch")
    matches = [entry for entry in catalog["entries"] if entry["envelope_sha256"] == candidate_envelope_sha]
    if len(matches) != 1 or matches[0]["lifecycle_state"] != "pending_review":
        _fail("candidate_catalog_entry_mismatch")
    return envelope, catalog, receipt


def _confined_root(root: Path, *, create: bool = True) -> Path:
    if root.exists() and (not root.is_dir() or root.is_symlink()):
        _fail("store_root_invalid")
    if create:
        root.mkdir(parents=True, exist_ok=True)
    elif not root.is_dir():
        _fail("store_root_invalid")
    if root.is_symlink():
        _fail("store_root_invalid")
    return root.resolve(strict=True)


def _write_file(path: Path, data: bytes) -> None:
    if path.exists() or path.is_symlink():
        _fail("staged_path_exists")
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def _atomic_marker(path: Path, data: bytes) -> None:
    temporary = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    try:
        _write_file(temporary, data)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        _fail("durable_file_invalid")
    try:
        import json
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise CandidateKnowledgeStoreError("durable_json_invalid") from exc
    if canonical_json_bytes(value) != path.read_bytes():
        _fail("durable_json_noncanonical")
    return value


def _generation_commit(path: Path) -> dict[str, Any]:
    if not path.is_dir() or path.is_symlink():
        _fail("generation_layout_invalid")
    commit = validate_candidate_commit(_read_json(path / "commit.json"))
    try:
        validate_knowledge_envelope(_read_json(path / "candidate_envelope.json"))
        validate_static_template_catalog(_read_json(path / "candidate_catalog.json"))
        validate_candidate_receipt(_read_json(path / "receipt.json"))
    except (TypeError, ValueError) as exc:
        raise CandidateKnowledgeStoreError("durable_candidate_invalid") from exc
    expected = {
        "candidate_envelope_sha256": _sha((path / "candidate_envelope.json").read_bytes()),
        "candidate_catalog_sha256": _sha((path / "candidate_catalog.json").read_bytes()),
        "receipt_sha256": _sha((path / "receipt.json").read_bytes()),
    }
    if commit["bindings"] != expected:
        _fail("durable_binding_mismatch")
    return commit


def _current_marker(root: Path) -> tuple[dict[str, Any], dict[str, Any]] | None:
    path = root / "current.json"
    if not path.exists():
        return None
    marker = _closed(_read_json(path), _MARKER_FIELDS, "marker")
    if marker["schema_version"] != "0.1":
        _fail("marker_schema_invalid")
    generation_id = _generation_token(marker["generation_id"])
    if not isinstance(marker["commit_sha256"], str) or _SHA.fullmatch(marker["commit_sha256"]) is None:
        _fail("marker_sha_invalid")
    commit = _generation_commit(root / "generations" / generation_id)
    if commit["integrity"]["commit_sha256"] != marker["commit_sha256"]:
        _fail("marker_commit_mismatch")
    return marker, commit


def commit_candidate_knowledge_set(
    store_root: Path,
    *,
    source_envelope: Mapping[str, Any],
    source_catalog: Mapping[str, Any],
    proposal: Mapping[str, Any],
    decision: Mapping[str, Any],
    candidate_set: Mapping[str, Any],
    generation_id: str,
    committed_at: datetime,
) -> CandidateCommitResult:
    """Commit one immutable candidate generation under a single-writer model."""
    _generation_token(generation_id)
    timestamp = _utc_text(committed_at)
    envelope, catalog, receipt = _validate_inputs(source_envelope, source_catalog, proposal, decision, candidate_set)
    root = _confined_root(Path(store_root))
    generations = root / "generations"
    staging_root = root / "staging"
    generations.mkdir(exist_ok=True)
    staging_root.mkdir(exist_ok=True)
    if generations.is_symlink() or staging_root.is_symlink():
        _fail("store_layout_invalid")
    envelope_bytes = canonical_json_bytes(envelope)
    catalog_bytes = canonical_catalog_bytes(catalog)
    receipt_bytes = canonical_receipt_bytes(receipt)
    commit = {
        "schema_version": "0.1",
        "identity": {"generation_id": generation_id, "committed_at": timestamp, "status": "candidate_pending_review"},
        "bindings": {
            "candidate_envelope_sha256": _sha(envelope_bytes),
            "candidate_catalog_sha256": _sha(catalog_bytes),
            "receipt_sha256": _sha(receipt_bytes),
        },
        "consumption": {
            "decision_id": receipt["consumption"]["decision_id"],
            "proposal_id": receipt["consumption"]["proposal_id"],
            "durably_recorded": True,
        },
        "integrity": {"hash_algorithm": "sha256", "commit_sha256": ""},
    }
    commit["integrity"]["commit_sha256"] = calculate_commit_sha256(commit)
    commit = validate_candidate_commit(commit)
    final = generations / generation_id
    visible = _current_marker(root)
    for existing in generations.iterdir():
        if existing.is_symlink() or not existing.is_dir():
            _fail("generation_layout_invalid")
        prior = _generation_commit(existing)
        same_consumption = prior["consumption"]["decision_id"] == commit["consumption"]["decision_id"] or prior["consumption"]["proposal_id"] == commit["consumption"]["proposal_id"]
        if same_consumption:
            if existing.name == generation_id and prior["integrity"]["commit_sha256"] == commit["integrity"]["commit_sha256"]:
                marker = {"schema_version": "0.1", "generation_id": generation_id, "commit_sha256": commit["integrity"]["commit_sha256"]}
                if visible is None:
                    _atomic_marker(root / "current.json", canonical_json_bytes(marker))
                elif visible[0] != marker:
                    current_time = datetime.fromisoformat(visible[1]["identity"]["committed_at"][:-1] + "+00:00")
                    if committed_at <= current_time:
                        _fail("stale_generation_replay")
                    _atomic_marker(root / "current.json", canonical_json_bytes(marker))
                return CandidateCommitResult(generation_id, final, commit["integrity"]["commit_sha256"], True)
            _fail("consumption_replay")
    if final.exists():
        _fail("generation_exists")
    if visible is not None:
        current_time = datetime.fromisoformat(visible[1]["identity"]["committed_at"][:-1] + "+00:00")
        if committed_at <= current_time:
            _fail("committed_at_not_strictly_newer")
    staging = staging_root / f"{generation_id}.{uuid4().hex}.staging"
    staging.mkdir()
    try:
        _write_file(staging / "candidate_envelope.json", envelope_bytes)
        _write_file(staging / "candidate_catalog.json", catalog_bytes)
        _write_file(staging / "receipt.json", receipt_bytes)
        _write_file(staging / "commit.json", canonical_json_bytes(commit))
        if _generation_commit(staging) != commit:
            _fail("staging_verification_failed")
        os.replace(staging, final)
        marker = {"schema_version": "0.1", "generation_id": generation_id, "commit_sha256": commit["integrity"]["commit_sha256"]}
        _atomic_marker(root / "current.json", canonical_json_bytes(marker))
    except Exception:
        raise
    return CandidateCommitResult(generation_id, final, commit["integrity"]["commit_sha256"], False)


def read_current_candidate_generation(store_root: Path) -> dict[str, Any]:
    root = _confined_root(Path(store_root), create=False)
    visible = _current_marker(root)
    if visible is None:
        _fail("durable_file_invalid")
    marker, commit = visible
    generation_id = marker["generation_id"]
    path = root / "generations" / generation_id
    return {
        "candidate_envelope": _read_json(path / "candidate_envelope.json"),
        "candidate_catalog": _read_json(path / "candidate_catalog.json"),
        "receipt": _read_json(path / "receipt.json"),
        "commit": commit,
    }
