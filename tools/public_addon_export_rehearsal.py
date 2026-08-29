"""Local-only synthetic rehearsal for a future public addon export."""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable, Mapping


ALLOWED_CLASSIFICATIONS = frozenset({"public_safe_addon", "public_safe_documentation"})
ENTRY_KEYS = frozenset({"path", "classification", "content", "sha256"})
SECRET_PATTERN = re.compile(
    rb"(?:-----BEGIN [A-Z ]+PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9_]{8,}|"
    rb"sk-[A-Za-z0-9_-]{8,})"
)


class ExportRehearsalError(ValueError):
    """Raised when a synthetic export cannot be safely materialized."""


@dataclass(frozen=True)
class ExportReceipt:
    staging_dir: Path
    file_count: int
    aggregate_sha256: str
    file_sha256: tuple[tuple[str, str], ...]


def _normalize_relative_path(value: object) -> str:
    if not isinstance(value, str) or not value or "\\" in value or value.startswith("./"):
        raise ExportRehearsalError("path must be a non-empty POSIX relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or "." in path.parts or ".." in path.parts:
        raise ExportRehearsalError(f"unsafe path: {value}")
    return path.as_posix()


def _validated_entries(entries: Iterable[Mapping[str, object]]) -> tuple[tuple[str, bytes, str], ...]:
    normalized: list[tuple[str, bytes, str]] = []
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, Mapping) or set(entry) != ENTRY_KEYS:
            raise ExportRehearsalError("entry must contain only path classification content sha256")
        path = _normalize_relative_path(entry["path"])
        classification = entry["classification"]
        if classification not in ALLOWED_CLASSIFICATIONS:
            raise ExportRehearsalError(f"unapproved classification for {path}")
        content = entry["content"]
        if not isinstance(content, bytes):
            raise ExportRehearsalError(f"content must be bytes for {path}")
        if SECRET_PATTERN.search(content):
            raise ExportRehearsalError(f"secret-shaped content for {path}")
        expected = entry["sha256"]
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise ExportRehearsalError(f"invalid sha256 for {path}")
        observed = hashlib.sha256(content).hexdigest()
        if observed != expected:
            raise ExportRehearsalError(f"sha256 mismatch for {path}")
        if path in seen:
            raise ExportRehearsalError(f"duplicate path: {path}")
        seen.add(path)
        normalized.append((path, content, observed))
    if not normalized:
        raise ExportRehearsalError("manifest must contain at least one entry")
    return tuple(sorted(normalized))


def _aggregate_sha256(entries: Iterable[tuple[str, bytes, str]]) -> str:
    digest = hashlib.sha256()
    for path, _content, file_digest in entries:
        digest.update(path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_digest.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def materialize_synthetic_export(
    entries: Iterable[Mapping[str, object]], staging_dir: Path,
) -> ExportReceipt:
    """Write a validated synthetic manifest atomically to an empty new directory.

    The caller supplies a local staging path. Existing paths are rejected, and
    all manifest validation occurs before any directory is created.
    """

    validated = _validated_entries(entries)
    target = Path(staging_dir)
    if target.exists():
        raise ExportRehearsalError(f"staging path already exists: {target}")
    parent = target.parent
    if not parent.is_dir():
        raise ExportRehearsalError(f"staging parent does not exist: {parent}")

    temporary = Path(tempfile.mkdtemp(prefix=f".{target.name}.", dir=parent))
    try:
        for path, content, expected in validated:
            output = temporary.joinpath(*PurePosixPath(path).parts)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(content)
            if hashlib.sha256(output.read_bytes()).hexdigest() != expected:
                raise ExportRehearsalError(f"post-write sha256 mismatch for {path}")
        os.replace(temporary, target)
    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary)
        raise

    file_sha256 = tuple((path, digest) for path, _content, digest in validated)
    return ExportReceipt(
        staging_dir=target,
        file_count=len(file_sha256),
        aggregate_sha256=_aggregate_sha256(validated),
        file_sha256=file_sha256,
    )
