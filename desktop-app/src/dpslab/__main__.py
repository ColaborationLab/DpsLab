"""Command-line entry points for DpsLab."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .config import ConfigurationError, project_root, resolve_simulation_config
from .parser import ProfileParseError, parse_profile
from .result_parser import ResultSummaryError, summarize_run
from .runner import SimulationRunError, run_simulation
from .scenario import ScenarioError, load_scenario
from .variant import VariantError, load_variant


def _arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(description="Herramientas locales de DpsLab")
    commands = parser.add_subparsers(dest="command", required=True)

    snapshot = commands.add_parser("snapshot", help="Genera un snapshot desde un perfil .simc")
    snapshot.add_argument("--input", type=Path, required=True, help="Perfil .simc de entrada")
    snapshot.add_argument("--output", type=Path, required=True, help="Snapshot JSON de salida")

    simulate = commands.add_parser("simulate", help="Ejecuta una simulación base aislada")
    simulate.add_argument(
        "--profile", type=Path, default=root / "profiles" / "flasil.simc", help="Perfil .simc"
    )
    simulate.add_argument("--simc-exe", type=Path, help="Ruta explícita a simc.exe")
    simulate.add_argument("--timeout", type=float, help="Timeout en segundos")
    simulate.add_argument("--threads", type=int, help="Hilos de SimulationCraft (predeterminado: 4)")
    simulate.add_argument("--iterations", type=int, help="Número de iteraciones")
    simulate.add_argument("--max-time", type=int, help="Duración máxima de combate en segundos")
    simulate.add_argument(
        "--vary-combat-length", type=float, help="Variación de duración de combate entre 0 y 1"
    )
    simulate.add_argument("--fight-style", help="Estilo de combate de SimulationCraft")
    simulate.add_argument("--desired-targets", type=int, help="Número de objetivos")
    simulate.add_argument("--target-error", type=float, help="Error objetivo para modo adaptativo")
    simulate.add_argument("--seed", type=int, help="Seed positiva de SimulationCraft")
    simulate.add_argument("--scenario", type=Path, help="Archivo TOML de escenario reproducible")
    simulate.add_argument("--variant", type=Path, help="Archivo TOML de variante de perfil")
    simulate.add_argument("--runs-dir", type=Path, help="Directorio raíz de ejecuciones")
    simulate.add_argument(
        "--html",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Genera también el informe HTML",
    )
    summarize = commands.add_parser("summarize", help="Resume una ejecución existente")
    summarize.add_argument("run_dir", type=Path, help="Carpeta de la ejecución")
    return parser.parse_args(argv)


def _snapshot(args: argparse.Namespace) -> int:
    snapshot = parse_profile(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(snapshot.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Snapshot escrito en {args.output}")
    return 0


def _simulate(args: argparse.Namespace) -> int:
    root = project_root()
    scenario = load_scenario(args.scenario) if args.scenario is not None else None
    variant = load_variant(args.variant) if args.variant is not None else None
    config = resolve_simulation_config(
        explicit_simc_exe=args.simc_exe,
        root=root,
        timeout_seconds=args.timeout,
        generate_html=args.html,
        runs_dir=args.runs_dir,
        threads=args.threads,
        iterations=args.iterations,
        max_time=args.max_time,
        vary_combat_length=args.vary_combat_length,
        fight_style=args.fight_style,
        desired_targets=args.desired_targets,
        target_error=args.target_error,
        scenario=scenario,
        variant=variant,
        seed=args.seed,
    )
    result = run_simulation(args.profile, config, root=root)
    print(f"Simulación {result.run_id} completada en {result.artifacts.run_dir}")
    return 0


def _summarize(args: argparse.Namespace) -> int:
    summary = summarize_run(args.run_dir, root=project_root())
    print(f"Resumen {summary.identification.run_id} escrito en {args.run_dir / 'run_summary.json'}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = _arguments(argv)
    try:
        if args.command == "snapshot":
            return _snapshot(args)
        if args.command == "simulate":
            return _simulate(args)
        return _summarize(args)
    except (
        ConfigurationError,
        ProfileParseError,
        ResultSummaryError,
        ScenarioError,
        VariantError,
        SimulationRunError,
        OSError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        if isinstance(exc, SimulationRunError) and exc.run_dir is not None:
            print(f"diagnóstico: {exc.run_dir}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
