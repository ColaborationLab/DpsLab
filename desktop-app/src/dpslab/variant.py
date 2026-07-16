"""Versioned, restricted profile variants."""

from __future__ import annotations

import os
import re
import tempfile
import tomllib
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

ALLOWED_OVERRIDE_KEYS = frozenset({"warlock.soul_shards"})
KEY_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*$")


class VariantError(ValueError):
    """A variant is missing, malformed, unsafe, or cannot be materialized."""


@dataclass(frozen=True, slots=True)
class ProfileOverride:
    key: str
    value: str


@dataclass(frozen=True, slots=True)
class ProfileVariant:
    id: str
    name: str
    description: str | None
    overrides: tuple[ProfileOverride, ...]


@dataclass(frozen=True, slots=True)
class LoadedVariant:
    variant: ProfileVariant
    source_file: Path
    source_sha256: str


@dataclass(frozen=True, slots=True)
class AppliedOverride:
    key: str
    value: str
    previous_occurrences: int
    effective_line: str
    order: int
    status: str = "applied"

    def to_dict(self) -> dict[str, Any]:
        return {name: getattr(self, name) for name in self.__dataclass_fields__}


def _digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def _text(table: dict[str, Any], key: str, *, optional: bool = False) -> str | None:
    value = table.get(key)
    if optional and value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise VariantError(f"variant.{key} debe ser texto no vacío")
    return value


def _validate_key(key: str) -> None:
    if not KEY_PATTERN.fullmatch(key) or ".." in key or key.endswith("."):
        raise VariantError(f"Key de override no válida: {key!r}")
    if key not in ALLOWED_OVERRIDE_KEYS:
        raise VariantError(f"Key de override no admitida en esta etapa: {key}")


def load_variant(path: Path) -> LoadedVariant:
    path = path.resolve()
    if not path.is_file():
        raise VariantError(f"No existe el archivo de variante: {path}")
    data = path.read_bytes()
    try:
        document = tomllib.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise VariantError(f"TOML de variante inválido: {path}: {exc}") from exc
    header = document.get("variant")
    raw_overrides = document.get("overrides")
    if not isinstance(header, dict):
        raise VariantError("Falta la tabla [variant]")
    if not isinstance(raw_overrides, list) or not raw_overrides:
        raise VariantError("La variante debe contener al menos un [[overrides]]")
    overrides: list[ProfileOverride] = []
    seen: set[str] = set()
    for raw in raw_overrides:
        if not isinstance(raw, dict):
            raise VariantError("Cada override debe ser una tabla")
        key, value = raw.get("key"), raw.get("value")
        if not isinstance(key, str) or not key:
            raise VariantError("overrides.key debe ser texto no vacío")
        _validate_key(key)
        if key in seen:
            raise VariantError(f"Key duplicada en la variante: {key}")
        if not isinstance(value, str) or any(ord(char) < 32 or ord(char) == 127 for char in value):
            raise VariantError(f"Valor no válido para {key}")
        seen.add(key)
        overrides.append(ProfileOverride(key, value))
    variant = ProfileVariant(
        id=_text(header, "id") or "",
        name=_text(header, "name") or "",
        description=_text(header, "description", optional=True),
        overrides=tuple(overrides),
    )
    return LoadedVariant(variant, path, _digest(data))


def _newline(data: bytes) -> bytes:
    return b"\r\n" if data.count(b"\r\n") > data.count(b"\n") - data.count(b"\r\n") else b"\n"


def create_effective_profile(
    base_bytes: bytes, loaded: LoadedVariant, destination: Path
) -> tuple[str, tuple[AppliedOverride, ...]]:
    newline = _newline(base_bytes)
    separator = b"" if base_bytes.endswith((b"\n", b"\r")) else newline
    text = base_bytes.decode("utf-8", errors="strict")
    applied = tuple(
        AppliedOverride(
            override.key,
            override.value,
            len(re.findall(rf"(?m)^\s*{re.escape(override.key)}\s*=", text)),
            f"{override.key}={override.value}",
            index,
        )
        for index, override in enumerate(loaded.variant.overrides, 1)
    )
    lines = [
        "# DpsLab Effective Profile",
        "# Base SimC addon checksum applies only to the original profile prefix.",
        f"# DpsLab Profile Variant: {loaded.variant.id}",
        *(item.effective_line for item in applied),
        "",
    ]
    output = base_bytes + separator + newline.join(line.encode("utf-8") for line in lines)
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile("wb", dir=destination.parent, prefix=".effective_profile.", suffix=".tmp", delete=False) as stream:
            temporary = stream.name
            stream.write(output)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
        temporary = None
    finally:
        if temporary is not None:
            Path(temporary).unlink(missing_ok=True)
    return _digest(destination.read_bytes()), applied
