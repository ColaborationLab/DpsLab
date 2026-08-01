"""Pure construction of inert, allowlisted first-party request plans."""

from __future__ import annotations

from dataclasses import dataclass
import re
from types import MappingProxyType
from typing import Mapping
from urllib.parse import quote, urlencode, urlunsplit


class OfficialSourceRequestError(ValueError):
    pass


@dataclass(frozen=True)
class OfficialRequestPlan:
    source_id: str
    method: str
    url: str
    headers: Mapping[str, str]
    allowed_redirect_hosts: tuple[str, ...]
    accepted_media_types: tuple[str, ...]
    max_bytes: int
    credential_mode: str
    status: str = "ready_for_injected_transport"


_SAFE_VALUE = re.compile(r"^[\x20-\x7e]{1,256}$")
_API_PATH = re.compile(r"^/data/wow/[a-z0-9][a-z0-9/_-]{0,190}$")
_NAMESPACE = re.compile(r"^(?:static|dynamic)-[a-z0-9]+$")


def _validator(value: str | None, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or _SAFE_VALUE.fullmatch(value) is None:
        raise OfficialSourceRequestError(f"{label}_invalid")
    return value


def _plan(source_id: str, host: str, path: str, query: str, accept: str, max_bytes: int,
          credential_mode: str, etag: str | None, last_modified: str | None) -> OfficialRequestPlan:
    headers = {"Accept": accept, "User-Agent": "DpsLab-maintainer/0.1"}
    if (value := _validator(etag, "etag")) is not None:
        headers["If-None-Match"] = value
    if (value := _validator(last_modified, "last_modified")) is not None:
        headers["If-Modified-Since"] = value
    return OfficialRequestPlan(
        source_id, "GET", urlunsplit(("https", host, path, query, "")),
        MappingProxyType(headers), (), (accept,), max_bytes, credential_mode,
    )


def plan_content_update_notes(etag: str | None = None, last_modified: str | None = None) -> OfficialRequestPlan:
    """Plan exact first-party discovery; never execute it."""
    return _plan(
        "blizzard.wow.content_update_notes", "worldofwarcraft.blizzard.com",
        "/en-us/content-update-notes", "", "text/html", 1_048_576,
        "none", etag, last_modified,
    )


def plan_game_data_api(path: str, namespace: str, *, locale: str = "en_US",
                       etag: str | None = None, last_modified: str | None = None) -> OfficialRequestPlan:
    """Plan an authenticated official API GET without accepting a credential."""
    if not isinstance(path, str) or _API_PATH.fullmatch(path) is None or "//" in path or "/../" in path or path.endswith("/.."):
        raise OfficialSourceRequestError("api_path_invalid")
    if not isinstance(namespace, str) or _NAMESPACE.fullmatch(namespace) is None:
        raise OfficialSourceRequestError("namespace_invalid")
    if locale != "en_US":
        raise OfficialSourceRequestError("locale_invalid")
    query = urlencode((("namespace", namespace), ("locale", locale)), quote_via=quote)
    return _plan(
        "blizzard.wow.game_data_api", "us.api.blizzard.com", path, query,
        "application/json", 1_048_576, "external_bearer_required",
        etag, last_modified,
    )
