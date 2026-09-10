"""Read actual Balance stat weights from a completed SimulationCraft JSON report."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path


class BalanceStatWeightsError(ValueError):
    pass


_KEYS = (("intellect", "Intellect"), ("int", "Intellect"), ("crit_rating", "CritRating"), ("haste_rating", "HasteRating"), ("mastery_rating", "MasteryRating"), ("versatility_rating", "VersatilityRating"))


@dataclass(frozen=True, repr=False)
class BalanceStatWeights:
    values: tuple[tuple[str, float], ...]

    def pawn_compatible(self) -> str:
        return "Pawn-compatible: " + ", ".join(f"{name}={value:.3f}" for name, value in self.values)

    def score_item(self, stats: tuple[tuple[str, int], ...]) -> float:
        factors = dict(self.values)
        return sum(factors.get(name, 0.0) * amount for name, amount in stats)


def load_balance_stat_weights(run_dir: Path) -> BalanceStatWeights | None:
    try:
        document = json.loads((run_dir / "simc.json").read_text(encoding="utf-8"))
        player = document["sim"]["players"][0]
        factors = player["scale_factors"]
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, KeyError, IndexError, TypeError):
        return None
    if not isinstance(factors, dict):
        return None
    values = []
    seen = set()
    for source, target in _KEYS:
        value = factors.get(source)
        if target in seen or isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            continue
        values.append((target, float(value)))
        seen.add(target)
    return BalanceStatWeights(tuple(values)) if values else None
