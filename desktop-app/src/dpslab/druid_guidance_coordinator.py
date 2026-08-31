"""Synthetic end-to-end coordination for the Druid vertical slice.

The coordinator joins already validated identity, semantic role policy, and
the governed static catalog. It performs no acquisition, persistence,
network access, simulation, or live game-fact mapping.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Any

from .addon_character_identity_transport import CharacterIdentitySnapshot
from .druid_identity_context import DruidIdentityRegistry, bind_druid_identity_context
from .druid_role_context import DruidRolePolicy
from .knowledge_envelope import CompatibilityContext, KnowledgeEnvelopeError
from .static_template_catalog import (
    ApprovalEvidence,
    StaticTemplateCatalogError,
    select_catalog_guidance,
)


@dataclass(frozen=True)
class DruidGuidanceDecision:
    """Bounded result that never retains or exposes character identity."""

    status: str
    reason: str | None
    policy: DruidRolePolicy | None
    entry_id: str | None
    statements: tuple[Mapping[str, Any], ...]


_TOKEN = re.compile(r"[a-z0-9][a-z0-9_.:-]{0,127}")


def _unavailable(
    reason: str, policy: DruidRolePolicy | None = None
) -> DruidGuidanceDecision:
    return DruidGuidanceDecision("guidance_unavailable", reason, policy, None, ())


def coordinate_druid_guidance(
    snapshot: object,
    registry: object,
    catalog: object,
    repository_root: object,
    content_context: object,
    observed_at: object,
    approval: object,
) -> DruidGuidanceDecision:
    """Select synthetic guidance only after identity and catalog validation."""

    identity = bind_druid_identity_context(snapshot, registry)
    if identity.status != "context_available" or identity.policy is None:
        return _unavailable(identity.reason or "identity_context_unavailable")

    if not isinstance(snapshot, CharacterIdentitySnapshot) or not isinstance(
        registry, DruidIdentityRegistry
    ):
        return _unavailable("identity_context_invalid")
    if not isinstance(catalog, Mapping):
        return _unavailable("catalog_invalid", identity.policy)
    if not isinstance(repository_root, Path):
        return _unavailable("repository_root_invalid", identity.policy)
    if not isinstance(content_context, str) or _TOKEN.fullmatch(content_context) is None:
        return _unavailable("content_context_invalid", identity.policy)
    if not isinstance(observed_at, datetime) or observed_at.tzinfo is None:
        return _unavailable("observed_at_invalid", identity.policy)
    try:
        if observed_at.utcoffset() is None:
            return _unavailable("observed_at_invalid", identity.policy)
        observed_at.astimezone(timezone.utc)
    except (ValueError, OverflowError):
        return _unavailable("observed_at_invalid", identity.policy)
    if approval is not None and not isinstance(approval, ApprovalEvidence):
        return _unavailable("approval_invalid", identity.policy)

    context = CompatibilityContext(
        wow_product="retail",
        build=snapshot.build,
        interface=snapshot.interface_version,
        class_id=snapshot.class_id,
        specialization_id=snapshot.specialization_id,
        race_id=snapshot.race_id,
        level=snapshot.level,
        content_context=content_context,
        observed_at=observed_at,
    )
    try:
        selected = select_catalog_guidance(catalog, repository_root, context, approval)
    except (KnowledgeEnvelopeError, StaticTemplateCatalogError):
        return _unavailable("knowledge_invalid", identity.policy)

    if selected.status != "guidance_available":
        return _unavailable(selected.reason or "knowledge_unavailable", identity.policy)
    return DruidGuidanceDecision(
        "guidance_available",
        None,
        identity.policy,
        selected.entry_id,
        selected.statements,
    )
