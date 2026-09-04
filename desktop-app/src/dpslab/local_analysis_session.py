"""Closed, ephemeral analysis-session model for selected equipment variants.

The model is intentionally independent from WoW, addon transports, files, UI,
and simulation engines.  Callers provide only already validated synthetic
values; this module neither discovers nor persists data.
"""

from __future__ import annotations

from dataclasses import dataclass
import re


_TOKEN = re.compile(r"[a-z0-9][a-z0-9_.:-]{0,63}")
_ROLES = frozenset({"damage", "healer", "tank"})
_SOURCES = frozenset({"designated_bag", "equipped"})
_VARIANT_KINDS = frozenset({"enchantment", "gem", "modifier"})
MAX_EQUIPPED_ITEMS = 19
MAX_SELECTED_CANDIDATES = 12
MAX_VIRTUAL_VARIANTS = 12


@dataclass(frozen=True)
class AnalysisCompatibility:
    """Trusted compatibility basis supplied separately from an export."""

    wow_product: str
    build: int
    interface_version: int
    content_version: str


@dataclass(frozen=True)
class AnalysisItem:
    """One synthetic item-shaped value with an explicit source and slot."""

    item_key: str
    item_id: int
    slot: str
    source: str
    current_expansion: bool


@dataclass(frozen=True)
class VirtualVariant:
    """A hypothetical modifier of a selected candidate copy."""

    variant_id: str
    target_item_key: str
    kind: str
    hypothetical: bool


@dataclass(frozen=True, repr=False)
class LocalAnalysisSession:
    """A non-durable requested analysis scope; it is not a simulation result."""

    compatibility: AnalysisCompatibility
    role: str
    content_context: str
    equipped_items: tuple[AnalysisItem, ...]
    selected_candidates: tuple[AnalysisItem, ...]
    virtual_variants: tuple[VirtualVariant, ...]


@dataclass(frozen=True, repr=False)
class LocalAnalysisSessionResult:
    state: str
    reason: str | None
    session: LocalAnalysisSession | None


def _token(value: object) -> bool:
    return isinstance(value, str) and _TOKEN.fullmatch(value) is not None


def _integer(value: object, minimum: int, maximum: int) -> bool:
    return not isinstance(value, bool) and isinstance(value, int) and minimum <= value <= maximum


def _unavailable(reason: str) -> LocalAnalysisSessionResult:
    return LocalAnalysisSessionResult("session_unavailable", reason, None)


def _compatibility(value: object) -> AnalysisCompatibility | None:
    if not isinstance(value, AnalysisCompatibility):
        return None
    if value.wow_product != "retail" or not _integer(value.build, 1, 9_999_999):
        return None
    if not _integer(value.interface_version, 1, 9_999_999) or not _token(value.content_version):
        return None
    return value


def _items(
    values: object,
    *,
    required_source: str,
    maximum: int,
) -> tuple[AnalysisItem, ...] | None:
    if not isinstance(values, tuple) or not 1 <= len(values) <= maximum:
        return None
    result: list[AnalysisItem] = []
    keys: set[str] = set()
    for value in values:
        if not isinstance(value, AnalysisItem):
            return None
        if (
            not _token(value.item_key)
            or not _integer(value.item_id, 1, 9_999_999)
            or not _token(value.slot)
            or value.source not in _SOURCES
            or value.source != required_source
            or value.current_expansion is not True
            or value.item_key in keys
        ):
            return None
        keys.add(value.item_key)
        result.append(value)
    return tuple(result)


def build_local_analysis_session(
    compatibility: object,
    role: object,
    content_context: object,
    equipped_items: object,
    selected_candidates: object,
    virtual_variants: object,
) -> LocalAnalysisSessionResult:
    """Validate one bounded, non-persistent analysis request."""

    trusted = _compatibility(compatibility)
    if trusted is None:
        return _unavailable("compatibility_unavailable")
    if role not in _ROLES or not _token(content_context):
        return _unavailable("analysis_context_invalid")
    equipped = _items(equipped_items, required_source="equipped", maximum=MAX_EQUIPPED_ITEMS)
    candidates = _items(
        selected_candidates,
        required_source="designated_bag",
        maximum=MAX_SELECTED_CANDIDATES,
    )
    if equipped is None or candidates is None:
        return _unavailable("analysis_items_invalid")
    equipped_keys = {item.item_key for item in equipped}
    candidate_keys = {item.item_key for item in candidates}
    if equipped_keys & candidate_keys:
        return _unavailable("analysis_items_invalid")
    equipped_slots = {item.slot for item in equipped}
    if any(item.slot not in equipped_slots for item in candidates):
        return _unavailable("analysis_slot_invalid")
    if not isinstance(virtual_variants, tuple) or len(virtual_variants) > MAX_VIRTUAL_VARIANTS:
        return _unavailable("analysis_variants_invalid")
    variants: list[VirtualVariant] = []
    variant_ids: set[str] = set()
    for value in virtual_variants:
        if (
            not isinstance(value, VirtualVariant)
            or not _token(value.variant_id)
            or value.variant_id in variant_ids
            or value.target_item_key not in candidate_keys
            or value.kind not in _VARIANT_KINDS
            or value.hypothetical is not True
        ):
            return _unavailable("analysis_variants_invalid")
        variant_ids.add(value.variant_id)
        variants.append(value)
    return LocalAnalysisSessionResult(
        "session_ready",
        None,
        LocalAnalysisSession(
            trusted,
            role,
            content_context,
            equipped,
            candidates,
            tuple(variants),
        ),
    )
