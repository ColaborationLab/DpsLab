"""Build the one-file Windows desktop package with the supplied SimC CLI."""
from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
import subprocess
import sys
import tkinter


def _require_tcl_runtime() -> None:
    """Avoid producing a windowed package that cannot start its Tk UI."""
    try:
        runtime = tkinter.Tcl()
        runtime.eval("info patchlevel")
    except tkinter.TclError as exc:
        raise SystemExit("Tcl/Tk build resources unavailable") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--simc", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--console", action="store_true")
    args = parser.parse_args()
    simc = args.simc.resolve()
    if simc.name.lower() != "simc.exe" or not simc.is_file():
        raise SystemExit("simc.exe source invalid")
    _require_tcl_runtime()
    output = args.output.resolve(); output.mkdir(parents=True, exist_ok=True)
    notice = output / "SIMULATIONCRAFT_NOTICE.txt"
    notice.write_text(
        "SimulationCraft CLI (simc.exe) is included under GPL v3.\n"
        f"Source SHA-256: {sha256(simc.read_bytes()).hexdigest()}\n"
        "Source: https://github.com/simulationcraft/simc\n",
        encoding="utf-8",
    )
    root = Path(__file__).resolve().parents[1]
    window_mode = "--console" if args.console else "--windowed"
    # PyInstaller's tkinter hook supports the runtime Tcl/Tk version selected
    # by the host Python (including Tcl/Tk 9); do not hard-code 8.6 paths.
    command = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onedir", window_mode, "--name", "DpsLab", "--paths", str(root / "desktop-app" / "src"), "--distpath", str(output), "--workpath", str(output / "work"), "--specpath", str(output / "spec"), "--add-binary", f"{simc};simc", "--add-data", f"{notice};.", str(root / "desktop-app" / "launch_dpslab.py")]
    return subprocess.run(command, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
