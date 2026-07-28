"""Ejecución local, aislada y auditable de SimulationCraft."""

from __future__ import annotations

import json
import re
import struct
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from time import monotonic
from typing import Any
from uuid import uuid4

from .config import SimulationConfig
from .result_parser import ResultSummaryError, summarize_run
from .variant import AppliedOverride, create_effective_profile


class SimulationRunError(RuntimeError):
    """Base error for a SimulationCraft run that did not complete safely."""

    def __init__(self, message: str, *, run_dir: Path | None = None, invocation: InvocationRecord | None = None) -> None:
        super().__init__(message)
        self.run_dir = run_dir
        self.invocation = invocation


class SimulationTimeoutError(SimulationRunError):
    """SimulationCraft exceeded its configured timeout."""


class SimulationProcessError(SimulationRunError):
    """SimulationCraft returned a non-zero exit code."""


class SimulationOutputError(SimulationRunError):
    """SimulationCraft did not create valid requested output."""


class ProfileIntegrityError(SimulationRunError):
    """The source profile changed during execution."""


class SummaryPostprocessingError(SimulationRunError):
    """Simulation completed, but generation of run_summary.json failed."""


class ScenarioIntegrityError(SimulationRunError):
    """The scenario file changed between loading and completing a run."""


class VariantIntegrityError(SimulationRunError):
    """The variant or base profile changed while preparing a run."""


@dataclass(frozen=True, slots=True)
class RunArtifacts:
    run_dir: Path
    json_file: Path
    html_file: Path | None
    metadata_file: Path
    stdout_file: Path
    stderr_file: Path


@dataclass(frozen=True, slots=True)
class RunResult:
    run_id: str
    status: str
    exit_code: int
    duration_seconds: float
    simc_version: str | None
    artifacts: RunArtifacts
    invocation: InvocationRecord | None = None


@dataclass(frozen=True, slots=True)
class InvocationRecord:
    portable_argv: tuple[str, ...]
    portable_argv_sha256: str
    process_argv_sha256: str
    executable_sha256: str
    executable_source: str
    argument_list: bool = True
    shell: bool = False


@dataclass(slots=True)
class RunReservation:
    run_id: str
    run_directory: Path
    reservation_token: str
    created_at: str
    comparison_execution_id: str
    member_id: str
    status: str = "reserved"
    consumed_at: str | None = None
    abandoned_at: str | None = None

    @property
    def consumed(self) -> bool:
        return self.status == "consumed"

    def consume(self, *, comparison_execution_id: str, member_id: str) -> None:
        if self.status != "reserved":
            raise SimulationRunError("La reserva no esta disponible")
        if (comparison_execution_id, member_id) != (self.comparison_execution_id, self.member_id):
            raise SimulationRunError("La reserva no pertenece a este miembro")
        self.status = "consumed"
        self.consumed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def abandon(self, *, comparison_execution_id: str, member_id: str) -> None:
        if self.status != "reserved" or (comparison_execution_id, member_id) != (self.comparison_execution_id, self.member_id):
            raise SimulationRunError("La reserva no puede abandonarse")
        self.status = "abandoned"
        self.abandoned_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def reserve_run(runs_dir: Path, *, comparison_execution_id: str = "standalone", member_id: str = "standalone", run_id: str | None = None) -> RunReservation:
    """Exclusively reserve a run directory without launching a process."""
    runs_dir.mkdir(parents=True, exist_ok=True)
    for _ in range(1 if run_id is not None else 10):
        selected = run_id
        if selected is None:
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
            selected = f"{stamp}-{uuid4().hex[:8]}"
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", selected):
            raise SimulationRunError("run_id reservado no valido")
        directory = runs_dir / selected
        try:
            directory.mkdir(exist_ok=False)
        except FileExistsError:
            if run_id is not None:
                raise SimulationRunError("El run_id ya esta reservado")
            continue
        return RunReservation(selected, directory, uuid4().hex, datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), comparison_execution_id, member_id)
    raise SimulationRunError("No se pudo reservar una carpeta de ejecucion unica")


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _portable_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name


def _argv_sha256(arguments: list[str] | tuple[str, ...]) -> str:
    digest = sha256()
    digest.update(struct.pack(">I", len(arguments)))
    for argument in arguments:
        encoded = argument.encode("utf-8")
        digest.update(struct.pack(">I", len(encoded)))
        digest.update(encoded)
    return digest.hexdigest()


def _portable_argv(command: list[str], *, root: Path) -> tuple[str, ...]:
    portable = ["<SIMC_EXE>"]
    for argument in command[1:]:
        if "=" not in argument:
            portable.append(_portable_path(Path(argument), root))
            continue
        key, value = argument.split("=", 1)
        if key in {"json", "html"}:
            path, *suffix = value.split(",", 1)
            rendered = _portable_path(Path(path), root)
            portable.append(f"{key}={rendered}" + (f",{suffix[0]}" if suffix else ""))
        else:
            portable.append(argument)
    return tuple(portable)


def _new_run_dir(runs_dir: Path) -> tuple[str, Path]:
    reservation = reserve_run(runs_dir)
    reservation.consume(comparison_execution_id="standalone", member_id="standalone")
    return reservation.run_id, reservation.run_directory


def _text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _simc_version(document: Any, stdout: str, stderr: str) -> str | None:
    if isinstance(document, dict):
        candidates = [
            document.get("version"),
            document.get("simc_version"),
        ]
        for section_name in ("sim", "simulationcraft"):
            section = document.get(section_name)
            if isinstance(section, dict):
                candidates.extend((section.get("version"), section.get("simc_version")))
        for candidate in candidates:
            if isinstance(candidate, (str, int, float)) and str(candidate).strip():
                return str(candidate)
    match = re.search(r"\bSimulationCraft\s+([^\s,;]+)", f"{stdout}\n{stderr}", re.IGNORECASE)
    return match.group(1) if match else None


def _simc_revision(document: Any) -> str | None:
    if not isinstance(document, dict):
        return None
    candidate = document.get("git_revision")
    if not isinstance(candidate, str) or not candidate.strip():
        return None
    return candidate.strip()


def _write_metadata(path: Path, metadata: dict[str, Any]) -> None:
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _metadata_parameters(
    profile: Path,
    json_file: Path,
    html_file: Path | None,
    *,
    root: Path,
    threads: int,
    iterations: int | None,
    max_time: int | None,
    vary_combat_length: float | None,
    fight_style: str | None,
    desired_targets: int | None,
    target_error: float | None,
    seed: int | None,
) -> list[str]:
    parameters = [
        _portable_path(profile, root),
        f"threads={threads}",
        f"json={_portable_path(json_file, root)},version=2,pretty_print=1",
    ]
    if iterations is not None:
        parameters.append(f"iterations={iterations}")
    if max_time is not None:
        parameters.append(f"max_time={max_time}")
    if vary_combat_length is not None:
        parameters.append(f"vary_combat_length={vary_combat_length:g}")
    if fight_style is not None:
        parameters.append(f"fight_style={fight_style}")
    if desired_targets is not None:
        parameters.append(f"desired_targets={desired_targets}")
    if target_error is not None:
        parameters.append(f"target_error={target_error:g}")
    if seed is not None:
        parameters.append(f"seed={seed}")
    if html_file is not None:
        parameters.append(f"html={_portable_path(html_file, root)}")
    return parameters


def run_simulation(
    profile: Path,
    config: SimulationConfig,
    *,
    root: Path,
    reservation: RunReservation | None = None,
) -> RunResult:
    """Run one baseline simulation and persist complete diagnostic artifacts."""
    root = root.resolve()
    profile = profile.resolve()
    if profile.suffix.lower() != ".simc":
        raise SimulationRunError(f"Se esperaba un perfil .simc: {profile}")
    if not profile.is_file():
        raise SimulationRunError(f"No existe el perfil: {profile}")

    profile_hash_before = _file_sha256(profile)
    base_bytes = profile.read_bytes()
    checksum_match = re.search(rb"(?m)^# Checksum:\s*(\S+)\s*$", base_bytes)
    base_simc_checksum = checksum_match.group(1).decode("ascii") if checksum_match else None
    variant_hash_before: str | None = None
    if config.variant is not None:
        variant_hash_before = _file_sha256(config.variant.source_file)
        if variant_hash_before != config.variant.source_sha256:
            raise VariantIntegrityError("La variante cambió después de ser cargada")
    scenario_hash_before: str | None = None
    scenario_hash_after: str | None = None
    scenario_hash_verified: bool | None = None
    if config.scenario is not None:
        try:
            scenario_hash_before = _file_sha256(config.scenario.source_file)
        except OSError as exc:
            raise SimulationRunError(f"No se pudo verificar el escenario: {exc}") from exc
        if scenario_hash_before != config.scenario.source_sha256:
            raise ScenarioIntegrityError("El escenario cambió después de ser cargado")
    if reservation is None:
        run_id, run_dir = _new_run_dir(config.runs_dir)
    else:
        if reservation.status != "reserved":
            raise SimulationRunError("La reserva ya fue consumida", run_dir=reservation.run_directory)
        if reservation.run_directory.resolve().parent != config.runs_dir.resolve() or reservation.run_directory.name != reservation.run_id or not reservation.run_directory.is_dir():
            raise SimulationRunError("La reserva no pertenece al directorio configurado")
        reservation.consume(comparison_execution_id=reservation.comparison_execution_id, member_id=reservation.member_id)
        run_id, run_dir = reservation.run_id, reservation.run_directory
    json_file = run_dir / "simc.json"
    html_file = run_dir / "simc.html" if config.generate_html else None
    metadata_file = run_dir / "metadata.json"
    stdout_file = run_dir / "stdout.txt"
    stderr_file = run_dir / "stderr.txt"
    artifacts = RunArtifacts(run_dir, json_file, html_file, metadata_file, stdout_file, stderr_file)

    effective_profile: Path | None = None
    effective_profile_sha256: str | None = None
    applied_overrides: tuple[AppliedOverride, ...] = ()
    variant_hash_after: str | None = None
    variant_hash_verified: bool | None = None
    profile_for_simc = profile
    if config.variant is not None:
        effective_profile = run_dir / "effective_profile.simc"
        effective_profile_sha256, applied_overrides = create_effective_profile(
            base_bytes, config.variant, effective_profile
        )
        profile_hash_prepared = _file_sha256(profile)
        variant_hash_after = _file_sha256(config.variant.source_file)
        variant_hash_verified = variant_hash_before == variant_hash_after == config.variant.source_sha256
        if profile_hash_prepared != profile_hash_before or not variant_hash_verified:
            error = "El perfil base o la variante cambió durante la preparación; subprocess no fue ejecutado"
            _write_metadata(metadata_file, {
                "schema_version": "0.3", "run_id": run_id, "status": "integrity_error",
                "error": error, "base_profile": _portable_path(profile, root),
                "base_profile_sha256_before": profile_hash_before,
                "base_profile_sha256_after": profile_hash_prepared,
                "variant_file": _portable_path(config.variant.source_file, root),
                "variant_sha256_before": variant_hash_before,
                "variant_sha256_after": variant_hash_after,
                "variant_hash_verified": variant_hash_verified,
                "effective_profile": _portable_path(effective_profile, root),
                "effective_profile_sha256": effective_profile_sha256,
            })
            raise VariantIntegrityError(error, run_dir=run_dir)
        profile_for_simc = effective_profile

    command: list[str] = [
        str(config.simc_exe.resolve()),
        str(profile_for_simc),
        f"threads={config.threads}",
        f"json={json_file.resolve()},version=2,pretty_print=1",
    ]
    if config.iterations is not None:
        command.append(f"iterations={config.iterations}")
    if config.max_time is not None:
        command.append(f"max_time={config.max_time}")
    if config.vary_combat_length is not None:
        command.append(f"vary_combat_length={config.vary_combat_length:g}")
    if config.fight_style is not None:
        command.append(f"fight_style={config.fight_style}")
    if config.desired_targets is not None:
        command.append(f"desired_targets={config.desired_targets}")
    if config.target_error is not None:
        command.append(f"target_error={config.target_error:g}")
    if config.seed is not None:
        command.append(f"seed={config.seed}")
    if html_file is not None:
        command.append(f"html={html_file.resolve()}")
    portable_argv = _portable_argv(command, root=root)
    invocation = InvocationRecord(
        portable_argv,
        _argv_sha256(portable_argv),
        _argv_sha256(command),
        _file_sha256(config.simc_exe),
        config.executable_source,
    )
    invocation_document = {
        "portable_argv": list(invocation.portable_argv),
        "portable_argv_sha256": invocation.portable_argv_sha256,
        "process_argv_sha256": invocation.process_argv_sha256,
        "executable_sha256": invocation.executable_sha256,
        "executable_source": invocation.executable_source,
        "argument_list": invocation.argument_list,
        "shell": invocation.shell,
        "timeout_seconds": config.timeout_seconds,
    }

    started_at = datetime.now(timezone.utc)
    started_clock = monotonic()
    stdout = ""
    stderr = ""
    exit_code: int | None = None
    status = "failed"
    error_message: str | None = None
    simc_version: str | None = None
    simc_revision: str | None = None
    output_document: Any = None
    raised_error: SimulationRunError | None = None

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=config.timeout_seconds,
            shell=False,
            check=False,
        )
        stdout = completed.stdout
        stderr = completed.stderr
        exit_code = completed.returncode
        if exit_code != 0:
            error_message = f"SimulationCraft terminó con código de salida {exit_code}"
            raised_error = SimulationProcessError(error_message, run_dir=run_dir)
        elif not json_file.is_file() or json_file.stat().st_size == 0:
            error_message = "SimulationCraft no generó un JSON principal válido"
            raised_error = SimulationOutputError(error_message, run_dir=run_dir)
        else:
            try:
                output_document = json.loads(json_file.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                error_message = f"El JSON generado por SimulationCraft no es válido: {exc}"
                raised_error = SimulationOutputError(error_message, run_dir=run_dir)
            if raised_error is None and html_file is not None and not html_file.is_file():
                error_message = "SimulationCraft no generó el HTML solicitado"
                raised_error = SimulationOutputError(error_message, run_dir=run_dir)
            if raised_error is None:
                status = "completed"
                simc_version = _simc_version(output_document, stdout, stderr)
                simc_revision = _simc_revision(output_document)
    except subprocess.TimeoutExpired as exc:
        stdout = _text(exc.stdout)
        stderr = _text(exc.stderr)
        status = "timeout"
        error_message = f"SimulationCraft excedió el timeout de {config.timeout_seconds:g} segundos"
        raised_error = SimulationTimeoutError(error_message, run_dir=run_dir)
    except OSError as exc:
        error_message = f"No se pudo ejecutar SimulationCraft: {exc}"
        raised_error = SimulationRunError(error_message, run_dir=run_dir)

    duration = monotonic() - started_clock
    finished_at = datetime.now(timezone.utc)
    stdout_file.write_text(stdout, encoding="utf-8")
    stderr_file.write_text(stderr, encoding="utf-8")
    profile_hash_after = _file_sha256(profile)
    if profile_hash_after != profile_hash_before:
        status = "profile_modified"
        error_message = "El perfil cambió durante la ejecución de SimulationCraft"
        raised_error = ProfileIntegrityError(error_message, run_dir=run_dir)

    if config.scenario is not None:
        try:
            scenario_hash_after = _file_sha256(config.scenario.source_file)
        except OSError:
            scenario_hash_after = None
        scenario_hash_verified = (
            scenario_hash_after is not None
            and scenario_hash_before == scenario_hash_after == config.scenario.source_sha256
        )
        if not scenario_hash_verified:
            status = "scenario_modified"
            error_message = "El escenario cambió durante la preparación o ejecución"
            raised_error = ScenarioIntegrityError(error_message, run_dir=run_dir)

    if config.variant is not None:
        try:
            variant_hash_after = _file_sha256(config.variant.source_file)
        except OSError:
            variant_hash_after = None
        variant_hash_verified = (
            variant_hash_after is not None
            and variant_hash_before == variant_hash_after == config.variant.source_sha256
        )
        if not variant_hash_verified:
            status = "variant_modified"
            error_message = "La variante cambió durante la preparación o ejecución"
            raised_error = VariantIntegrityError(error_message, run_dir=run_dir)

    metadata = {
        "schema_version": "0.3",
        "run_id": run_id,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "duration_seconds": duration,
        "status": status,
        "error": error_message,
        "profile": _portable_path(profile, root),
        "profile_sha256_before": profile_hash_before,
        "profile_sha256_after": profile_hash_after,
        "base_profile": _portable_path(profile, root),
        "base_simc_checksum": base_simc_checksum,
        "base_profile_sha256": profile_hash_before,
        "base_profile_sha256_before": profile_hash_before,
        "base_profile_sha256_after": profile_hash_after,
        "base_profile_hash_verified": profile_hash_before == profile_hash_after,
        "effective_profile": _portable_path(effective_profile, root) if effective_profile else None,
        "effective_profile_sha256": effective_profile_sha256,
        "variant_id": config.variant.variant.id if config.variant else None,
        "variant_name": config.variant.variant.name if config.variant else None,
        "variant_file": _portable_path(config.variant.source_file, root) if config.variant else None,
        "variant_sha256_before": variant_hash_before,
        "variant_sha256_after": variant_hash_after,
        "variant_hash_verified": variant_hash_verified,
        "overrides": [item.to_dict() for item in applied_overrides] if config.variant else None,
        "simc_version": simc_version,
        "simc_revision": simc_revision,
        "parameters": _metadata_parameters(
            profile_for_simc,
            json_file,
            html_file,
            root=root,
            threads=config.threads,
            iterations=config.iterations,
            max_time=config.max_time,
            vary_combat_length=config.vary_combat_length,
            fight_style=config.fight_style,
            desired_targets=config.desired_targets,
            target_error=config.target_error,
            seed=config.seed,
        ),
        "threads": config.threads,
        "iterations": config.iterations,
        "max_time": config.max_time,
        "vary_combat_length": config.vary_combat_length,
        "fight_style": config.fight_style,
        "desired_targets": config.desired_targets,
        "target_error": config.target_error,
        "seed": config.seed,
        "effective_parameters": {
            "threads": config.threads,
            "iterations": config.iterations,
            "max_time": config.max_time,
            "vary_combat_length": config.vary_combat_length,
            "fight_style": config.fight_style,
            "desired_targets": config.desired_targets,
            "target_error": config.target_error,
            "seed": config.seed,
            "generate_html": config.generate_html,
            "timeout_seconds": config.timeout_seconds,
        },
        "scenario_id": config.scenario.scenario.id if config.scenario else None,
        "scenario_name": config.scenario.scenario.name if config.scenario else None,
        "scenario_file": (
            _portable_path(config.scenario.source_file, root) if config.scenario else None
        ),
        "scenario_sha256_before": scenario_hash_before,
        "scenario_sha256_after": scenario_hash_after,
        "scenario_hash_verified": scenario_hash_verified,
        "scenario_effective_parameters": (
            {
                "fight_style": config.fight_style,
                "desired_targets": config.desired_targets,
                "max_time": config.max_time,
                "vary_combat_length": config.vary_combat_length,
                "target_error": config.target_error,
                "iterations": config.iterations,
            }
            if config.scenario
            else None
        ),
        "timeout_seconds": config.timeout_seconds,
        "exit_code": exit_code,
        "artifacts": {
            "json": _portable_path(json_file, root),
            "html": _portable_path(html_file, root) if html_file is not None else None,
            "stdout": _portable_path(stdout_file, root),
            "stderr": _portable_path(stderr_file, root),
        },
        "html_requested": config.generate_html,
        "html_generated": html_file is not None and html_file.is_file(),
        "invocation": invocation_document,
    }
    _write_metadata(metadata_file, metadata)

    if raised_error is not None:
        raised_error.invocation = invocation
        raise raised_error
    try:
        summarize_run(run_dir, root=root)
    except ResultSummaryError as exc:
        raise SummaryPostprocessingError(
            f"La simulación terminó correctamente, pero falló el postprocesamiento: {exc}",
            run_dir=run_dir,
        ) from exc
    return RunResult(run_id, status, exit_code or 0, duration, simc_version, artifacts, invocation)
