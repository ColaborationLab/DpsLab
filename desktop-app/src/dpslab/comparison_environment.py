"""Reproducible software identity for comparison_result 0.1."""

from __future__ import annotations

import platform
import shutil
import struct
import subprocess
import sys
from hashlib import sha256
from importlib.metadata import version
from pathlib import Path
from .comparison_models import ComparisonSoftware, DpsLabSourceIdentity, PlatformIdentity, PythonIdentity, ScipyIdentity, SimulationCraftIdentity


def source_tree_inventory(source: Path) -> tuple[str, ...]:
    """Portable, deterministic list of files covered by source identity v1."""
    return tuple(
        path.relative_to(source).as_posix()
        for path in sorted(
            (item for item in source.rglob("*") if item.is_file() and "__pycache__" not in item.parts and item.suffix != ".pyc" and not item.name.endswith(".tmp")),
            key=lambda item: item.relative_to(source).as_posix(),
        )
    )


def source_tree_sha256(source: Path) -> str:
    digest = sha256()
    files = [source / relative for relative in source_tree_inventory(source)]
    digest.update(struct.pack(">I", len(files)))
    for path in files:
        relative = path.relative_to(source).as_posix().encode("utf-8")
        content = path.read_bytes()
        digest.update(struct.pack(">I", len(relative)))
        digest.update(relative)
        digest.update(struct.pack(">Q", len(content)))
        digest.update(content)
    return digest.hexdigest()


def dpslab_source_identity(root: Path) -> DpsLabSourceIdentity:
    git = shutil.which("git")
    if git is not None:
        try:
            commit = subprocess.run([git, "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True, shell=False).stdout.strip()
            dirty = bool(subprocess.run([git, "status", "--porcelain"], cwd=root, capture_output=True, text=True, check=True, shell=False).stdout)
            return DpsLabSourceIdentity("git_commit", "0.1.0", commit, dirty, None)
        except (OSError, subprocess.SubprocessError):
            pass
    source = root / "desktop-app" / "src" / "dpslab"
    inventory = source_tree_inventory(source)
    return DpsLabSourceIdentity("dpslab_source_tree_sha256_v1", "0.1.0", None, None, source_tree_sha256(source), "sorted_portable_paths_v1", inventory)


def software_record(root: Path) -> ComparisonSoftware:
    return ComparisonSoftware(
        PythonIdentity(platform.python_version(), platform.python_implementation()),
        dpslab_source_identity(root),
        ScipyIdentity(">=1.11.0,<2.0.0", version("scipy")),
        PlatformIdentity(platform.system(), platform.release(), platform.machine(), sys.platform),
        SimulationCraftIdentity(None, None, None),
    )
