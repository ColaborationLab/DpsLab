"""Strict Windows-aware cleanup for test-only temporary directories."""

from __future__ import annotations

from contextlib import contextmanager
import shutil
import tempfile
import time
from pathlib import Path
from typing import Iterator


def _is_directory_not_empty(error: OSError) -> bool:
    return 145 in {getattr(error, "winerror", None), getattr(error, "errno", None)}


def strict_temporary_cleanup(
    temporary: tempfile.TemporaryDirectory[str], root: Path
) -> None:
    try:
        temporary.cleanup()
    except OSError as error:
        if not _is_directory_not_empty(error):
            raise
        for attempt in range(5):
            try:
                shutil.rmtree(root)
                return
            except OSError as retry_error:
                if not _is_directory_not_empty(retry_error) or attempt == 4:
                    raise
                time.sleep(0.05 * (attempt + 1))


@contextmanager
def strict_temporary_directory() -> Iterator[Path]:
    temporary = tempfile.TemporaryDirectory()
    root = Path(temporary.name)
    try:
        yield root
    finally:
        strict_temporary_cleanup(temporary, root)
