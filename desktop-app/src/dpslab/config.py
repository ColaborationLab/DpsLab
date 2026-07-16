"""Resolución de configuración local para SimulationCraft."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .scenario import LoadedScenario
from .variant import LoadedVariant


SIMC_ENV_VAR = "DPSLAB_SIMC_EXE"
DEFAULT_TIMEOUT_SECONDS = 600.0
DEFAULT_THREADS = 4


class ConfigurationError(ValueError):
    """Raised when local SimulationCraft configuration is invalid."""


@dataclass(frozen=True, slots=True)
class SimulationConfig:
    simc_exe: Path
    runs_dir: Path
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    threads: int = DEFAULT_THREADS
    generate_html: bool = False
    iterations: int | None = None
    max_time: int | None = None
    vary_combat_length: float | None = None
    fight_style: str | None = None
    desired_targets: int | None = None
    target_error: float | None = None
    scenario: LoadedScenario | None = None
    variant: LoadedVariant | None = None
    seed: int | None = None
    executable_source: str = "local_config"


def project_root() -> Path:
    """Return the repository root from the installed source layout."""
    return Path(__file__).resolve().parents[3]


def _read_local_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with path.open("rb") as stream:
            document = tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ConfigurationError(f"No se pudo leer la configuración {path}: {exc}") from exc
    section = document.get("simulationcraft", {})
    if not isinstance(section, dict):
        raise ConfigurationError("La sección [simulationcraft] debe ser una tabla TOML")
    return section


def _resolved_path(value: str | Path, *, base: Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def resolve_simulation_config(
    *,
    explicit_simc_exe: Path | None = None,
    environ: Mapping[str, str] | None = None,
    root: Path | None = None,
    timeout_seconds: float | None = None,
    generate_html: bool | None = None,
    runs_dir: Path | None = None,
    threads: int | None = None,
    iterations: int | None = None,
    max_time: int | None = None,
    vary_combat_length: float | None = None,
    fight_style: str | None = None,
    desired_targets: int | None = None,
    target_error: float | None = None,
    scenario: LoadedScenario | None = None,
    variant: LoadedVariant | None = None,
    seed: int | None = None,
) -> SimulationConfig:
    """Resolve config using CLI, environment, then local TOML precedence."""
    root = (root or project_root()).resolve()
    environment = environ if environ is not None else os.environ
    local_path = root / "config" / "dpslab.local.toml"
    local = _read_local_config(local_path)

    exe_value: str | Path | None = explicit_simc_exe
    executable_source = "explicit_cli"
    if exe_value is None:
        exe_value = environment.get(SIMC_ENV_VAR) or None
        executable_source = "environment"
    if exe_value is None:
        local_value = local.get("simc_exe")
        if local_value is not None and not isinstance(local_value, str):
            raise ConfigurationError("simulationcraft.simc_exe debe ser texto")
        exe_value = local_value or None
        executable_source = "local_config"
    if exe_value is None:
        raise ConfigurationError(
            "No se configuró simc.exe. Usa --simc-exe, la variable "
            f"{SIMC_ENV_VAR} o {local_path}."
        )

    simc_exe = _resolved_path(exe_value, base=root)
    if not simc_exe.is_file():
        raise ConfigurationError(f"No existe simc.exe en la ruta configurada: {simc_exe}")

    raw_timeout = timeout_seconds if timeout_seconds is not None else local.get(
        "timeout_seconds", DEFAULT_TIMEOUT_SECONDS
    )
    if isinstance(raw_timeout, bool) or not isinstance(raw_timeout, (int, float)):
        raise ConfigurationError("simulationcraft.timeout_seconds debe ser numérico")
    resolved_timeout = float(raw_timeout)
    if resolved_timeout <= 0:
        raise ConfigurationError("El timeout debe ser mayor que cero")

    raw_threads = threads if threads is not None else local.get("threads", DEFAULT_THREADS)
    if isinstance(raw_threads, bool) or not isinstance(raw_threads, int):
        raise ConfigurationError("threads debe ser un entero")
    resolved_threads = raw_threads
    if isinstance(resolved_threads, bool) or resolved_threads <= 0:
        raise ConfigurationError("threads debe ser un entero mayor que cero")

    scenario_values = scenario.scenario if scenario is not None else None
    resolved_iterations = (
        iterations
        if iterations is not None
        else scenario_values.precision.iterations if scenario_values is not None else None
    )
    if target_error is not None:
        resolved_target_error = target_error
    elif iterations is not None and iterations > 0:
        resolved_target_error = None
    elif scenario_values is not None:
        resolved_target_error = scenario_values.precision.target_error
    else:
        resolved_target_error = None
    resolved_max_time = (
        max_time if max_time is not None else scenario_values.max_time if scenario_values else None
    )
    resolved_vary = (
        vary_combat_length
        if vary_combat_length is not None
        else scenario_values.vary_combat_length if scenario_values else None
    )
    resolved_fight_style = (
        fight_style if fight_style is not None else scenario_values.fight_style if scenario_values else None
    )
    resolved_targets = (
        desired_targets
        if desired_targets is not None
        else scenario_values.desired_targets if scenario_values else None
    )

    if resolved_iterations is not None and (
        isinstance(resolved_iterations, bool) or resolved_iterations < 0
    ):
        raise ConfigurationError("iterations debe ser un entero mayor o igual que cero")
    if resolved_iterations == 0 and (
        resolved_target_error is None or resolved_target_error <= 0
    ):
        raise ConfigurationError("target_error debe ser mayor que cero cuando iterations es 0")
    if resolved_target_error is not None and resolved_target_error <= 0:
        raise ConfigurationError("target_error debe ser mayor que cero")
    if resolved_max_time is not None and (
        isinstance(resolved_max_time, bool) or resolved_max_time <= 0
    ):
        raise ConfigurationError("max_time debe ser un entero mayor que cero")
    if resolved_vary is not None and not 0 <= resolved_vary <= 1:
        raise ConfigurationError("vary_combat_length debe estar entre 0 y 1")
    if resolved_fight_style is not None and not resolved_fight_style.strip():
        raise ConfigurationError("fight_style debe ser texto no vacío")
    if resolved_targets is not None and resolved_targets < 1:
        raise ConfigurationError("desired_targets debe ser mayor o igual que 1")
    if seed is not None and (isinstance(seed, bool) or not isinstance(seed, int) or seed <= 0 or seed > 0x7FFFFFFF):
        raise ConfigurationError("seed debe ser un entero positivo de 31 bits")

    raw_html = generate_html if generate_html is not None else local.get("generate_html", False)
    if not isinstance(raw_html, bool):
        raise ConfigurationError("simulationcraft.generate_html debe ser true o false")

    raw_runs_dir: str | Path = runs_dir or local.get("runs_dir", "results/runs")
    if not isinstance(raw_runs_dir, (str, Path)):
        raise ConfigurationError("simulationcraft.runs_dir debe ser una ruta")

    return SimulationConfig(
        simc_exe=simc_exe,
        runs_dir=_resolved_path(raw_runs_dir, base=root),
        timeout_seconds=resolved_timeout,
        threads=resolved_threads,
        generate_html=raw_html,
        iterations=resolved_iterations,
        max_time=resolved_max_time,
        vary_combat_length=resolved_vary,
        fight_style=resolved_fight_style,
        desired_targets=resolved_targets,
        target_error=resolved_target_error,
        scenario=scenario,
        variant=variant,
        seed=seed,
        executable_source=executable_source,
    )
