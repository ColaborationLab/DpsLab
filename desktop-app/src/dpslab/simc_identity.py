"""Isolated, fail-closed identity probe for a configured SimulationCraft binary."""

from __future__ import annotations

import math
import os
import re
import subprocess
import tempfile
import threading
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from time import monotonic
from typing import BinaryIO

from .comparison_models import SimulationCraftIdentity
from .config import SimulationConfig


class SimulationCraftIdentityProbeError(RuntimeError):
    """SimulationCraft identity could not be captured safely and completely."""


@dataclass(frozen=True, slots=True)
class SimulationCraftIdentityProbe:
    identity: SimulationCraftIdentity
    branch: str
    executable_source: str
    portable_argv: tuple[str, ...] = ("<SIMC_EXE>", "display_build=2")
    isolated: bool = True


_ALLOWED_EXECUTABLE_SOURCES = frozenset(
    {"explicit_cli", "environment", "local_config"}
)
_VERSION_LINE_PATTERN = re.compile(
    r"^SimulationCraft\s+([0-9]{4}-[0-9]{2})\b"
)
_BUILD_CLAUSE_MARKER_PATTERN = re.compile(r"\bgit build\b")
_BUILD_CLAUSE_PATTERN = re.compile(
    r"\bgit build\s+([A-Za-z0-9._/-]{1,64})\s+"
    r"([0-9a-f]{7,40})\b"
)
_MAX_CAPTURED_OUTPUT_BYTES = 64 * 1024
_MAX_PROBE_TIMEOUT_SECONDS = 60.0
_READ_CHUNK_BYTES = 4096
_PROCESS_STOP_TIMEOUT_SECONDS = 5.0


@dataclass(frozen=True, slots=True)
class _ProcessCapture:
    returncode: int
    stdout: bytes
    stderr: bytes
    failure: str | None = None


def _file_sha256(path: Path) -> str | None:
    digest = sha256()
    try:
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    except OSError:
        return None
    return digest.hexdigest()


def _isolated_environment(directory: Path) -> dict[str, str]:
    environment = {
        key: value
        for key in (
            "SystemRoot",
            "WINDIR",
            "ComSpec",
            "PROCESSOR_ARCHITECTURE",
            "NUMBER_OF_PROCESSORS",
        )
        if (value := os.environ.get(key))
    }
    isolated = str(directory)
    environment.update(
        {
            "TEMP": isolated,
            "TMP": isolated,
            "HOME": isolated,
            "USERPROFILE": isolated,
            "HTTP_PROXY": "http://127.0.0.1:9",
            "HTTPS_PROXY": "http://127.0.0.1:9",
            "ALL_PROXY": "http://127.0.0.1:9",
            "NO_PROXY": "*",
        }
    )
    return environment


def _single_identity(stdout: str, stderr: str) -> tuple[str, str, str]:
    identities: list[tuple[str, str, str]] = []
    malformed_candidate = False
    for stream in (stdout, stderr):
        for line in stream.splitlines():
            version_match = _VERSION_LINE_PATTERN.match(line)
            if version_match is None:
                continue
            build_markers = list(
                _BUILD_CLAUSE_MARKER_PATTERN.finditer(line)
            )
            build_matches = list(_BUILD_CLAUSE_PATTERN.finditer(line))
            if len(build_markers) != 1 or len(build_matches) != 1:
                malformed_candidate = True
                continue
            branch, revision = build_matches[0].groups()
            identities.append(
                (version_match.group(1), branch, revision)
            )
    if malformed_candidate or len(identities) != 1:
        raise SimulationCraftIdentityProbeError(
            "simc_identity_missing_or_ambiguous"
        )
    version, branch, revision = identities[0]
    return version, branch, revision


def _stop_process(process: subprocess.Popen[bytes]) -> bool:
    try:
        process.terminate()
    except OSError:
        pass
    try:
        process.wait(timeout=_PROCESS_STOP_TIMEOUT_SECONDS)
        return True
    except (OSError, subprocess.TimeoutExpired):
        pass
    try:
        process.kill()
    except OSError:
        pass
    try:
        process.wait(timeout=_PROCESS_STOP_TIMEOUT_SECONDS)
        return True
    except (OSError, subprocess.TimeoutExpired):
        return False


def _capture_process(
    process: subprocess.Popen[bytes],
    *,
    timeout_seconds: float,
) -> _ProcessCapture:
    if process.stdout is None or process.stderr is None:
        stopped = _stop_process(process)
        failure = (
            "capture_unavailable" if stopped else "process_stop_failed"
        )
        return _ProcessCapture(-1, b"", b"", failure)

    buffers = {"stdout": bytearray(), "stderr": bytearray()}
    lock = threading.Lock()
    exceeded = threading.Event()
    read_failed = threading.Event()
    captured_bytes = 0

    def drain(stream: BinaryIO, label: str) -> None:
        nonlocal captured_bytes
        try:
            while chunk := stream.read(_READ_CHUNK_BYTES):
                with lock:
                    remaining = (
                        _MAX_CAPTURED_OUTPUT_BYTES - captured_bytes
                    )
                    if len(chunk) > remaining:
                        buffers[label].extend(chunk[: max(remaining, 0)])
                        captured_bytes += len(chunk)
                        exceeded.set()
                        return
                    buffers[label].extend(chunk)
                    captured_bytes += len(chunk)
        except (OSError, ValueError):
            read_failed.set()

    readers = [
        threading.Thread(
            target=drain,
            args=(process.stdout, "stdout"),
            daemon=True,
        ),
        threading.Thread(
            target=drain,
            args=(process.stderr, "stderr"),
            daemon=True,
        ),
    ]
    for reader in readers:
        reader.start()

    deadline = monotonic() + timeout_seconds
    failure: str | None = None
    returncode = -1
    while True:
        if exceeded.is_set():
            failure = "output_too_large"
            if not _stop_process(process):
                failure = "process_stop_failed"
            returncode = process.returncode if process.returncode is not None else -1
            break
        if read_failed.is_set():
            failure = "capture_failed"
            if not _stop_process(process):
                failure = "process_stop_failed"
            returncode = process.returncode if process.returncode is not None else -1
            break
        remaining = deadline - monotonic()
        if remaining <= 0:
            failure = "timeout"
            if not _stop_process(process):
                failure = "process_stop_failed"
            returncode = process.returncode if process.returncode is not None else -1
            break
        try:
            returncode = process.wait(timeout=min(0.05, remaining))
            break
        except subprocess.TimeoutExpired:
            continue
        except OSError:
            failure = "wait_failed"
            if not _stop_process(process):
                failure = "process_stop_failed"
            returncode = process.returncode if process.returncode is not None else -1
            break

    for reader in readers:
        reader.join(timeout=_PROCESS_STOP_TIMEOUT_SECONDS)
    if any(reader.is_alive() for reader in readers) or read_failed.is_set():
        if not _stop_process(process):
            failure = "process_stop_failed"
        else:
            failure = failure or "capture_failed"
    if exceeded.is_set() and failure != "process_stop_failed":
        failure = "output_too_large"
    try:
        process.stdout.close()
        process.stderr.close()
    except OSError:
        failure = failure or "capture_failed"
    return _ProcessCapture(
        returncode,
        bytes(buffers["stdout"]),
        bytes(buffers["stderr"]),
        failure,
    )


def capture_simulationcraft_identity(
    config: SimulationConfig,
    *,
    timeout_seconds: float = 30.0,
) -> SimulationCraftIdentityProbe:
    """Capture build identity without creating a run or comparison artifact."""
    if (
        isinstance(timeout_seconds, bool)
        or not isinstance(timeout_seconds, (int, float))
        or not math.isfinite(timeout_seconds)
        or timeout_seconds <= 0
        or timeout_seconds > _MAX_PROBE_TIMEOUT_SECONDS
    ):
        raise SimulationCraftIdentityProbeError("probe_timeout_invalid")
    if config.executable_source not in _ALLOWED_EXECUTABLE_SOURCES:
        raise SimulationCraftIdentityProbeError("executable_source_invalid")
    if not config.simc_exe.is_absolute():
        raise SimulationCraftIdentityProbeError(
            "simulationcraft_executable_path_not_absolute"
        )
    executable: Path | None
    try:
        executable = config.simc_exe.resolve(strict=True)
    except OSError:
        executable = None
    if executable is None:
        raise SimulationCraftIdentityProbeError(
            "simulationcraft_executable_missing"
        )
    if not executable.is_file():
        raise SimulationCraftIdentityProbeError(
            "simulationcraft_executable_missing"
        )

    digest_before = _file_sha256(executable)
    if digest_before is None:
        raise SimulationCraftIdentityProbeError(
            "simulationcraft_executable_unreadable"
        )
    command = [str(executable), "display_build=2"]
    creationflags = (
        subprocess.CREATE_NO_WINDOW
        if os.name == "nt" and hasattr(subprocess, "CREATE_NO_WINDOW")
        else 0
    )
    with tempfile.TemporaryDirectory(
        prefix="dpslab-simc-identity-"
    ) as raw:
        isolated = Path(raw).resolve()
        process: subprocess.Popen[bytes] | None
        try:
            process = subprocess.Popen(
                command,
                cwd=isolated,
                env=_isolated_environment(isolated),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                creationflags=creationflags,
            )
        except OSError:
            process = None
        if process is None:
            raise SimulationCraftIdentityProbeError(
                "simulationcraft_identity_probe_start_failed"
            )
        captured = _capture_process(
            process, timeout_seconds=float(timeout_seconds)
        )

    digest_after = _file_sha256(executable)
    if digest_after is None:
        raise SimulationCraftIdentityProbeError(
            "simulationcraft_executable_unreadable_after_probe"
        )
    if digest_after != digest_before:
        raise SimulationCraftIdentityProbeError(
            "simulationcraft_executable_changed_during_probe"
        )
    if captured.failure == "output_too_large":
        raise SimulationCraftIdentityProbeError(
            "simulationcraft_identity_probe_output_too_large"
        )
    if captured.failure == "timeout":
        raise SimulationCraftIdentityProbeError(
            "simulationcraft_identity_probe_timeout"
        )
    if captured.failure is not None:
        raise SimulationCraftIdentityProbeError(
            "simulationcraft_identity_probe_capture_failed"
        )
    if captured.returncode != 0:
        raise SimulationCraftIdentityProbeError(
            "simulationcraft_identity_probe_nonzero_exit"
        )

    stdout = captured.stdout.decode("utf-8", errors="replace")
    stderr = captured.stderr.decode("utf-8", errors="replace")
    version, branch, revision = _single_identity(stdout, stderr)
    return SimulationCraftIdentityProbe(
        identity=SimulationCraftIdentity(
            version=version,
            revision=revision,
            executable_sha256=digest_before,
        ),
        branch=branch,
        executable_source=config.executable_source,
    )
