"""Injected transport validation with no built-in network implementation."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Callable
from urllib.parse import urlsplit

from .official_source_request import OfficialRequestPlan
from .patch_source_adapter import InjectedResponse


@dataclass(frozen=True)
class RawTransportResponse:
    status_code: int
    final_url: str
    media_type: str
    body: bytes
    complete: bool
    etag: str | None = None
    last_modified: str | None = None


@dataclass(frozen=True)
class OfficialTransportOutcome:
    status: str
    reason: str | None
    response: InjectedResponse | None


Sender = Callable[[OfficialRequestPlan, float], RawTransportResponse]
_HEADER = re.compile(r"^[\x20-\x7e]{1,256}$")


def _unavailable(reason: str) -> OfficialTransportOutcome:
    return OfficialTransportOutcome("evidence_unavailable", reason, None)


def _header(value: object) -> bool:
    return value is None or isinstance(value, str) and _HEADER.fullmatch(value) is not None


def execute_injected_transport(plan: OfficialRequestPlan, sender: Sender, *, timeout_seconds: float = 15.0) -> OfficialTransportOutcome:
    if not isinstance(plan, OfficialRequestPlan):
        return _unavailable("plan_invalid")
    if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, (int, float)) or not 1 <= timeout_seconds <= 30:
        return _unavailable("timeout_invalid")
    if plan.credential_mode != "none":
        return _unavailable("credential_required")
    try:
        raw = sender(plan, float(timeout_seconds))
    except Exception:
        return _unavailable("transport_error")
    if not isinstance(raw, RawTransportResponse):
        return _unavailable("response_type_invalid")
    if isinstance(raw.status_code, bool) or not isinstance(raw.status_code, int) or raw.status_code not in {200, 304}:
        return _unavailable("status_not_accepted")
    try:
        requested = urlsplit(plan.url)
        final = urlsplit(raw.final_url)
    except (TypeError, ValueError):
        return _unavailable("final_url_invalid")
    allowed_hosts = {requested.hostname, *plan.allowed_redirect_hosts}
    if final.scheme != "https" or final.hostname not in allowed_hosts or final.username is not None or final.password is not None or final.fragment:
        return _unavailable("final_url_not_allowlisted")
    if final.hostname == requested.hostname and (final.path != requested.path or final.query != requested.query):
        return _unavailable("final_target_changed")
    media = raw.media_type.split(";", 1)[0].strip().lower() if isinstance(raw.media_type, str) else ""
    if media not in plan.accepted_media_types:
        return _unavailable("media_type_invalid")
    if not isinstance(raw.body, bytes):
        return _unavailable("body_type_invalid")
    if not isinstance(raw.complete, bool):
        return _unavailable("complete_flag_invalid")
    if not _header(raw.etag) or not _header(raw.last_modified):
        return _unavailable("cache_validator_invalid")
    if raw.status_code == 304:
        if raw.body or not raw.complete or raw.etag is None and raw.last_modified is None:
            return _unavailable("not_modified_invalid")
    elif not raw.complete or not raw.body or len(raw.body) > plan.max_bytes:
        return _unavailable("body_incomplete_or_size_invalid")
    return OfficialTransportOutcome(
        "response_quarantined_pending_capture_validation",
        None,
        InjectedResponse(raw.status_code, final.hostname or "", media, raw.body, raw.complete, raw.etag, raw.last_modified),
    )
