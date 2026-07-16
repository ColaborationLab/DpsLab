"""Modelos de datos del snapshot de un perfil SimulationCraft."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Character:
    name: str
    region: str
    realm: str
    character_class: str
    specialization: str
    level: int
    race: str
    role: str
    professions: dict[str, int]
    loot_spec: str | None = None


@dataclass(frozen=True, slots=True)
class SavedLoadout:
    name: str
    talent_hash: str


@dataclass(frozen=True, slots=True)
class GearItem:
    slot: str
    name: str | None
    item_level: int | None
    item_id: int
    attributes: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Snapshot:
    schema_version: str
    source_file: str
    source_sha256: str
    simc_checksum: str | None
    character: Character
    active_talent_hash: str
    saved_loadouts: list[SavedLoadout]
    equipped_gear: list[GearItem]
    bag_gear: list[GearItem]
    unparsed_fields: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert the complete dataclass tree to JSON-compatible values."""
        return asdict(self)
