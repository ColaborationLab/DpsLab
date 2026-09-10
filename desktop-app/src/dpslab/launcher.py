"""Windows desktop entry point for the current real Druid flow."""

import os
from pathlib import Path

from .druid_restoration_ui import TkDruidBalanceWorkspace


def main() -> int:
    root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "DpsLab"
    root.mkdir(parents=True, exist_ok=True)
    TkDruidBalanceWorkspace(root).run()
    return 0
