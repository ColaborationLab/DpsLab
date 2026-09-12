"""Player-requested local storage for completed class/spec loadout comparisons."""
from __future__ import annotations

from dataclasses import dataclass
import json
import math
import os
from pathlib import Path
import tempfile
import time
from uuid import uuid4

from .loadout_recommendation import LoadoutComparison


class LoadoutComparisonLibraryError(ValueError):
    pass


@dataclass(frozen=True, repr=False)
class LoadoutComparisonCase:
    case_id: str
    title: str
    saved_at: int
    export_text: str
    comparison: LoadoutComparison


def _directory(root: Path) -> Path:
    if not root.is_absolute():
        raise LoadoutComparisonLibraryError("loadout_library_root_invalid")
    return root / "loadout-library"


def _valid(comparison: object) -> bool:
    return isinstance(comparison, LoadoutComparison) and comparison.metric == "DPS" and comparison.role in {"damage", "tank", "healer"} and len(comparison.loadouts) in range(1, 5) and all(isinstance(identifier, int) and isinstance(value, float) and math.isfinite(value) and value > 0 for identifier, value in comparison.loadouts)


def _document(case: LoadoutComparisonCase) -> dict[str, object]:
    comparison = case.comparison
    return {"case_id": case.case_id, "class_id": comparison.class_id, "export_text": case.export_text, "loadouts": [[identifier, value] for identifier, value in comparison.loadouts], "message": comparison.message, "metric": comparison.metric, "preferred_loadout": comparison.preferred_loadout, "role": comparison.role, "saved_at": case.saved_at, "schema_version": "0.1", "specialization_id": comparison.specialization_id, "title": case.title}


def save_case(root: Path, title: str, export_text: str, comparison: LoadoutComparison, *, now: int | None = None) -> LoadoutComparisonCase:
    saved_at = int(time.time()) if now is None else now
    if not isinstance(title, str) or not 1 <= len(title.strip()) <= 80 or not isinstance(export_text, str) or not 1 <= len(export_text) <= 65_536 or not _valid(comparison) or not isinstance(saved_at, int) or isinstance(saved_at, bool) or saved_at < 1:
        raise LoadoutComparisonLibraryError("loadout_library_input_invalid")
    case = LoadoutComparisonCase(uuid4().hex, title.strip(), saved_at, export_text, comparison)
    directory = _directory(root); directory.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=directory, prefix=".case-", suffix=".tmp", delete=False) as temporary:
        temporary.write(json.dumps(_document(case), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
        name = temporary.name
    os.replace(name, directory / f"{case.case_id}.json")
    return case


def _read(path: Path) -> LoadoutComparisonCase:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        fields = {"case_id", "class_id", "export_text", "loadouts", "message", "metric", "preferred_loadout", "role", "saved_at", "schema_version", "specialization_id", "title"}
        if not isinstance(value, dict) or set(value) != fields or value["schema_version"] != "0.1": raise ValueError
        loadouts = tuple((identifier, float(score)) for identifier, score in value["loadouts"])
        comparison = LoadoutComparison(value["message"], loadouts, value["preferred_loadout"], value["class_id"], value["specialization_id"], value["role"], value["metric"])
        case = LoadoutComparisonCase(value["case_id"], value["title"], value["saved_at"], value["export_text"], comparison)
        if not _valid(comparison) or not isinstance(case.case_id, str) or len(case.case_id) != 32 or not isinstance(case.title, str) or not 1 <= len(case.title) <= 80 or not isinstance(case.saved_at, int) or not isinstance(case.export_text, str): raise ValueError
        return case
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise LoadoutComparisonLibraryError("loadout_library_case_invalid") from exc


def list_cases(root: Path) -> tuple[LoadoutComparisonCase, ...]:
    directory = _directory(root)
    if not directory.is_dir(): return ()
    try:
        return tuple(sorted((_read(path) for path in directory.glob("*.json")), key=lambda case: case.saved_at, reverse=True))
    except OSError as exc:
        raise LoadoutComparisonLibraryError("loadout_library_unavailable") from exc
