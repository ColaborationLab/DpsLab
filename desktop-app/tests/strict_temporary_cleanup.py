"""Strict Windows-aware cleanup for test-only temporary directories."""

from __future__ import annotations

import shutil
import tempfile
import time
from pathlib import Path


def strict_temporary_cleanup(
    temporary: tempfile.TemporaryDirectory[str], root: Path
) -> None:
    try:
        temporary.cleanup()
    except OSError as error:
        if getattr(error, "winerror", None) != 145:
            raise
        for attempt in range(5):
            try:
                shutil.rmtree(root)
                return
            except OSError as retry_error:
                if getattr(retry_error, "winerror", None) != 145 or attempt == 4:
                    raise
                time.sleep(0.05 * (attempt + 1))
