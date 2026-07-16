"""Parser enfocado en exportaciones de perfiles del addon SimulationCraft."""

from __future__ import annotations

import re
from hashlib import sha256
from pathlib import Path

from .models import Character, GearItem, SavedLoadout, Snapshot


class ProfileParseError(ValueError):
    """Raised when a SimC profile is missing or structurally invalid."""


_LOADOUT_RE = re.compile(r"^# Saved Loadout:\s*(?P<name>.+?)\s*$")
_ITEM_NAME_RE = re.compile(r"^#\s+(?P<name>.+?)\s+\((?P<level>\d+)\)\s*$")
_ASSIGNMENT_RE = re.compile(r"^(?P<key>[A-Za-z][A-Za-z0-9_]*)=(?P<value>.*)$")
_CHARACTER_KEYS = {"level", "race", "region", "server", "spec", "role", "professions"}
_CHECKSUM_RE = re.compile(r"^# Checksum:\s*(?P<checksum>\S+)\s*$")


def _clean_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1]
    return value


def _parse_professions(value: str) -> dict[str, int]:
    professions: dict[str, int] = {}
    if not value:
        return professions
    for entry in value.split("/"):
        try:
            name, raw_level = entry.split("=", 1)
            professions[name] = int(raw_level)
        except (ValueError, TypeError) as exc:
            raise ProfileParseError(f"Profesión inválida: {entry!r}") from exc
    return professions


def _source_name(path: Path) -> str:
    """Return a portable project-relative source name when possible."""
    parts = path.parts
    lowered = [part.lower() for part in parts]
    if "profiles" in lowered:
        index = len(lowered) - 1 - lowered[::-1].index("profiles")
        return Path(*parts[index:]).as_posix()
    return path.name


def _parse_item(line: str, name: str | None, item_level: int | None) -> GearItem:
    match = _ASSIGNMENT_RE.match(line)
    if match is None:
        raise ProfileParseError(f"Línea de equipo inválida: {line!r}")

    slot = match.group("key")
    raw_parts = match.group("value").split(",")
    attributes: dict[str, str] = {}
    for part in raw_parts:
        part = part.strip()
        if not part:
            continue
        if "=" not in part:
            raise ProfileParseError(f"Atributo de equipo inválido en {line!r}: {part!r}")
        key, value = part.split("=", 1)
        attributes[key] = value

    try:
        item_id = int(attributes.pop("id"))
    except KeyError as exc:
        raise ProfileParseError(f"El objeto de {slot!r} no contiene id") from exc
    except ValueError as exc:
        raise ProfileParseError(f"El objeto de {slot!r} tiene un id no numérico") from exc

    return GearItem(
        slot=slot,
        name=name,
        item_level=item_level,
        item_id=item_id,
        attributes=attributes,
    )


def parse_profile(path: Path) -> Snapshot:
    """Read and parse a UTF-8 SimulationCraft profile from *path*."""
    if path.suffix.lower() != ".simc":
        raise ProfileParseError(f"Se esperaba un archivo .simc, no {path.name!r}")
    try:
        source_bytes = path.read_bytes()
        text = source_bytes.decode("utf-8")
    except FileNotFoundError as exc:
        raise ProfileParseError(f"No existe el perfil: {path}") from exc
    except UnicodeDecodeError as exc:
        raise ProfileParseError(f"El perfil no es UTF-8 válido: {path}") from exc
    except OSError as exc:
        raise ProfileParseError(f"No se pudo leer el perfil {path}: {exc}") from exc
    return parse_profile_text(
        text,
        source_file=_source_name(path),
        source_sha256=sha256(source_bytes).hexdigest(),
    )


def parse_profile_text(
    text: str,
    *,
    source_file: str = "<memory>",
    source_sha256: str | None = None,
) -> Snapshot:
    """Parse the subset of SimC syntax needed by the initial DpsLab snapshot."""
    character_values: dict[str, str] = {}
    character_class: str | None = None
    character_name: str | None = None
    active_talents: str | None = None
    loot_spec: str | None = None
    simc_checksum: str | None = None
    saved_loadouts: list[SavedLoadout] = []
    equipped: list[GearItem] = []
    bags: list[GearItem] = []
    unparsed_fields: list[str] = []

    in_bags = False
    after_bags = False
    pending_loadout: str | None = None
    pending_item_name: str | None = None
    pending_item_level: int | None = None

    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if stripped == "### Gear from Bags":
            in_bags = True
            after_bags = False
            pending_item_name = None
            pending_item_level = None
            continue
        if in_bags and stripped.startswith("### "):
            in_bags = False
            after_bags = True
            pending_item_name = None
            pending_item_level = None
        if not stripped:
            continue

        checksum_match = _CHECKSUM_RE.match(stripped)
        if checksum_match:
            simc_checksum = checksum_match.group("checksum")
            continue
        if stripped.startswith("# loot_spec="):
            loot_spec = _clean_value(stripped.removeprefix("# loot_spec="))
            continue

        loadout_match = _LOADOUT_RE.match(stripped)
        if loadout_match and not in_bags:
            pending_loadout = loadout_match.group("name")
            continue
        if pending_loadout is not None:
            if stripped.startswith("# talents="):
                saved_loadouts.append(
                    SavedLoadout(pending_loadout, stripped.removeprefix("# talents=").strip())
                )
                pending_loadout = None
                continue
            if not stripped.startswith("#"):
                unparsed_fields.append(f"loadout:{pending_loadout}")
                pending_loadout = None

        item_match = _ITEM_NAME_RE.match(stripped)
        if item_match and not after_bags:
            pending_item_name = item_match.group("name")
            pending_item_level = int(item_match.group("level"))
            continue

        if in_bags and stripped.startswith("# "):
            candidate = stripped[2:].strip()
            if _ASSIGNMENT_RE.match(candidate):
                bags.append(_parse_item(candidate, pending_item_name, pending_item_level))
                pending_item_name = None
                pending_item_level = None
            continue

        if stripped.startswith("#") or after_bags:
            continue

        assignment = _ASSIGNMENT_RE.match(stripped)
        if assignment is None:
            unparsed_fields.append(stripped)
            continue
        key = assignment.group("key")
        value = _clean_value(assignment.group("value"))

        if key in _CHARACTER_KEYS:
            character_values[key] = value
        elif key == "talents":
            active_talents = value
        elif not value.startswith(",") and character_class is None:
            character_class = key
            character_name = value
        elif value.startswith(","):
            equipped.append(_parse_item(stripped, pending_item_name, pending_item_level))
            pending_item_name = None
            pending_item_level = None
        else:
            unparsed_fields.append(key)

    required = {
        "name": character_name,
        "class": character_class,
        "level": character_values.get("level"),
        "race": character_values.get("race"),
        "region": character_values.get("region"),
        "server": character_values.get("server"),
        "spec": character_values.get("spec"),
        "role": character_values.get("role"),
        "professions": character_values.get("professions"),
        "talents": active_talents,
    }
    missing = [key for key, value in required.items() if value is None]
    if missing:
        raise ProfileParseError(f"Faltan campos obligatorios: {', '.join(missing)}")
    try:
        level = int(character_values["level"])
    except ValueError as exc:
        raise ProfileParseError("El nivel del personaje no es numérico") from exc

    return Snapshot(
        schema_version="0.1",
        source_file=source_file,
        source_sha256=source_sha256 or sha256(text.encode("utf-8")).hexdigest(),
        simc_checksum=simc_checksum,
        character=Character(
            name=character_name or "",
            region=character_values["region"],
            realm=character_values["server"],
            character_class=character_class or "",
            specialization=character_values["spec"],
            level=level,
            race=character_values["race"],
            role=character_values["role"],
            professions=_parse_professions(character_values["professions"]),
            loot_spec=loot_spec,
        ),
        active_talent_hash=active_talents or "",
        saved_loadouts=saved_loadouts,
        equipped_gear=equipped,
        bag_gear=bags,
        unparsed_fields=sorted(set(unparsed_fields)),
    )
