"""Modelos, lectura y validación de escenarios reproducibles."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any


class ScenarioError(ValueError):
    """Raised when a scenario file is missing or invalid."""


@dataclass(frozen=True, slots=True)
class PrecisionSettings:
    target_error: float | None
    iterations: int


@dataclass(frozen=True, slots=True)
class Scenario:
    id: str
    name: str
    description: str
    fight_style: str
    desired_targets: int
    max_time: int
    vary_combat_length: float
    precision: PrecisionSettings


@dataclass(frozen=True, slots=True)
class LoadedScenario:
    scenario: Scenario
    source_file: Path
    source_sha256: str


def _table(document: dict[str, Any], name: str) -> dict[str, Any]:
    value = document.get(name)
    if not isinstance(value, dict):
        raise ScenarioError(f"Falta la tabla [{name}] del escenario")
    return value


def _text(table: dict[str, Any], key: str, *, allow_empty: bool = False) -> str:
    value = table.get(key)
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        raise ScenarioError(f"{key} debe ser texto no vacío")
    return value


def _integer(table: dict[str, Any], key: str) -> int:
    value = table.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ScenarioError(f"{key} debe ser un entero")
    return value


def _number(table: dict[str, Any], key: str, *, optional: bool = False) -> float | None:
    value = table.get(key)
    if value is None and optional:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ScenarioError(f"{key} debe ser numérico")
    return float(value)


def load_scenario(path: Path) -> LoadedScenario:
    """Read, hash and validate one UTF-8 TOML scenario without modifying it."""
    try:
        source = path.read_bytes()
    except FileNotFoundError as exc:
        raise ScenarioError(f"No existe el escenario: {path}") from exc
    except OSError as exc:
        raise ScenarioError(f"No se pudo leer el escenario {path}: {exc}") from exc
    try:
        document = tomllib.loads(source.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise ScenarioError(f"El escenario no contiene TOML UTF-8 válido: {path}: {exc}") from exc

    scenario_data = _table(document, "scenario")
    precision_data = _table(document, "precision")
    desired_targets = _integer(scenario_data, "desired_targets")
    max_time = _integer(scenario_data, "max_time")
    vary_combat_length = _number(scenario_data, "vary_combat_length")
    iterations = _integer(precision_data, "iterations")
    target_error = _number(precision_data, "target_error", optional=True)

    if desired_targets < 1:
        raise ScenarioError("desired_targets debe ser mayor o igual que 1")
    if max_time <= 0:
        raise ScenarioError("max_time debe ser mayor que cero")
    if vary_combat_length is None or not 0 <= vary_combat_length <= 1:
        raise ScenarioError("vary_combat_length debe estar entre 0 y 1")
    if iterations < 0:
        raise ScenarioError("iterations debe ser mayor o igual que cero")
    if iterations == 0 and (target_error is None or target_error <= 0):
        raise ScenarioError("target_error debe ser mayor que cero cuando iterations es 0")
    if target_error is not None and target_error <= 0:
        raise ScenarioError("target_error debe ser mayor que cero")

    scenario = Scenario(
        id=_text(scenario_data, "id"),
        name=_text(scenario_data, "name"),
        description=_text(scenario_data, "description", allow_empty=True),
        fight_style=_text(scenario_data, "fight_style"),
        desired_targets=desired_targets,
        max_time=max_time,
        vary_combat_length=vary_combat_length,
        precision=PrecisionSettings(target_error=target_error, iterations=iterations),
    )
    return LoadedScenario(scenario, path.resolve(), sha256(source).hexdigest())

