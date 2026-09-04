"""Quality gate contractual y no funcional para DpsLab."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable


BEGIN = "<!-- DPSLAB_TASK_CONTRACT_BEGIN -->"
END = "<!-- DPSLAB_TASK_CONTRACT_END -->"
CONTRACT_KEYS = {
    "contract_version", "task_id", "title", "baseline_commit",
    "authorization", "scope", "tests", "protected_files", "audit",
    "acceptance_criteria", "express_exclusions",
}
AUTH_KEYS = {"status", "authorization_id", "authorized_by", "authorized_at"}
SCOPE_KEYS = {
    "allowed_paths", "generated_paths", "forbidden_paths",
    "allow_deletions", "allow_renames",
}
TEST_KEYS = {"focused", "full", "baseline_test_count", "minimum_test_count"}
COMMAND_KEYS = {"working_directory", "argv", "environment"}
AUDIT_KEYS = {"required", "independence"}
RUN_LINE = re.compile(r"Ran\s+(\d+)\s+tests?\s+in\s+")
AUDIT_DECISIONS = {"approved", "changes_required", "blocked"}


class GateError(RuntimeError):
    pass


@dataclass(frozen=True)
class Change:
    status: str
    path: str
    old_path: str | None = None


@dataclass(frozen=True)
class CommandResult:
    argv: tuple[str, ...]
    cwd: str
    returncode: int
    stdout: str
    stderr: str
    test_count: int | None = None


Runner = Callable[[list[str], Path, dict[str, str] | None], subprocess.CompletedProcess[str]]


def _closed(document: dict[str, Any], keys: set[str], label: str) -> None:
    unknown = set(document) - keys
    missing = keys - set(document)
    if unknown or missing:
        raise GateError(f"{label}: unknown={sorted(unknown)} missing={sorted(missing)}")


def normalize_path(value: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise GateError("path must be a non-empty POSIX relative path")
    if re.match(r"^[A-Za-z]:/", value):
        raise GateError(f"unsafe path: {value}")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise GateError(f"unsafe path: {value}")
    return path.as_posix()


def extract_contract(text: str) -> dict[str, Any]:
    if text.count(BEGIN) != 1 or text.count(END) != 1:
        raise GateError("contract delimiters missing or duplicated")
    body = text.split(BEGIN, 1)[1].split(END, 1)[0].strip()
    match = re.fullmatch(r"```json\s*(\{.*\})\s*```", body, re.DOTALL)
    if not match:
        raise GateError("contract must be one JSON code block")
    try:
        raw = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise GateError(f"invalid contract JSON: {exc}") from exc
    if not isinstance(raw, dict):
        raise GateError("contract must be an object")
    validate_contract(raw)
    return raw


def validate_contract(contract: dict[str, Any]) -> None:
    _closed(contract, CONTRACT_KEYS, "contract")
    if contract["contract_version"] != "0.1":
        raise GateError("unsupported contract_version")
    if not re.fullmatch(r"[a-z0-9][a-z0-9_]*", contract["task_id"]):
        raise GateError("invalid task_id")
    if not re.fullmatch(r"[0-9a-f]{40}", contract["baseline_commit"]):
        raise GateError("invalid baseline_commit")
    authorization = contract["authorization"]
    scope = contract["scope"]
    tests = contract["tests"]
    audit = contract["audit"]
    if not all(isinstance(item, dict) for item in (authorization, scope, tests, audit)):
        raise GateError("contract sections must be objects")
    _closed(authorization, AUTH_KEYS, "authorization")
    _closed(scope, SCOPE_KEYS, "scope")
    _closed(tests, TEST_KEYS, "tests")
    _closed(audit, AUDIT_KEYS, "audit")
    if authorization["status"] not in {"design_only", "authorized_for_implementation"}:
        raise GateError("invalid authorization status")
    for key in ("authorization_id", "authorized_by", "authorized_at"):
        if not isinstance(authorization[key], str) or not authorization[key].strip():
            raise GateError(f"invalid authorization.{key}")
    try:
        parsed = datetime.fromisoformat(authorization["authorized_at"])
    except ValueError as exc:
        raise GateError("invalid authorization timestamp") from exc
    if parsed.tzinfo is None:
        raise GateError("authorization timestamp requires timezone")
    for key in ("allowed_paths", "generated_paths", "forbidden_paths"):
        if not isinstance(scope[key], list) or not scope[key]:
            raise GateError(f"scope.{key} must be a non-empty list")
        scope[key] = [normalize_path(item) for item in scope[key]]
        if len(scope[key]) != len(set(scope[key])):
            raise GateError(f"duplicate scope.{key}")
    if not isinstance(scope["allow_deletions"], bool) or not isinstance(scope["allow_renames"], bool):
        raise GateError("scope flags must be booleans")
    for key in ("focused", "full"):
        command = tests[key]
        if not isinstance(command, dict):
            raise GateError(f"tests.{key} must be an object")
        _closed(command, COMMAND_KEYS, f"tests.{key}")
        normalize_path(command["working_directory"])
        if not isinstance(command["argv"], list) or not command["argv"] or not all(
            isinstance(item, str) and item for item in command["argv"]
        ):
            raise GateError(f"tests.{key}.argv invalid")
        joined = " ".join(command["argv"]).lower()
        if "simc" in joined or "simulationcraft" in joined:
            raise GateError("SimulationCraft invocation is forbidden")
        if not isinstance(command["environment"], dict) or not all(
            isinstance(k, str) and isinstance(v, str) for k, v in command["environment"].items()
        ):
            raise GateError(f"tests.{key}.environment invalid")
    baseline_count = tests["baseline_test_count"]
    minimum_count = tests["minimum_test_count"]
    if (
        isinstance(baseline_count, bool) or not isinstance(baseline_count, int)
        or isinstance(minimum_count, bool) or not isinstance(minimum_count, int)
        or baseline_count < 1 or minimum_count < 1
    ):
        raise GateError("invalid test counts")
    if not isinstance(contract["protected_files"], dict) or not contract["protected_files"]:
        raise GateError("protected_files must be a non-empty object")
    normalized_protected: dict[str, str] = {}
    for path, digest in contract["protected_files"].items():
        normalized = normalize_path(path)
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise GateError(f"invalid SHA-256 for {path}")
        normalized_protected[normalized] = digest
    contract["protected_files"] = normalized_protected
    if audit != {"required": True, "independence": "declared_and_procedural"}:
        raise GateError("audit policy invalid")
    for key in ("acceptance_criteria", "express_exclusions"):
        if not isinstance(contract[key], list) or not contract[key] or not all(
            isinstance(item, str) and item.strip() for item in contract[key]
        ):
            raise GateError(f"{key} invalid")


def default_runner(argv: list[str], cwd: Path, env: dict[str, str] | None) -> subprocess.CompletedProcess[str]:
    merged = os.environ.copy()
    for key in tuple(merged):
        if key == "GIT_DIR" or key.startswith("GIT_WORK_TREE"):
            merged.pop(key)
    if env:
        merged.update({
            key: value for key, value in env.items()
            if key != "GIT_DIR" and not key.startswith("GIT_WORK_TREE")
        })
    return subprocess.run(
        argv, cwd=cwd, env=merged, text=True, encoding="utf-8",
        errors="replace", capture_output=True, shell=False, check=False,
    )


def run_git(root: Path, args: list[str], runner: Runner = default_runner) -> str:
    result = runner(
        ["git", "-c", f"safe.directory={root.as_posix()}", *args], root, None
    )
    if result.returncode != 0:
        raise GateError(f"Git indeterminate: {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout


def repository_state(root: Path, baseline: str, runner: Runner = default_runner) -> dict[str, str]:
    top = run_git(root, ["rev-parse", "--show-toplevel"], runner).strip()
    if Path(top).resolve() != root.resolve():
        raise GateError("unexpected repository root")
    branch = run_git(root, ["branch", "--show-current"], runner).strip()
    head = run_git(root, ["rev-parse", "HEAD"], runner).strip()
    run_git(root, ["merge-base", "--is-ancestor", baseline, "HEAD"], runner)
    return {"toplevel": top, "branch": branch, "head": head, "baseline": baseline}


def parse_name_status(raw: str) -> list[Change]:
    fields = raw.split("\0")
    if fields and fields[-1] == "":
        fields.pop()
    changes: list[Change] = []
    index = 0
    while index < len(fields):
        status = fields[index]
        index += 1
        kind = status[:1]
        if kind in {"R", "C"}:
            if index + 1 >= len(fields):
                raise GateError("malformed rename/copy record")
            old_path = normalize_path(fields[index])
            path = normalize_path(fields[index + 1])
            index += 2
            changes.append(Change(kind, path, old_path))
        elif kind in {"A", "M", "D", "T", "U"}:
            if index >= len(fields):
                raise GateError("malformed name-status record")
            changes.append(Change(kind, normalize_path(fields[index])))
            index += 1
        else:
            raise GateError(f"unknown Git status: {status}")
    return changes


def collect_changes(root: Path, baseline: str, runner: Runner = default_runner) -> list[Change]:
    tracked = run_git(
        root, ["diff", "--name-status", "-z", "-M", baseline, "--"], runner
    )
    untracked = run_git(
        root, ["ls-files", "--others", "--exclude-standard", "-z"], runner
    )
    changes = parse_name_status(tracked)
    changes.extend(Change("A", normalize_path(path)) for path in untracked.split("\0") if path)
    unique: dict[tuple[str, str, str | None], Change] = {}
    for change in changes:
        unique[(change.status, change.path, change.old_path)] = change
    return sorted(unique.values(), key=lambda item: (item.path, item.status, item.old_path or ""))


def _matches(path: str, patterns: Iterable[str]) -> bool:
    return any(path == pattern or fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def validate_changes(changes: Iterable[Change], scope: dict[str, Any]) -> list[Change]:
    validated: list[Change] = []
    allowed = scope["allowed_paths"]
    forbidden = scope["forbidden_paths"]
    for change in changes:
        paths = [change.path] + ([change.old_path] if change.old_path else [])
        if any(_matches(path, forbidden) for path in paths):
            raise GateError(f"forbidden path changed: {change.path}")
        if any(not _matches(path, allowed) for path in paths):
            raise GateError(f"path outside allowed scope: {change.path}")
        if change.status == "D" and not scope["allow_deletions"]:
            raise GateError(f"deletion not authorized: {change.path}")
        if change.status == "R" and not scope["allow_renames"]:
            raise GateError(f"rename not authorized: {change.old_path} -> {change.path}")
        if change.status in {"T", "U"}:
            raise GateError(f"unsupported Git state: {change.status} {change.path}")
        validated.append(change)
    return validated


def validate_generated_paths(root: Path, contract: dict[str, Any], runner: Runner = default_runner) -> None:
    task_id = contract["task_id"]
    prefix = f".dpslab/quality-gates/{task_id}/"
    tracked = set(run_git(root, ["ls-files", "-z"], runner).split("\0"))
    for value in contract["scope"]["generated_paths"]:
        path = normalize_path(value)
        if not path.startswith(prefix) or path in tracked:
            raise GateError(f"invalid generated path: {path}")
        destination = root / Path(path)
        current = destination.parent
        while current != root:
            if current.exists() and current.is_symlink():
                raise GateError(f"generated path traverses symlink: {path}")
            current = current.parent
        check = runner(
            ["git", "-c", f"safe.directory={root.as_posix()}", "check-ignore", "-q", "--", path],
            root, None,
        )
        if check.returncode != 0:
            raise GateError(f"generated path is not ignored: {path}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_hashes(root: Path, protected: dict[str, str]) -> dict[str, str]:
    observed: dict[str, str] = {}
    for value, expected in protected.items():
        path = root / Path(value)
        if not path.is_file() or path.is_symlink():
            raise GateError(f"protected file missing or linked: {value}")
        actual = sha256_file(path)
        if actual != expected:
            raise GateError(f"protected hash mismatch: {value}")
        observed[value] = actual
    return observed


def execute_test_command(
    root: Path, command: dict[str, Any], runner: Runner = default_runner
) -> CommandResult:
    cwd = (root / Path(command["working_directory"])).resolve()
    if root.resolve() not in (cwd, *cwd.parents):
        raise GateError("test working directory escapes repository")
    result = runner(command["argv"], cwd, command["environment"])
    combined = f"{result.stdout}\n{result.stderr}"
    match = RUN_LINE.search(combined)
    count = int(match.group(1)) if match else None
    return CommandResult(
        tuple(command["argv"]), command["working_directory"], result.returncode,
        result.stdout, result.stderr, count,
    )


def validate_test_result(result: CommandResult, minimum: int | None = None) -> None:
    combined = f"{result.stdout}\n{result.stderr}"
    if result.returncode != 0 or "\nOK" not in f"\n{combined}":
        raise GateError(f"test command failed: {' '.join(result.argv)}")
    if minimum is not None:
        if result.test_count is None:
            raise GateError("functional test count unavailable")
        if result.test_count < minimum:
            raise GateError(f"functional test count below minimum: {result.test_count} < {minimum}")


def atomic_json(path: Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent,
            prefix=f".{path.name}.", suffix=".tmp", delete=False,
        ) as stream:
            temporary = Path(stream.name)
            json.dump(document, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def compact_result(result: CommandResult) -> dict[str, Any]:
    return {
        "argv": list(result.argv),
        "working_directory": result.cwd,
        "returncode": result.returncode,
        "test_count": result.test_count,
        "stdout_tail": result.stdout[-4000:],
        "stderr_tail": result.stderr[-4000:],
    }


def document_digest(document: dict[str, Any]) -> str:
    material = {
        key: value for key, value in document.items()
        if key != "document_sha256"
    }
    encoded = json.dumps(
        material, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _git_directory(root: Path, argument: str) -> Path:
    value = run_git(root, ["rev-parse", argument]).strip()
    if not value:
        raise GateError("git directory is indeterminate")
    path = Path(value)
    candidate = path if path.is_absolute() else root / path
    if candidate.is_symlink():
        raise GateError("git directory is indeterminate")
    resolved = candidate.resolve()
    if not resolved.is_dir():
        raise GateError("git directory is indeterminate")
    return resolved


def _regular_git_file(path: Path, directory: Path) -> Path:
    if path.is_symlink():
        raise GateError("git directory is indeterminate")
    resolved = path.resolve()
    try:
        resolved.relative_to(directory)
    except ValueError:
        raise GateError("git directory is indeterminate") from None
    if not resolved.is_file():
        raise GateError("git directory is indeterminate")
    return resolved


def _git_path(root: Path, name: str, directory: Path) -> Path:
    value = run_git(root, ["rev-parse", "--git-path", name]).strip()
    if not value:
        raise GateError("git directory is indeterminate")
    path = Path(value)
    candidate = path if path.is_absolute() else root / path
    return _regular_git_file(candidate, directory)


def real_repository_fingerprint(root: Path) -> dict[str, str | None]:
    git_dir = _git_directory(root, "--absolute-git-dir")
    common_git_dir = _git_directory(root, "--git-common-dir")
    head = _git_path(root, "HEAD", git_dir)
    index = _git_path(root, "index", git_dir)
    config = _regular_git_file(common_git_dir / "config", common_git_dir)
    worktree_config_path = git_dir / "config.worktree"
    if worktree_config_path.is_symlink():
        raise GateError("git directory is indeterminate")
    worktree_config = (
        _regular_git_file(worktree_config_path, git_dir)
        if worktree_config_path.exists()
        else None
    )
    return {
        "head": head.read_text(encoding="utf-8"),
        "index_sha256": sha256_file(index),
        "config_sha256": sha256_file(config),
        "config_worktree_sha256": (
            sha256_file(worktree_config) if worktree_config is not None else None
        ),
    }


def candidate_paths(
    root: Path, baseline: str, changes: list[Change], runner: Runner = default_runner
) -> list[str]:
    baseline_files = {
        normalize_path(path)
        for path in run_git(
            root, ["ls-tree", "-r", "--name-only", "-z", baseline], runner
        ).split("\0")
        if path
    }
    for change in changes:
        if change.status == "D":
            baseline_files.discard(change.path)
        elif change.status == "R":
            assert change.old_path is not None
            baseline_files.discard(change.old_path)
            baseline_files.add(change.path)
        else:
            baseline_files.add(change.path)
    return sorted(baseline_files)


def materialize_candidate(
    root: Path,
    destination: Path,
    contract: dict[str, Any],
    changes: list[Change],
    runner: Runner = default_runner,
) -> dict[str, str]:
    paths = candidate_paths(root, contract["baseline_commit"], changes, runner)
    manifest: dict[str, str] = {}
    for relative in paths:
        source = root / Path(relative)
        if not source.is_file() or source.is_symlink():
            raise GateError(f"candidate file missing or linked: {relative}")
        target = destination / Path(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        source_hash = sha256_file(source)
        target_hash = sha256_file(target)
        if source_hash != target_hash:
            raise GateError(f"candidate materialization mismatch: {relative}")
        manifest[relative] = source_hash
    generated = set(contract["scope"]["generated_paths"])
    if any(path in manifest for path in generated):
        raise GateError("generated path entered candidate workspace")
    return manifest


def initialize_temporary_repository(
    workspace: Path, runner: Runner = default_runner
) -> str:
    commands = (
        ["git", "init", "-b", "main"],
        ["git", "add", "-A"],
        [
            "git", "-c", "user.name=DpsLab Quality Gate",
            "-c", "user.email=dpslab-quality-gate@local.invalid",
            "commit", "-m", "ephemeral candidate",
        ],
    )
    for argv in commands:
        result = runner(argv, workspace, None)
        if result.returncode != 0:
            raise GateError(f"temporary Git command failed: {' '.join(argv)}: {result.stderr.strip()}")
    head = runner(["git", "rev-parse", "HEAD"], workspace, None)
    clean = runner(["git", "status", "--porcelain"], workspace, None)
    remotes = runner(["git", "remote", "-v"], workspace, None)
    if head.returncode != 0 or clean.returncode != 0 or clean.stdout or remotes.returncode != 0 or remotes.stdout:
        raise GateError("temporary repository is not clean, committed, and remote-free")
    return head.stdout.strip()


def verify_materialized_candidate(workspace: Path, manifest: dict[str, str]) -> None:
    observed = {
        path.relative_to(workspace).as_posix(): sha256_file(path)
        for path in workspace.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(workspace).parts
    }
    if observed != manifest:
        raise GateError("temporary candidate differs from validated candidate")


def execute_functional_in_temporary_candidate(
    root: Path,
    contract: dict[str, Any],
    changes: list[Change],
    runner: Runner = default_runner,
    temporary_factory: Callable[..., Any] = tempfile.TemporaryDirectory,
) -> tuple[CommandResult, dict[str, Any]]:
    fingerprint = real_repository_fingerprint(root)
    temporary_path: Path | None = None
    try:
        with temporary_factory(prefix="dpslab-quality-gate-") as temporary:
            temporary_path = Path(temporary)
            manifest = materialize_candidate(root, temporary_path, contract, changes, runner)
            temporary_head = initialize_temporary_repository(temporary_path, runner)
            verify_materialized_candidate(temporary_path, manifest)
            result = execute_test_command(temporary_path, contract["tests"]["full"], runner)
            verify_materialized_candidate(temporary_path, manifest)
            clean = runner(["git", "status", "--porcelain"], temporary_path, None)
            if clean.returncode != 0 or clean.stdout:
                raise GateError("temporary repository became dirty during functional tests")
            details = {
                "temporary_commit": temporary_head,
                "candidate_file_count": len(manifest),
                "candidate_manifest_sha256": document_digest(manifest),
                "workspace_clean_after_tests": True,
                "workspace_removed": False,
            }
    except GateError:
        raise
    except Exception as exc:
        raise GateError(f"temporary candidate workspace failed: {exc}") from exc
    finally:
        if real_repository_fingerprint(root) != fingerprint:
            raise GateError("real repository HEAD, index, or config changed")
    if temporary_path is None or temporary_path.exists():
        raise GateError("temporary candidate workspace cleanup failed")
    details["workspace_removed"] = True
    return result, details


def load_contract(root: Path) -> dict[str, Any]:
    return extract_contract((root / "docs/NEXT_TASK.md").read_text(encoding="utf-8"))


def preflight(root: Path, contract: dict[str, Any], runner: Runner = default_runner) -> dict[str, Any]:
    state = repository_state(root, contract["baseline_commit"], runner)
    changes = validate_changes(
        collect_changes(root, contract["baseline_commit"], runner),
        contract["scope"],
    )
    validate_generated_paths(root, contract, runner)
    hashes = verify_hashes(root, contract["protected_files"])
    return {
        "repository": state,
        "changes": [change.__dict__ for change in changes],
        "protected_hashes": hashes,
    }


def run_gate(root: Path, contract: dict[str, Any], runner: Runner = default_runner) -> dict[str, Any]:
    if contract["authorization"]["status"] != "authorized_for_implementation":
        raise GateError("task is not authorized for implementation")
    before = preflight(root, contract, runner)
    focused = execute_test_command(root, contract["tests"]["focused"], runner)
    validate_test_result(focused)
    changes = [Change(**item) for item in before["changes"]]
    full, temporary_workspace = execute_functional_in_temporary_candidate(
        root, contract, changes, runner
    )
    validate_test_result(full, contract["tests"]["minimum_test_count"])
    after = preflight(root, contract, runner)
    if before["changes"] != after["changes"]:
        raise GateError("repository delta changed while tests were running")
    document = {
        "result_version": "0.1",
        "task_id": contract["task_id"],
        "status": "implemented_pending_independent_audit",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "authorization": contract["authorization"],
        "baseline_commit": contract["baseline_commit"],
        "repository": after["repository"],
        "changes": after["changes"],
        "protected_hashes": after["protected_hashes"],
        "tests": {
            "baseline_test_count": contract["tests"]["baseline_test_count"],
            "minimum_test_count": contract["tests"]["minimum_test_count"],
            "focused": compact_result(focused),
            "full": compact_result(full),
        },
        "simulationcraft_invoked": False,
        "functional_workspace": temporary_workspace,
    }
    document["document_sha256"] = document_digest(document)
    implementation_path = root / Path(contract["scope"]["generated_paths"][0])
    atomic_json(implementation_path, document)
    return document


def audit_gate(
    root: Path, contract: dict[str, Any], auditor: str, implementer: str,
    decision: str, runner: Runner = default_runner,
) -> dict[str, Any]:
    if not auditor.strip() or not implementer.strip() or auditor.strip() == implementer.strip():
        raise GateError("auditor and implementer must be distinct declared actors")
    if contract["audit"]["independence"] != "declared_and_procedural":
        raise GateError("declared procedural independence is required")
    if decision not in AUDIT_DECISIONS:
        raise GateError("invalid audit decision")
    preflight(root, contract, runner)
    implementation_path = root / Path(contract["scope"]["generated_paths"][0])
    if not implementation_path.is_file():
        raise GateError("implementation.json is missing")
    implementation = json.loads(implementation_path.read_text(encoding="utf-8"))
    expected_digest = implementation.get("document_sha256")
    if not isinstance(expected_digest, str) or expected_digest != document_digest(implementation):
        raise GateError("implementation.json integrity mismatch")
    checks = [
        "contract validated",
        "real repository delta validated",
        "protected hashes verified",
        "implementation.json integrity verified",
        "declared procedural independence recorded",
    ]
    document = {
        "result_version": "0.1",
        "task_id": contract["task_id"],
        "status": "audit_recorded_not_automatically_approved",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "auditor": auditor.strip(),
        "implementer": implementer.strip(),
        "independence": "declared_and_procedural",
        "independence_is_cryptographic_guarantee": False,
        "implementation_sha256": sha256_file(implementation_path),
        "implementation_status": implementation.get("status"),
        "decision": decision,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "verifications": checks,
        "findings": [],
    }
    atomic_json(root / Path(contract["scope"]["generated_paths"][1]), document)
    return document


def verify_gate(root: Path, contract: dict[str, Any], runner: Runner = default_runner) -> dict[str, Any]:
    state = preflight(root, contract, runner)
    implementation_path = root / Path(contract["scope"]["generated_paths"][0])
    if implementation_path.exists():
        state["implementation_sha256"] = sha256_file(implementation_path)
    return state


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("preflight")
    subparsers.add_parser("run")
    audit_parser = subparsers.add_parser("audit")
    audit_parser.add_argument("--auditor", required=True)
    audit_parser.add_argument("--implementer", required=True)
    audit_parser.add_argument(
        "--decision", required=True, choices=sorted(AUDIT_DECISIONS)
    )
    subparsers.add_parser("verify")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    try:
        contract = load_contract(root)
        if args.command == "preflight":
            result = preflight(root, contract)
        elif args.command == "run":
            result = run_gate(root, contract)
        elif args.command == "audit":
            result = audit_gate(
                root, contract, args.auditor, args.implementer, args.decision
            )
        else:
            result = verify_gate(root, contract)
    except (GateError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"quality_gate_error: {exc}")
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
