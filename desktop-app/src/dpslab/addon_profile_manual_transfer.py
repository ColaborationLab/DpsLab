"""Explicit, local-only bridge from one identity snapshot to one protected profile."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .addon_character_identity_transport import CharacterIdentitySnapshot
from .local_character_context_profile import (
    CharacterContextProfileError,
    CharacterContextProfileInput,
    DataProtector,
    create_profile,
    inspect_profile,
    replace_selected_profile,
)


PREVIEW_CONFIRMATION = "PREVIEW_ADDON_PROFILE_TRANSFER"
CREATE_CONFIRMATION = "CREATE_ADDON_PROFILE_TRANSFER"
REPLACE_CONFIRMATION = "REPLACE_ADDON_PROFILE_TRANSFER"
MAX_CAPTURE_AGE_SECONDS = 900
MAX_DISPLAY_VALUE_LENGTH = 128


@dataclass(frozen=True, repr=False)
class LocalDisplayIdentity:
    display_name: str
    realm: str


@dataclass(frozen=True, repr=False)
class ManualTransferPreview:
    state: str
    reason: str | None
    context: CharacterContextProfileInput | None


@dataclass(frozen=True, repr=False)
class ManualTransferResult:
    state: str
    reason: str | None
    profile_id: str | None


def _integer(value: object, minimum: int, maximum: int) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        return None
    return value


def _display(value: object) -> str | None:
    if not isinstance(value, str) or not 1 <= len(value) <= MAX_DISPLAY_VALUE_LENGTH or "\x00" in value:
        return None
    return value


def _rejected(reason: str) -> ManualTransferPreview:
    return ManualTransferPreview("rejected", reason, None)


def preview_manual_identity_transfer(
    snapshot: object,
    display: object,
    *,
    expected_build: object,
    expected_interface_version: object,
    now_epoch: object,
    confirmation: object,
) -> ManualTransferPreview:
    """Create a non-durable profile candidate only after explicit confirmation."""
    if confirmation != PREVIEW_CONFIRMATION:
        return _rejected("consent_required")
    if not isinstance(snapshot, CharacterIdentitySnapshot):
        return _rejected("source_invalid")
    if not isinstance(display, LocalDisplayIdentity):
        return _rejected("display_identity_invalid")
    name = _display(display.display_name)
    realm = _display(display.realm)
    if name is None or realm is None:
        return _rejected("display_identity_invalid")
    build = _integer(expected_build, 1, 9_999_999)
    interface = _integer(expected_interface_version, 1, 9_999_999)
    now = _integer(now_epoch, 1, 9_999_999_999)
    if build is None or interface is None or now is None:
        return _rejected("compatibility_unavailable")
    if snapshot.build != build or snapshot.interface_version != interface:
        return _rejected("compatibility_unavailable")
    if snapshot.captured_at > now:
        return _rejected("transport_from_future")
    if now - snapshot.captured_at > MAX_CAPTURE_AGE_SECONDS:
        return _rejected("transport_stale")
    try:
        captured_at = datetime.fromtimestamp(snapshot.captured_at, tz=timezone.utc).isoformat().replace("+00:00", "Z")
    except (OverflowError, OSError, ValueError):
        return _rejected("transport_invalid")
    return ManualTransferPreview(
        "ready",
        None,
        CharacterContextProfileInput(
            name,
            realm,
            snapshot.class_id,
            snapshot.specialization_id,
            snapshot.role,
            snapshot.level,
            snapshot.race_id,
            str(snapshot.build),
            captured_at,
        ),
    )


def apply_manual_identity_transfer(
    root: Path,
    preview: object,
    protector: DataProtector,
    *,
    operation: object,
    confirmation: object,
    selected_profile_id: object = None,
) -> ManualTransferResult:
    """Persist an approved preview only through an explicit create or replace choice."""
    if not isinstance(preview, ManualTransferPreview) or preview.state != "ready" or preview.context is None:
        return ManualTransferResult("rejected", "preview_unavailable", None)
    if operation == "create":
        if confirmation != CREATE_CONFIRMATION:
            return ManualTransferResult("rejected", "create_confirmation_required", None)
        try:
            if inspect_profile(root, protector).state != "absent":
                return ManualTransferResult("rejected", "profile_already_selected", None)
            stored = create_profile(root, preview.context, protector)
        except CharacterContextProfileError:
            return ManualTransferResult("rejected", "profile_unavailable", None)
        return ManualTransferResult("created", None, stored.profile_id)
    if operation == "replace":
        if confirmation != REPLACE_CONFIRMATION:
            return ManualTransferResult("rejected", "replace_confirmation_required", None)
        if not isinstance(selected_profile_id, str):
            return ManualTransferResult("rejected", "profile_mismatch", None)
        try:
            stored = replace_selected_profile(root, selected_profile_id, preview.context, protector)
        except CharacterContextProfileError:
            return ManualTransferResult("rejected", "profile_mismatch", None)
        return ManualTransferResult("replaced", None, stored.profile_id)
    return ManualTransferResult("rejected", "operation_invalid", None)
