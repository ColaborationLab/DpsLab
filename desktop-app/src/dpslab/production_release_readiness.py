"""Pure fail-closed readiness assessment before any production signing operation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

from .candidate_release_bundle import validate_candidate_release_bundle
from .release_signing import validate_release_trust_registry


class ProductionReleaseReadinessError(ValueError):
    pass


@dataclass(frozen=True)
class ProductionReleaseReadinessContext:
    observed_at: datetime
    wow_build: int
    interface: int
    target_channel: str
    production_key_id: str


@dataclass(frozen=True)
class ProductionReleaseReadinessOutcome:
    status: str
    reasons: tuple[str, ...]
    manifest_sha256: str | None
    key_id: str | None


def _utc(value: datetime, label: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise ProductionReleaseReadinessError(f"{label}_invalid")
    return value


def _time(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ProductionReleaseReadinessError(f"{label}_invalid")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ProductionReleaseReadinessError(f"{label}_invalid") from exc
    return _utc(parsed, label)


def _context(value: ProductionReleaseReadinessContext) -> ProductionReleaseReadinessContext:
    _utc(value.observed_at, "observed_at")
    for field in ("wow_build", "interface"):
        item = getattr(value, field)
        if isinstance(item, bool) or not isinstance(item, int) or item < 1:
            raise ProductionReleaseReadinessError(f"{field}_invalid")
    if value.target_channel not in {"stable", "beta"}:
        raise ProductionReleaseReadinessError("target_channel_invalid")
    if not isinstance(value.production_key_id, str) or not value.production_key_id.startswith("dpslab.release.ed25519."):
        raise ProductionReleaseReadinessError("production_key_id_invalid")
    return value


def _strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for key, item in value.items():
            yield from _strings(key)
            yield from _strings(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _strings(item)


def assess_production_release_readiness(
    bundle: Mapping[str, Any],
    registry: Mapping[str, Any],
    context: ProductionReleaseReadinessContext,
) -> ProductionReleaseReadinessOutcome:
    """Assess exact public inputs without constructing a signer or mutating state."""
    current = _context(context)
    try:
        candidate = validate_candidate_release_bundle(bundle)
    except (TypeError, ValueError):
        return ProductionReleaseReadinessOutcome("production_release_readiness_unavailable", ("candidate_bundle_invalid",), None, None)
    try:
        trust = validate_release_trust_registry(registry)
    except (TypeError, ValueError):
        return ProductionReleaseReadinessOutcome("production_release_readiness_unavailable", ("trust_registry_invalid",), candidate["manifest"]["integrity"]["manifest_sha256"], None)

    manifest = candidate["manifest"]
    envelope = candidate["release_envelope"]
    review = candidate["review_decision"]
    reasons: list[str] = []
    lowered = tuple(text.lower() for text in _strings(candidate))
    if any("synthetic" in text for text in lowered):
        reasons.append("synthetic_material_forbidden")
    if any("placeholder" in text for text in lowered):
        reasons.append("placeholder_material_forbidden")

    identity = manifest["identity"]
    compatibility = manifest["compatibility"]
    assessment = review["assessment"]
    if identity["target_channel"] != current.target_channel:
        reasons.append("target_channel_mismatch")
    if not compatibility["build_min"] <= current.wow_build <= compatibility["build_max"]:
        reasons.append("wow_build_outside_manifest")
    if not compatibility["interface_min"] <= current.interface <= compatibility["interface_max"]:
        reasons.append("interface_outside_manifest")
    if assessment["wow_build"] != current.wow_build:
        reasons.append("review_wow_build_mismatch")
    if assessment["interface"] != current.interface:
        reasons.append("review_interface_mismatch")
    if _time(identity["created_at"], "manifest_created_at") > current.observed_at:
        reasons.append("manifest_created_in_future")
    expires_at = _time(envelope["evidence"]["expires_at"], "expires_at")
    if current.observed_at >= expires_at:
        reasons.append("evidence_expired")
    if envelope["integrity"]["publisher_key_id"] != current.production_key_id:
        reasons.append("publisher_key_mismatch")

    keys = [item for item in trust["keys"] if item["key_id"] == current.production_key_id and item["status"] == "trusted"]
    if len(keys) != 1:
        reasons.append("trusted_production_key_not_found")
    else:
        key = keys[0]
        if not _time(key["valid_from"], "key_valid_from") <= current.observed_at <= _time(key["valid_until"], "key_valid_until"):
            reasons.append("production_key_outside_validity")

    unique = tuple(dict.fromkeys(reasons))
    if unique:
        return ProductionReleaseReadinessOutcome(
            "production_release_readiness_unavailable",
            unique,
            manifest["integrity"]["manifest_sha256"],
            current.production_key_id,
        )
    return ProductionReleaseReadinessOutcome(
        "production_release_candidate_ready_for_attended_signing_review",
        (),
        manifest["integrity"]["manifest_sha256"],
        current.production_key_id,
    )
