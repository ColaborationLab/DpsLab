"""Windows desktop entry point for the player-selected class/spec flow."""

import os
from pathlib import Path

from .qt_loadout_ui import QtLoadoutWorkspace


def main() -> int:
    root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "DpsLab"
    root.mkdir(parents=True, exist_ok=True)
    QtLoadoutWorkspace(root).run()
    return 0
