"""Pure rows for the loadout comparison table."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from .loadout_recommendation import LoadoutComparison


_STATS = (
    ("CritRating", "Crítico"),
    ("HasteRating", "Celeridad"),
    ("MasteryRating", "Maestría"),
    ("VersatilityRating", "Versatilidad"),
)
_PRIMARY = (("Intellect", "Intelecto"), ("Agility", "Agilidad"), ("Strength", "Fuerza"))
_ALIASES = {
    "Crit": "CritRating", "CriticalStrike": "CritRating",
    "Haste": "HasteRating", "Mastery": "MasteryRating",
    "Vers": "VersatilityRating", "Versatility": "VersatilityRating",
    "Int": "Intellect", "Agi": "Agility", "Str": "Strength",
}


@dataclass(frozen=True, repr=False)
class ComparisonCell:
    text: str
    value: float | None
    delta: str = ""


@dataclass(frozen=True, repr=False)
class ComparisonRow:
    label: str
    source: str
    cells: tuple[ComparisonCell, ...]
    highlighted: bool = False


@dataclass(frozen=True, repr=False)
class ComparisonTable:
    columns: tuple[str, ...]
    rows: tuple[ComparisonRow, ...]


def _number(value: float, suffix: str = "") -> str:
    return f"{value:,.1f}{suffix}" if value % 1 else f"{value:,.0f}{suffix}"


def _dps_delta(values: tuple[float | None, ...], reference: float | None = None) -> tuple[str, ...]:
    if reference is None:
        reference = max((value for value in values if value is not None), default=None)
    return tuple("" if value is None or reference is None or reference <= 0 or value == reference else f"{(value / reference - 1) * 100:+.2f} %" for value in values)


def _highlight(values: tuple[float | None, ...]) -> bool:
    numeric = tuple(value for value in values if value is not None)
    return len(numeric) > 1 and max(numeric) != min(numeric)


def _columns(comparison: LoadoutComparison, names: Mapping[int, str]) -> tuple[int, ...]:
    return tuple(identifier for identifier, _ in comparison.loadouts[:4])


def _column_names(ids: tuple[int, ...], names: Mapping[int, str], scores: Mapping[int, float]) -> tuple[str, ...]:
    labels = tuple(names.get(identifier, f"Loadout {identifier}") for identifier in ids)
    best = max(scores.get(identifier, float("-inf")) for identifier in ids)
    return tuple(
        (f"{label} [{identifier}]" if labels.count(label) > 1 else label) + (" — Mayor DPS" if scores.get(identifier) == best else "")
        for identifier, label in zip(ids, labels)
    )


def _equipment_stats(equipped: Iterable[object]) -> Mapping[str, float]:
    totals: dict[str, float] = {}
    for item in equipped:
        for name, value in getattr(item, "stats", ()):
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                canonical = _ALIASES.get(name, name)
                totals[canonical] = totals.get(canonical, 0.0) + float(value)
    return totals


def comparison_table(comparison: LoadoutComparison, names: Mapping[int, str], equipped: Iterable[object] = (), reference_id: int | None = None) -> ComparisonTable:
    """Present known equipment, per-build SimC weights and DPS without inventing values."""
    ids = _columns(comparison, names)
    if not ids:
        return ComparisonTable((), ())
    scores = dict(comparison.loadouts)
    columns = _column_names(ids, names, scores)
    if reference_id in ids:
        columns = tuple(label + (" — Referencia" if identifier == reference_id else "") for identifier, label in zip(ids, columns))
    equipment = _equipment_stats(equipped)
    weights = {item.build_id: dict(item.values) for item in comparison.score_weights if item.build_id is not None}
    dps = tuple(scores.get(identifier) for identifier in ids)
    rows: list[ComparisonRow] = [ComparisonRow(
        f"{comparison.metric} resultante", "Resultado de SimulationCraft; diferencia porcentual frente a la referencia elegida o al máximo simulado",
        tuple(ComparisonCell("N/D" if value is None else _number(value), value, delta) for value, delta in zip(dps, _dps_delta(dps, scores.get(reference_id) if reference_id in ids else None))), _highlight(dps)
    )]
    for key, label in _PRIMARY + _STATS:
        weight_values = tuple(weights.get(identifier, {}).get(key) for identifier in ids)
        greatest = max((value for value in weight_values if value is not None), default=None)
        equipment_value = equipment.get(key)
        cells = tuple(
            ComparisonCell(
                "\n".join(
                    ([f"Equipo: {_number(equipment_value)}"] if equipment_value is not None else [])
                    + [f"Peso: {_number(weight)}" if weight is not None else "Peso: N/D"]
                    + (["Mayor peso"] if weight == greatest and greatest is not None else [])
                ) if equipment_value is not None or weight is not None else "N/D",
                weight,
            )
            for weight in weight_values
        )
        rows.append(ComparisonRow(label, "Equipo exportado y peso de SimulationCraft", cells, _highlight(weight_values)))
    return ComparisonTable(columns, tuple(rows))
