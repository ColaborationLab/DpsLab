"""Command-line entry points for DpsLab."""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from importlib.metadata import PackageNotFoundError
from pathlib import Path
from typing import Sequence

from .addon_observation_import import import_addon_observation
from .comparison_environment import software_record
from .comparison_execution import (
    ComparisonExecutionError,
    execute_frozen_comparison,
)
from .comparison_readiness import (
    ComparisonReadinessError,
    assess_comparison_readiness,
)
from .comparison_spec import ComparisonSpecError, load_comparison_spec
from .config import ConfigurationError, project_root, resolve_simulation_config
from .parser import ProfileParseError, parse_profile
from .result_parser import ResultSummaryError, summarize_run
from .retail_installation import RetailInstallationError, validate_retail_installation_root
from .retail_installation_store import (
    RetailInstallationStoreError,
    store_retail_installation,
)
from .local_character_context_profile import (
    CharacterContextProfileError,
    WindowsProfileProtector,
    inspect_profile,
)
from .local_profile_manual_ui import (
    LocalProfileManualController,
    TkLocalProfileManualWorkspace,
)
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

    comparison_ready = commands.add_parser(
        "comparison-ready",
        help="Verifica la preparación portable de una comparación congelada",
    )
    comparison_ready.add_argument(
        "--comparison",
        type=Path,
        default=root / "comparisons" / "flasil_neck_50228_vs_249368_v1.toml",
        help="Contrato TOML de comparación congelado",
    )
    comparison_ready.add_argument(
        "--simc-exe",
        type=Path,
        help="Ruta explícita a simc.exe",
    )
    comparison_ready.add_argument(
        "--probe-timeout",
        type=float,
        default=30.0,
        help="Timeout de la sonda de identidad en segundos",
    )
    comparison_execute = commands.add_parser(
        "comparison-execute",
        help="Ejecuta el protocolo A/B congelado después de readiness",
    )
    comparison_execute.add_argument(
        "--comparison",
        type=Path,
        default=root / "comparisons" / "flasil_neck_50228_vs_249368_v1.toml",
    )
    comparison_execute.add_argument("--simc-exe", type=Path, required=True)
    comparison_execute.add_argument(
        "--probe-timeout", type=float, default=30.0
    )
    comparison_execute.add_argument(
        "--confirm-comparison-id", required=True
    )

    addon_configure = commands.add_parser(
        "addon-configure",
        help="Guarda una instalación Retail elegida explícitamente",
    )
    addon_configure.add_argument("--config-root", type=Path, required=True)
    addon_configure.add_argument("--retail-root", type=Path, required=True)

    addon_import = commands.add_parser(
        "addon-import",
        help="Importa una observación admitida mediante una acción explícita",
    )
    addon_import.add_argument("--config-root", type=Path, required=True)

    profile_workspace = commands.add_parser(
        "profile-workspace",
        help="Abre un espacio local de perfil sin importación automática",
    )
    profile_workspace.add_argument("--profile-root", type=Path, required=True)
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


def _comparison_ready(args: argparse.Namespace) -> int:
    if (
        not math.isfinite(args.probe_timeout)
        or args.probe_timeout <= 0
        or args.probe_timeout > 60.0
    ):
        raise ComparisonReadinessError("probe_timeout_invalid")
    try:
        root = project_root()
        spec = load_comparison_spec(args.comparison, root=root)
        scenario = load_scenario(spec.scenario)
        values = scenario.scenario
        config = resolve_simulation_config(
            explicit_simc_exe=args.simc_exe,
            root=root,
            timeout_seconds=spec.protocol.timeout_seconds,
            generate_html=False,
            runs_dir=root / "results" / "runs",
            threads=spec.protocol.threads,
            iterations=spec.protocol.iterations_per_run,
            max_time=values.max_time,
            vary_combat_length=values.vary_combat_length,
            fight_style=values.fight_style,
            desired_targets=values.desired_targets,
            target_error=None,
            scenario=scenario,
            variant=None,
            seed=None,
        )
        readiness = assess_comparison_readiness(
            spec,
            config,
            software_record(root),
            root=root,
            probe_timeout_seconds=args.probe_timeout,
        )
    except ComparisonReadinessError:
        raise
    except (
        ComparisonSpecError,
        ConfigurationError,
        PackageNotFoundError,
        ScenarioError,
        OSError,
    ):
        raise ComparisonReadinessError(
            "comparison_readiness_setup_failed"
        ) from None
    report = readiness.preflight
    print(
        json.dumps(
            {
                "base_profile_sha256": report.base_profile_sha256,
                "comparison_id": report.comparison_id,
                "comparison_spec_sha256": report.comparison_spec_sha256,
                "evidence_manifest_sha256": report.evidence_manifest_sha256,
                "executable_source": readiness.executable_source,
                "portable_probe_argv": list(readiness.portable_probe_argv),
                "ready": readiness.ready,
                "runs_dir": report.runs_dir,
                "scenario_sha256": report.scenario_sha256,
                "simulationcraft_branch": readiness.simulationcraft_branch,
            },
            ensure_ascii=True,
            sort_keys=True,
        )
    )
    return 0


def _comparison_execute(args: argparse.Namespace) -> int:
    if (
        not math.isfinite(args.probe_timeout)
        or args.probe_timeout <= 0
        or args.probe_timeout > 60.0
    ):
        raise ComparisonExecutionError("comparison_probe_timeout_invalid")
    try:
        root = project_root()
        spec = load_comparison_spec(args.comparison, root=root)
        scenario = load_scenario(spec.scenario)
        values = scenario.scenario
        config = resolve_simulation_config(
            explicit_simc_exe=args.simc_exe,
            root=root,
            timeout_seconds=spec.protocol.timeout_seconds,
            generate_html=False,
            runs_dir=root / "results" / "runs",
            threads=spec.protocol.threads,
            iterations=spec.protocol.iterations_per_run,
            max_time=values.max_time,
            vary_combat_length=values.vary_combat_length,
            fight_style=values.fight_style,
            desired_targets=values.desired_targets,
            target_error=None,
            scenario=scenario,
            variant=None,
            seed=None,
        )
        readiness = assess_comparison_readiness(
            spec,
            config,
            software_record(root),
            root=root,
            probe_timeout_seconds=args.probe_timeout,
        )
        result = execute_frozen_comparison(
            spec,
            config,
            readiness,
            confirmation=args.confirm_comparison_id,
            root=root,
        )
    except ComparisonExecutionError:
        raise
    except Exception:
        raise ComparisonExecutionError(
            "comparison_execution_setup_failed"
        ) from None
    print(
        json.dumps(
            {
                "comparison_execution_id": result.comparison_execution_id,
                "comparison_id": result.comparison_id,
                "status": result.status,
            },
            sort_keys=True,
        )
    )
    return 0


def _addon_configure(args: argparse.Namespace) -> int:
    selection = validate_retail_installation_root(args.retail_root)
    receipt = store_retail_installation(args.config_root, selection)
    print(
        json.dumps(
            {"byte_count": receipt.byte_count, "state": "configured"},
            ensure_ascii=True,
            sort_keys=True,
        )
    )
    return 0


def _addon_import(args: argparse.Namespace) -> int:
    result = import_addon_observation(args.config_root)
    print(
        json.dumps(
            {
                "byte_count": result.byte_count,
                "observation_available": result.observation is not None,
                "observation_type": result.observation_type,
                "reason": result.reason,
                "source_sha256": result.source_sha256,
                "state": result.state,
            },
            ensure_ascii=True,
            sort_keys=True,
        )
    )
    return 2 if result.state == "rejected" else 0


def _profile_workspace(args: argparse.Namespace) -> int:
    root = args.profile_root
    if not root.is_absolute():
        raise CharacterContextProfileError("profile_workspace_root_invalid")
    try:
        protector = WindowsProfileProtector()
    except Exception:
        raise CharacterContextProfileError("profile_workspace_protection_unavailable") from None
    try:
        inspect_profile(root, protector)
    except Exception:
        raise CharacterContextProfileError("profile_workspace_unavailable") from None
    controller = LocalProfileManualController(
        root,
        protector,
        expected_build=0,
        expected_interface_version=0,
        now_epoch=lambda: int(time.time()),
        snapshot_supplier=None,
    )
    try:
        TkLocalProfileManualWorkspace(controller).run()
    except Exception:
        raise CharacterContextProfileError("profile_workspace_desktop_unavailable") from None
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = _arguments(argv)
    try:
        if args.command == "snapshot":
            return _snapshot(args)
        if args.command == "simulate":
            return _simulate(args)
        if args.command == "comparison-ready":
            return _comparison_ready(args)
        if args.command == "comparison-execute":
            return _comparison_execute(args)
        if args.command == "addon-configure":
            return _addon_configure(args)
        if args.command == "addon-import":
            return _addon_import(args)
        if args.command == "profile-workspace":
            return _profile_workspace(args)
        return _summarize(args)
    except (
        ComparisonReadinessError,
        ComparisonExecutionError,
        CharacterContextProfileError,
        ComparisonSpecError,
        ConfigurationError,
        ProfileParseError,
        RetailInstallationError,
        RetailInstallationStoreError,
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
