"""Fail-closed synthetic evidence gate for the Druid vertical slice.

This module deliberately evaluates receipts only.  It never reads an addon,
contacts a source, stores evidence, or supplies game facts or guidance.
"""

from __future__ import annotations

from dataclasses import dataclass
import re

from .druid_role_context import DruidRolePolicy


_TOKEN = re.compile(r"[a-z0-9][a-z0-9_.:-]{0,127}")
_SHA256 = re.compile(r"[0-9a-f]{64}")
_ROLE_SAFETY = {
    "damage": "damage_primary",
    "tank": "survival_first",
    "healer": "healing_safety_first",
}


@dataclass(frozen=True)
class CompatibilityReceipt:
    receipt_id: str
    receipt_sha256: str
    build_min: int
    build_max: int
    interface_min: int
    interface_max: int
    reviewed: bool
    synthetic: bool


@dataclass(frozen=True)
class SemanticMappingReceipt:
    receipt_id: str
    receipt_sha256: str
    specialization: str
    role: str
    reviewed: bool
    synthetic: bool


@dataclass(frozen=True)
class TemplateReceipt:
    template_id: str
    template_sha256: str
    role: str
    safety_ordering: str
    closed: bool
    synthetic: bool


@dataclass(frozen=True)
class DruidTemplateEvidence:
    registry: CompatibilityReceipt
    mapping: SemanticMappingReceipt
    primary_source: CompatibilityReceipt
    template: TemplateReceipt


@dataclass(frozen=True)
class DruidTemplateEvidenceDecision:
    status: str
    reason: str | None
    policy: DruidRolePolicy | None
    template_id: str | None


def _valid_token(value: object) -> bool:
    return isinstance(value, str) and _TOKEN.fullmatch(value) is not None


def _valid_sha256(value: object) -> bool:
    return isinstance(value, str) and _SHA256.fullmatch(value) is not None


def _valid_range(minimum: object, maximum: object) -> bool:
    return (
        not isinstance(minimum, bool)
        and not isinstance(maximum, bool)
        and isinstance(minimum, int)
        and isinstance(maximum, int)
        and 1 <= minimum <= maximum <= 10_000_000
    )


def _valid_compatibility(receipt: object, build: int, interface: int) -> bool:
    if not isinstance(receipt, CompatibilityReceipt):
        return False
    return (
        _valid_token(receipt.receipt_id)
        and _valid_sha256(receipt.receipt_sha256)
        and _valid_range(receipt.build_min, receipt.build_max)
        and _valid_range(receipt.interface_min, receipt.interface_max)
        and receipt.reviewed is True
        and receipt.synthetic is True
        and receipt.build_min <= build <= receipt.build_max
        and receipt.interface_min <= interface <= receipt.interface_max
    )


def _unavailable(reason: str, policy: DruidRolePolicy | None = None) -> DruidTemplateEvidenceDecision:
    return DruidTemplateEvidenceDecision("evidence_unavailable", reason, policy, None)


def evaluate_druid_template_evidence(
    policy: object, evidence: object, build: object, interface: object
) -> DruidTemplateEvidenceDecision:
    """Return review eligibility only after four synthetic, reviewed bindings."""

    if not isinstance(policy, DruidRolePolicy):
        return _unavailable("policy_invalid")
    if isinstance(build, bool) or not isinstance(build, int) or not 1 <= build <= 10_000_000:
        return _unavailable("build_invalid", policy)
    if isinstance(interface, bool) or not isinstance(interface, int) or not 1 <= interface <= 10_000_000:
        return _unavailable("interface_invalid", policy)
    if not isinstance(evidence, DruidTemplateEvidence):
        return _unavailable("evidence_invalid", policy)
    if not _valid_compatibility(evidence.registry, build, interface):
        return _unavailable("registry_evidence_unavailable", policy)
    if not _valid_compatibility(evidence.primary_source, build, interface):
        return _unavailable("primary_source_evidence_unavailable", policy)

    mapping = evidence.mapping
    if not isinstance(mapping, SemanticMappingReceipt):
        return _unavailable("mapping_evidence_unavailable", policy)
    if not (
        _valid_token(mapping.receipt_id)
        and _valid_sha256(mapping.receipt_sha256)
        and mapping.specialization == policy.specialization
        and mapping.role == policy.role
        and mapping.reviewed is True
        and mapping.synthetic is True
    ):
        return _unavailable("mapping_evidence_unavailable", policy)

    template = evidence.template
    if not isinstance(template, TemplateReceipt):
        return _unavailable("template_evidence_unavailable", policy)
    if not (
        _valid_token(template.template_id)
        and _valid_sha256(template.template_sha256)
        and template.role == policy.role
        and template.safety_ordering == _ROLE_SAFETY[policy.role]
        and template.closed is True
        and template.synthetic is True
    ):
        return _unavailable("template_evidence_unavailable", policy)
    return DruidTemplateEvidenceDecision("review_eligible", None, policy, template.template_id)
