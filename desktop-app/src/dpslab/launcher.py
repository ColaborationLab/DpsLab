"""Windows desktop entry point for the player-selected class/spec flow."""

import os
from pathlib import Path

from .loadout_ui import TkLoadoutWorkspace


def main() -> int:
    root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "DpsLab"
    root.mkdir(parents=True, exist_ok=True)
    TkLoadoutWorkspace(root).run()
    return 0
