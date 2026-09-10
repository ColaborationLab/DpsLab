"""Player-requested local storage for completed Balance comparison summaries."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import tempfile
import time
from uuid import uuid4

from .druid_balance_recommendation import DruidBalanceComparison


class BalanceComparisonLibraryError(ValueError):
    pass


@dataclass(frozen=True, repr=False)
class BalanceComparisonCase:
    case_id: str
    title: str
    saved_at: int
    export_text: str
    message: str
    loadouts: tuple[tuple[int, float], ...]
    preferred_loadout: int


def _directory(root: Path) -> Path:
    if not root.is_absolute():
        raise BalanceComparisonLibraryError("balance_library_root_invalid")
    return root / "balance-library"


def _document(case: BalanceComparisonCase) -> dict[str, object]:
    return {"case_id": case.case_id, "export_text": case.export_text, "loadouts": [[identifier, dps] for identifier, dps in case.loadouts], "message": case.message, "preferred_loadout": case.preferred_loadout, "saved_at": case.saved_at, "schema_version": "0.1", "title": case.title}


def save_case(root: Path, title: str, export_text: str, comparison: DruidBalanceComparison, *, now: int | None = None) -> BalanceComparisonCase:
    if not isinstance(title, str) or not 1 <= len(title.strip()) <= 80 or not isinstance(export_text, str) or not 1 <= len(export_text) <= 65_536 or not isinstance(comparison, DruidBalanceComparison):
        raise BalanceComparisonLibraryError("balance_library_input_invalid")
    saved_at = int(time.time()) if now is None else now
    if not isinstance(saved_at, int) or isinstance(saved_at, bool) or saved_at < 1:
        raise BalanceComparisonLibraryError("balance_library_input_invalid")
    case = BalanceComparisonCase(uuid4().hex, title.strip(), saved_at, export_text, comparison.message, comparison.loadouts, comparison.preferred_loadout)
    directory = _directory(root)
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / f"{case.case_id}.json"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=directory, prefix=".case-", suffix=".tmp", delete=False) as temporary:
        temporary.write(json.dumps(_document(case), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
        temporary_name = temporary.name
    os.replace(temporary_name, destination)
    return case


def _read(path: Path) -> BalanceComparisonCase:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict) or set(value) != {"case_id", "export_text", "loadouts", "message", "preferred_loadout", "saved_at", "schema_version", "title"} or value["schema_version"] != "0.1":
            raise ValueError
        loadouts = tuple((identifier, float(dps)) for identifier, dps in value["loadouts"])
        if not all(isinstance(identifier, int) and not isinstance(identifier, bool) and isinstance(dps, (int, float)) and not isinstance(dps, bool) and dps > 0 for identifier, dps in loadouts):
            raise ValueError
        case = BalanceComparisonCase(value["case_id"], value["title"], value["saved_at"], value["export_text"], value["message"], loadouts, value["preferred_loadout"])
        if not isinstance(case.case_id, str) or len(case.case_id) != 32 or not isinstance(case.title, str) or not 1 <= len(case.title) <= 80 or not isinstance(case.saved_at, int) or not isinstance(case.export_text, str) or not isinstance(case.message, str) or not isinstance(case.preferred_loadout, int) or len(case.loadouts) not in range(2, 5):
            raise ValueError
        return case
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise BalanceComparisonLibraryError("balance_library_case_invalid") from exc


def list_cases(root: Path) -> tuple[BalanceComparisonCase, ...]:
    directory = _directory(root)
    if not directory.is_dir():
        return ()
    try:
        paths = sorted(directory.glob("*.json"))
    except OSError as exc:
        raise BalanceComparisonLibraryError("balance_library_unavailable") from exc
    return tuple(sorted((_read(path) for path in paths), key=lambda case: case.saved_at, reverse=True))
