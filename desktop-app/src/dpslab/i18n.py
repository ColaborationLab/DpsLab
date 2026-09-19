"""Small, deterministic translation catalog for the user-facing suite text.

Payloads, character names, realms, talent strings, paths and SimulationCraft
output deliberately stay outside this catalog. Missing keys fail back to
English so a partial translation cannot break the UI.
"""
from __future__ import annotations

from importlib import import_module
import locale as system_locale
from string import Formatter
from typing import Mapping

SUPPORTED_LOCALES = ("es", "en", "pt-BR")
DEFAULT_LOCALE = "en"


def normalize_locale(value: str | None) -> str:
    value = (value or "").replace("_", "-").lower()
    if value in {"es", "es-es", "es-mx", "eses", "esmx"}:
        return "es"
    if value in {"pt", "pt-br", "ptbr"}:
        return "pt-BR"
    return "en"


def resolved_locale(value: str | None = None) -> str:
    """Resolve Auto using the host locale, with English as a safe fallback."""
    if value not in (None, "", "auto"):
        return normalize_locale(value)
    try:
        host_locale = system_locale.getlocale()[0]
    except (ValueError, TypeError):
        host_locale = None
    return normalize_locale(host_locale)


def _catalog(locale: str) -> Mapping[str, str]:
    module_name = {"es": "es", "pt-BR": "pt_BR"}.get(locale, "en")
    return import_module(f".locales.{module_name}", __package__).MESSAGES


def messages(locale: str | None = None) -> Mapping[str, str]:
    """Return a read-only-by-convention catalog with English fallback."""
    selected_locale = resolved_locale(locale)
    selected = _catalog(selected_locale)
    if selected_locale == DEFAULT_LOCALE:
        return selected
    return {**_catalog(DEFAULT_LOCALE), **selected}


def tr(key: str, locale: str | None = None, **values: object) -> str:
    """Translate a stable key and format only its declared placeholders."""
    text = messages(locale).get(key, _catalog(DEFAULT_LOCALE).get(key, key))
    return text.format(**values) if values else text


def placeholders(text: str) -> frozenset[str]:
    return frozenset(name for _, name, _, _ in Formatter().parse(text) if name)
