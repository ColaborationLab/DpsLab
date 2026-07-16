"""Interpretación tolerante de artefactos producidos por SimulationCraft."""

from __future__ import annotations

import json
import os
import re
import tempfile
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable, Sequence

from .result_models import (
    DpsResult,
    ExecutionResult,
    RunDiagnostics,
    RunIdentification,
    RunScenario,
    RunSummary,
    RunVariant,
    SimcDisplayedError,
    SummaryGeneration,
)


JsonPath = tuple[str | int, ...]


class ResultSummaryError(ValueError):
    """Raised when run artifacts cannot produce a trustworthy summary."""


def _read_json(path: Path, *, label: str, required: bool) -> dict[str, Any]:
    if not path.is_file():
        if required:
            raise ResultSummaryError(f"No existe {label}: {path}")
        return {}
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ResultSummaryError(f"{label} no contiene JSON válido: {path}: {exc}") from exc
    if not isinstance(document, dict):
        raise ResultSummaryError(f"{label} debe contener un objeto JSON: {path}")
    return document


def _at(document: Any, path: JsonPath) -> Any:
    current = document
    for part in path:
        if isinstance(part, int):
            if not isinstance(current, list) or not 0 <= part < len(current):
                return None
            current = current[part]
        else:
            if not isinstance(current, dict) or part not in current:
                return None
            current = current[part]
    return current


def _first(document: Any, paths: Sequence[JsonPath]) -> Any:
    for path in paths:
        value = _at(document, path)
        if value is not None:
            return value
    return None


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _integer(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _string(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def _player(document: dict[str, Any]) -> dict[str, Any]:
    players = _first(document, (("sim", "players"), ("players",)))
    if not isinstance(players, list) or not players or not isinstance(players[0], dict):
        raise ResultSummaryError("El JSON de SimulationCraft no contiene ningún personaje")
    return players[0]


def _class_and_specialization(player: dict[str, Any]) -> tuple[str | None, str | None]:
    character_class = _string(_first(player, (("class",), ("character_class",), ("type",))))
    specialization = _string(_first(player, (("specialization",), ("spec",))))
    if character_class is None and specialization is not None and " " in specialization:
        specialization_parts = specialization.rsplit(" ", 1)
        specialization, character_class = specialization_parts[0], specialization_parts[1]
    return character_class, specialization


def _warnings(stderr: str) -> list[str]:
    return [line for line in stderr.splitlines() if line.strip()]


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _profile_hash_verified(metadata: dict[str, Any], root: Path) -> bool | None:
    before = _string(metadata.get("profile_sha256_before"))
    after = _string(metadata.get("profile_sha256_after"))
    if before is None or after is None:
        return None
    if before.lower() != after.lower():
        return False
    profile_value = _string(metadata.get("profile"))
    if profile_value is not None:
        profile = Path(profile_value)
        if not profile.is_absolute():
            profile = root / profile
        if profile.is_file():
            return _file_sha256(profile).lower() == before.lower()
    return True


def _scenario_hash_data(metadata: dict[str, Any]) -> tuple[str | None, bool | None]:
    before = _string(metadata.get("scenario_sha256_before"))
    after = _string(metadata.get("scenario_sha256_after"))
    recorded = metadata.get("scenario_hash_verified")
    verified = recorded if isinstance(recorded, bool) else None
    if verified is None and before is not None and after is not None:
        verified = before.lower() == after.lower()
    if before is not None and after is not None and before.lower() != after.lower():
        return before, False
    return before or after, verified


def _simc_elapsed_seconds(document: dict[str, Any], stdout: str) -> float | None:
    json_value = _number(
        _first(
            document,
            (
                ("sim", "statistics", "elapsed_time_seconds"),
                ("statistics", "elapsed_time_seconds"),
            ),
        )
    )
    if json_value is not None:
        return json_value
    match = re.search(
        r"^\s*Wall\s*Seconds?\s*[:=]\s*"
        r"(?P<seconds>[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)\s*$",
        stdout,
        re.IGNORECASE | re.MULTILINE,
    )
    if match is None:
        return None
    try:
        return float(match.group("seconds"))
    except ValueError:
        return None


def _total_simulated_combat_seconds(document: dict[str, Any]) -> float | None:
    return _number(
        _first(
            document,
            (
                ("sim", "statistics", "simulation_length", "sum"),
                ("statistics", "simulation_length", "sum"),
            ),
        )
    )


def _iterations_completed(document: dict[str, Any], stdout: str) -> int | None:
    value = _integer(
        _first(document, (("sim", "options", "iterations"), ("options", "iterations")))
    )
    if value is not None:
        return value
    match = re.search(r"^\s*Iterations\s*=\s*(?P<count>\d+)\b", stdout, re.MULTILINE)
    return int(match.group("count")) if match is not None else None


def _simc_displayed_error(document: dict[str, Any], stdout: str) -> SimcDisplayedError | None:
    value = _number(
        _first(
            document,
            (
                ("sim", "players", 0, "collected_data", "dps", "relative_error_percent"),
                ("sim", "players", 0, "collected_data", "dps", "error_percent"),
            ),
        )
    )
    if value is not None:
        return SimcDisplayedError(None, value, "json", "sim.players[0].collected_data.dps.error_percent", "observed_error")
    matches = re.findall(
        r"\bDPS\s*=.*?\bDPS-Error\s*=\s*"
        r"([0-9]+(?:\.[0-9]+)?(?:[eE][+-]?\d+)?)\s*/\s*"
        r"([0-9]+(?:\.[0-9]+)?)\s*%",
        stdout,
        re.IGNORECASE,
    )
    unique = {(float(absolute), float(percent)) for absolute, percent in matches}
    if len(unique) != 1:
        return None
    absolute, percent = unique.pop()
    return SimcDisplayedError(absolute, percent, "stdout", "DPS-Error=<absolute>/<percent>%", "observed_error")


def _atomic_write_json(path: Path, document: dict[str, Any]) -> None:
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=".run_summary.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary_name = temporary.name
            json.dump(document, temporary, ensure_ascii=False, indent=2)
            temporary.write("\n")
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_name, path)
        temporary_name = None
    except OSError as exc:
        raise ResultSummaryError(f"No se pudo escribir el resumen atómicamente: {exc}") from exc
    finally:
        if temporary_name is not None:
            Path(temporary_name).unlink(missing_ok=True)


def summarize_run(run_dir: Path, *, root: Path) -> RunSummary:
    """Read one completed run and atomically create or replace run_summary.json."""
    run_dir = run_dir.resolve()
    root = root.resolve()
    if not run_dir.is_dir():
        raise ResultSummaryError(f"No existe la carpeta de ejecución: {run_dir}")

    simc = _read_json(run_dir / "simc.json", label="simc.json", required=True)
    metadata = _read_json(run_dir / "metadata.json", label="metadata.json", required=False)
    player = _player(simc)
    stderr_path = run_dir / "stderr.txt"
    try:
        stderr = stderr_path.read_text(encoding="utf-8") if stderr_path.is_file() else ""
    except (OSError, UnicodeDecodeError) as exc:
        raise ResultSummaryError(f"No se pudo leer stderr.txt: {exc}") from exc
    stdout_path = run_dir / "stdout.txt"
    try:
        stdout = stdout_path.read_text(encoding="utf-8") if stdout_path.is_file() else ""
    except (OSError, UnicodeDecodeError):
        stdout = ""

    character_class, specialization = _class_and_specialization(player)
    dps_document = _first(
        player,
        (("collected_data", "dps"), ("dps",)),
    )
    if not isinstance(dps_document, dict):
        dps_document = {}

    mean = _number(dps_document.get("mean"))
    mean_error = _number(
        _first(
            dps_document,
            (("mean_error",), ("mean_std_dev",), ("standard_error",), ("error",)),
        )
    )
    relative_error = None
    if mean not in (None, 0.0) and mean_error is not None:
        relative_error = abs(mean_error / mean) * 100

    iterations_parameter = _integer(
        _first(metadata, (("iterations",), ("parameters", "iterations")))
    )
    iteration_mode = None
    if iterations_parameter == 0:
        iteration_mode = "adaptive"
    elif iterations_parameter is not None and iterations_parameter > 0:
        iteration_mode = "fixed"
    iterations_requested = iterations_parameter if iteration_mode == "fixed" else None
    iterations_completed = _iterations_completed(simc, stdout)
    sample_count = _integer(dps_document.get("count"))
    mismatch = (
        iterations_requested != sample_count
        if iteration_mode == "fixed"
        and iterations_requested is not None
        and sample_count is not None
        else None
    )
    completed_mismatch = (
        iterations_completed != sample_count
        if iterations_completed is not None and sample_count is not None
        else None
    )
    warnings = _warnings(stderr)
    if mismatch:
        warnings.append(
            f"Las iteraciones solicitadas ({iterations_requested}) difieren del número de muestras DPS ({sample_count})."
        )
    scenario_sha256, scenario_hash_verified = _scenario_hash_data(metadata)
    scenario_effective = metadata.get("scenario_effective_parameters")
    if not isinstance(scenario_effective, dict):
        scenario_effective = None

    summary = RunSummary(
        schema_version="0.3",
        identification=RunIdentification(
            run_id=_string(metadata.get("run_id")) or run_dir.name,
            simc_version=_string(metadata.get("simc_version"))
            or _string(_first(simc, (("version",), ("simc_version",)))),
            json_report_version=_string(
                _first(simc, (("report_version",), ("json_report_version",)))
            ),
            character=_string(_first(player, (("name",), ("character",)))) or "",
            character_class=character_class,
            specialization=specialization,
            level=_integer(player.get("level")),
        ),
        scenario=RunScenario(
            scenario_id=_string(metadata.get("scenario_id")),
            scenario_name=_string(metadata.get("scenario_name")),
            scenario_file=_string(metadata.get("scenario_file")),
            scenario_sha256=scenario_sha256,
            scenario_hash_verified=scenario_hash_verified,
            profile=_string(metadata.get("profile")),
            threads=_integer(metadata.get("threads"))
            or _integer(_first(simc, (("sim", "options", "threads"),))),
            iteration_mode=iteration_mode,
            iterations_parameter=iterations_parameter,
            iterations_requested=iterations_requested,
            iterations_completed=iterations_completed,
            dps_sample_count=sample_count,
            max_time=_number(metadata.get("max_time"))
            or _number(_first(simc, (("sim", "options", "max_time"),))),
            vary_combat_length=_number(metadata.get("vary_combat_length")),
            fight_style=_string(
                _first(simc, (("sim", "options", "fight_style"), ("options", "fight_style")))
            ),
            desired_targets=_integer(
                _first(simc, (("sim", "options", "desired_targets"), ("options", "desired_targets")))
            ),
            target_error_percent=_number(metadata.get("target_error"))
            or _number(_first(simc, (("sim", "options", "target_error"),))),
            effective_parameters=scenario_effective,
        ),
        variant=RunVariant(
            variant_id=_string(metadata.get("variant_id")),
            variant_name=_string(metadata.get("variant_name")),
            variant_file=_string(metadata.get("variant_file")),
            variant_sha256=_string(metadata.get("variant_sha256_before")) or _string(metadata.get("variant_sha256_after")),
            variant_hash_verified=metadata.get("variant_hash_verified") if isinstance(metadata.get("variant_hash_verified"), bool) else None,
            base_profile=_string(metadata.get("base_profile")) or _string(metadata.get("profile")),
            base_simc_checksum=_string(metadata.get("base_simc_checksum")),
            base_profile_sha256=_string(metadata.get("base_profile_sha256")) or _string(metadata.get("profile_sha256_before")),
            effective_profile=_string(metadata.get("effective_profile")),
            effective_profile_sha256=_string(metadata.get("effective_profile_sha256")),
            overrides=metadata.get("overrides") if isinstance(metadata.get("overrides"), list) else None,
        ),
        dps=DpsResult(
            mean=mean,
            median=_number(dps_document.get("median")),
            min=_number(dps_document.get("min")),
            max=_number(dps_document.get("max")),
            standard_deviation=_number(
                _first(dps_document, (("std_dev",), ("standard_deviation",)))
            ),
            mean_error=mean_error,
            observed_relative_error_percent=relative_error,
            simc_displayed_error=_simc_displayed_error(simc, stdout),
        ),
        execution=ExecutionResult(
            simulation_status=_string(metadata.get("status")),
            duration_seconds=_number(metadata.get("duration_seconds")),
            simc_elapsed_seconds=_simc_elapsed_seconds(simc, stdout),
            total_simulated_combat_seconds=_total_simulated_combat_seconds(simc),
            exit_code=_integer(metadata.get("exit_code")),
        ),
        diagnostics=RunDiagnostics(
            warnings=warnings,
            stderr_nonempty=bool(stderr),
            requested_iterations_differ_from_sample_count=mismatch,
            completed_iterations_differ_from_dps_sample_count=completed_mismatch,
            profile_hash_verified=_profile_hash_verified(metadata, root),
        ),
        summary_generation=SummaryGeneration(status="completed", error=None),
    )
    if not summary.identification.character:
        raise ResultSummaryError("El personaje del JSON de SimulationCraft no tiene nombre")
    _atomic_write_json(run_dir / "run_summary.json", summary.to_dict())
    return summary
