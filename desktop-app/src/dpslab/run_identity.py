"""Pure, ephemeral planning of comparison run identities."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import PurePosixPath
from typing import Callable, Literal


class RunIdentityError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class RunIdentityPlan:
    comparison_execution_id: str
    member_id: str
    block_index: int
    attempt: int
    arm: Literal["a", "b"]
    run_id: str
    portable_path: str


RunIdSource = Callable[[], str]
_RUN_ID_PATTERN = re.compile(r"[A-Za-z0-9_.-]+")
_HEX_PATTERN = re.compile(r"[0-9a-fA-F]+")


def build_current_run_id(timestamp: datetime, uuid_hex: str) -> str:
    """Build the exact timestamp-plus-eight-hex convention used by reserve_run."""
    if timestamp.tzinfo is None:
        raise RunIdentityError("run_id timestamp must include timezone")
    if not isinstance(uuid_hex, str) or len(uuid_hex) < 8 or not _HEX_PATTERN.fullmatch(uuid_hex):
        raise RunIdentityError("uuid_hex must contain at least eight hexadecimal characters")
    rendered = timestamp.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    return f"{rendered}-{uuid_hex[:8].lower()}"


def _nonempty_identity(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise RunIdentityError(f"{field_name} is empty or not canonical")
    if "\r" in value or "\n" in value or "\x00" in value:
        raise RunIdentityError(f"{field_name} contains invalid characters")
    return value


def _validate_run_id(run_id: str) -> str:
    if not isinstance(run_id, str) or not run_id or _RUN_ID_PATTERN.fullmatch(run_id) is None:
        raise RunIdentityError("run_id does not match the current convention")
    return run_id


def _portable_root(value: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or value != value.strip():
        raise RunIdentityError("runs root is empty or not canonical")
    if "\\" in value or ":" in value or "\x00" in value:
        raise RunIdentityError("runs root is not portable")
    root = PurePosixPath(value)
    if root.is_absolute() or root == PurePosixPath("."):
        raise RunIdentityError("runs root must be relative")
    if any(part in {"", ".", ".."} for part in root.parts):
        raise RunIdentityError("runs root contains an unsafe segment")
    if root.as_posix() != value:
        raise RunIdentityError("runs root is not in canonical portable form")
    return root


def _expected_member_id(
    comparison_execution_id: str,
    block_index: int,
    attempt: int,
    arm: str,
) -> str:
    return f"{comparison_execution_id}:block-{block_index}:attempt-{attempt}:{arm}"


def validate_run_identity_plan(plan: RunIdentityPlan, *, runs_root_portable: str) -> None:
    execution_id = _nonempty_identity(plan.comparison_execution_id, "comparison_execution_id")
    _nonempty_identity(plan.member_id, "member_id")
    if isinstance(plan.block_index, bool) or not isinstance(plan.block_index, int) or not 1 <= plan.block_index <= 8:
        raise RunIdentityError("block_index is outside the frozen protocol")
    if isinstance(plan.attempt, bool) or not isinstance(plan.attempt, int) or not 1 <= plan.attempt <= 2:
        raise RunIdentityError("attempt is outside the frozen protocol")
    if plan.arm not in {"a", "b"}:
        raise RunIdentityError("arm is invalid")
    expected_member = _expected_member_id(execution_id, plan.block_index, plan.attempt, plan.arm)
    if plan.member_id != expected_member:
        raise RunIdentityError("member_id does not match logical ownership")
    run_id = _validate_run_id(plan.run_id)
    root = _portable_root(runs_root_portable)
    expected_path = (root / run_id).as_posix()
    if plan.portable_path != expected_path:
        raise RunIdentityError("portable path does not match runs root and run_id")
    path = PurePosixPath(plan.portable_path)
    if path.is_absolute() or ":" in plan.portable_path or "\\" in plan.portable_path:
        raise RunIdentityError("portable path is not relative and portable")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise RunIdentityError("portable path contains an unsafe segment")


def select_run_identity(
    *,
    comparison_execution_id: str,
    member_id: str,
    block_index: int,
    attempt: int,
    arm: Literal["a", "b"],
    runs_root_portable: str,
    run_id_source: RunIdSource,
    occupied_run_ids: frozenset[str] = frozenset(),
    occupied_portable_paths: frozenset[str] = frozenset(),
    known_plans: tuple[RunIdentityPlan, ...] = (),
    max_attempts: int = 10,
) -> RunIdentityPlan:
    """Select a provisional identity without reading, claiming, or persisting resources."""
    execution_id = _nonempty_identity(comparison_execution_id, "comparison_execution_id")
    member = _nonempty_identity(member_id, "member_id")
    if not callable(run_id_source):
        raise RunIdentityError("run_id_source must be callable")
    if isinstance(max_attempts, bool) or not isinstance(max_attempts, int) or max_attempts <= 0:
        raise RunIdentityError("max_attempts must be a positive integer")
    root = _portable_root(runs_root_portable)

    ownership_probe = RunIdentityPlan(
        execution_id,
        member,
        block_index,
        attempt,
        arm,
        "ownership-probe",
        (root / "ownership-probe").as_posix(),
    )
    validate_run_identity_plan(ownership_probe, runs_root_portable=runs_root_portable)

    for known in known_plans:
        validate_run_identity_plan(known, runs_root_portable=runs_root_portable)

    for _ in range(max_attempts):
        run_id = _validate_run_id(run_id_source())
        portable_path = (root / run_id).as_posix()
        candidate = RunIdentityPlan(
            execution_id,
            member,
            block_index,
            attempt,
            arm,
            run_id,
            portable_path,
        )
        validate_run_identity_plan(candidate, runs_root_portable=runs_root_portable)

        matching = tuple(
            plan
            for plan in known_plans
            if plan.run_id == run_id or plan.portable_path == portable_path
        )
        if matching:
            if len(matching) == 1 and matching[0] == candidate:
                return candidate
            continue
        if run_id in occupied_run_ids or portable_path in occupied_portable_paths:
            continue
        return candidate
    raise RunIdentityError("no provisional run identity available within max_attempts")
