"""Isolated, fail-closed identity probe for a configured SimulationCraft binary."""

from __future__ import annotations

import json
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
_VERSION_PATTERN = re.compile(r"[0-9]{4}-[0-9]{2}")
_VERSION_IDENTITY_PATTERN = re.compile(
    r"\bSimulationCraft\s+([0-9]{4}-[0-9]{2})\b"
)
_BRANCH_PATTERN = re.compile(r"[A-Za-z0-9._/-]{1,64}")
_REVISION_PATTERN = re.compile(r"[0-9a-f]{7,40}")
_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
_MAX_CAPTURED_OUTPUT_BYTES = 64 * 1024
_MAX_PROBE_TIMEOUT_SECONDS = 60.0
_READ_CHUNK_BYTES = 4096
_PROCESS_STOP_TIMEOUT_SECONDS = 5.0
_MANIFEST_RELATIVE_PATH = Path(
    "comparisons/simulationcraft_identity_manifest_0_1.json"
)
_MANIFEST_ROOT_KEYS = {
    "schema_version",
    "manifest_id",
    "authority",
    "entries",
}
_MANIFEST_AUTHORITY_KEYS = {
    "kind",
    "attested_by",
    "attested_at",
    "trust_model",
}
_MANIFEST_ENTRY_KEYS = {
    "executable_sha256",
    "version",
    "branch",
    "revision",
}
_ATTESTED_EXECUTABLE_SHA256 = (
    "710c71129f779376ed17dbcd92f67aa325056e19e27fa8b2b0182fb05db8c7ee"
)
_ATTESTED_VERSION = "1205-01"
_ATTESTED_BRANCH = "midnight"
_ATTESTED_REVISION = "a81c39d"


@dataclass(frozen=True, slots=True)
class _ProcessCapture:
    returncode: int
    stdout: bytes
    stderr: bytes
    failure: str | None = None


@dataclass(frozen=True, slots=True)
class _AttestedIdentity:
    executable_sha256: str
    version: str
    branch: str
    revision: str


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


def _single_version_without_build(
    stdout: str,
    stderr: str,
) -> str:
    versions = [
        match.group(1)
        for stream in (stdout, stderr)
        for match in _VERSION_IDENTITY_PATTERN.finditer(stream)
    ]
    if (
        len(versions) != 1
        or _BUILD_CLAUSE_MARKER_PATTERN.search(stdout) is not None
        or _BUILD_CLAUSE_MARKER_PATTERN.search(stderr) is not None
    ):
        raise SimulationCraftIdentityProbeError(
            "simc_identity_missing_or_ambiguous"
        )
    return versions[0]


def _manifest_path() -> Path:
    return Path(__file__).resolve().parents[3] / _MANIFEST_RELATIVE_PATH


def _manifest_identity(
    path: Path,
    *,
    executable_sha256: str,
    observed_version: str,
) -> _AttestedIdentity:
    try:
        document = json.loads(path.read_bytes())
    except (OSError, json.JSONDecodeError):
        raise SimulationCraftIdentityProbeError(
            "simc_identity_manifest_unavailable"
        ) from None
    if (
        not isinstance(document, dict)
        or set(document) != _MANIFEST_ROOT_KEYS
        or document.get("schema_version") != "0.1"
        or document.get("manifest_id")
        != "simulationcraft_identity_manifest_0_1"
    ):
        raise SimulationCraftIdentityProbeError(
            "simc_identity_manifest_invalid"
        )
    authority = document.get("authority")
    if (
        not isinstance(authority, dict)
        or set(authority) != _MANIFEST_AUTHORITY_KEYS
        or authority.get("kind") != "explicit_human_attestation"
        or authority.get("attested_by") != "Daniel"
        or authority.get("trust_model") != "trust_on_first_use"
        or not isinstance(authority.get("attested_at"), str)
        or re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}-\d{2}:\d{2}",
            authority["attested_at"],
        )
        is None
    ):
        raise SimulationCraftIdentityProbeError(
            "simc_identity_manifest_invalid"
        )
    raw_entries = document.get("entries")
    if not isinstance(raw_entries, list) or len(raw_entries) != 1:
        raise SimulationCraftIdentityProbeError(
            "simc_identity_manifest_invalid"
        )
    entries: list[_AttestedIdentity] = []
    hashes: set[str] = set()
    for raw in raw_entries:
        if not isinstance(raw, dict) or set(raw) != _MANIFEST_ENTRY_KEYS:
            raise SimulationCraftIdentityProbeError(
                "simc_identity_manifest_invalid"
            )
        values = tuple(raw[key] for key in _MANIFEST_ENTRY_KEYS)
        if not all(isinstance(value, str) for value in values):
            raise SimulationCraftIdentityProbeError(
                "simc_identity_manifest_invalid"
            )
        entry = _AttestedIdentity(
            executable_sha256=raw["executable_sha256"],
            version=raw["version"],
            branch=raw["branch"],
            revision=raw["revision"],
        )
        if (
            _SHA256_PATTERN.fullmatch(entry.executable_sha256) is None
            or _VERSION_PATTERN.fullmatch(entry.version) is None
            or _BRANCH_PATTERN.fullmatch(entry.branch) is None
            or _REVISION_PATTERN.fullmatch(entry.revision) is None
            or entry.executable_sha256 in hashes
        ):
            raise SimulationCraftIdentityProbeError(
                "simc_identity_manifest_invalid"
            )
        hashes.add(entry.executable_sha256)
        entries.append(entry)
    matches = [
        entry
        for entry in entries
        if entry.executable_sha256 == executable_sha256
    ]
    if len(matches) != 1:
        raise SimulationCraftIdentityProbeError(
            "simc_identity_executable_unattested"
        )
    match = matches[0]
    if match != _AttestedIdentity(
        executable_sha256=_ATTESTED_EXECUTABLE_SHA256,
        version=_ATTESTED_VERSION,
        branch=_ATTESTED_BRANCH,
        revision=_ATTESTED_REVISION,
    ):
        raise SimulationCraftIdentityProbeError(
            "simc_identity_manifest_invalid"
        )
    if match.version != observed_version:
        raise SimulationCraftIdentityProbeError(
            "simc_identity_attested_version_mismatch"
        )
    return match


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
    try:
        version, branch, revision = _single_identity(stdout, stderr)
    except SimulationCraftIdentityProbeError:
        version = _single_version_without_build(stdout, stderr)
        attested = _manifest_identity(
            _manifest_path(),
            executable_sha256=digest_before,
            observed_version=version,
        )
        branch = attested.branch
        revision = attested.revision
    return SimulationCraftIdentityProbe(
        identity=SimulationCraftIdentity(
            version=version,
            revision=revision,
            executable_sha256=digest_before,
        ),
        branch=branch,
        executable_source=config.executable_source,
    )
