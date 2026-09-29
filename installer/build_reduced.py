"""Build the one-file Windows desktop package with the supplied SimC CLI."""
from __future__ import annotations

import argparse
from hashlib import sha256
from importlib.metadata import distribution
from pathlib import Path
import subprocess
import sys


def _require_qt_runtime() -> None:
    """Avoid producing a windowed package that cannot start its Qt UI."""
    try:
        from PySide6 import QtWidgets
        if QtWidgets.QApplication is None:
            raise RuntimeError("QApplication unavailable")
    except Exception as exc:
        raise SystemExit("Qt build resources unavailable") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--simc", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--console", action="store_true")
    args = parser.parse_args()
    simc = args.simc.resolve()
    if simc.name.lower() != "simc.exe" or not simc.is_file():
        raise SystemExit("simc.exe source invalid")
    _require_qt_runtime()
    output = args.output.resolve(); output.mkdir(parents=True, exist_ok=True)
    qt_runtime_hook = output / "pyi_rth_dpslab_qt.py"
    qt_runtime_hook.write_text(
        "import os\nimport sys\n"
        "root = getattr(sys, '_MEIPASS', '')\n"
        "handles = []\n"
        "for name in ('PySide6', 'shiboken6'):\n"
        "    path = os.path.join(root, name)\n"
        "    if os.path.isdir(path):\n"
        "        os.environ['PATH'] = path + os.pathsep + os.environ.get('PATH', '')\n"
        "        if hasattr(os, 'add_dll_directory'):\n"
        "            handles.append(os.add_dll_directory(path))\n"
        "sys._dpslab_qt_dll_handles = handles\n",
        encoding="utf-8",
    )
    notice = output / "SIMULATIONCRAFT_NOTICE.txt"
    notice.write_text(
        "SimulationCraft CLI (simc.exe) is included under GPL v3.\n"
        f"Binary SHA-256: {sha256(simc.read_bytes()).hexdigest()}\n"
        "Corresponding source: https://github.com/simulationcraft/simc/tree/98395518bc03c99f70668662f5eb6229b357eb9f\n"
        "The binary hash identifies this packaged executable; it is not a source hash or signature.\n",
        encoding="utf-8",
    )
    copying = simc.parent / "COPYING"
    if not copying.is_file():
        raise SystemExit("SimulationCraft COPYING file missing beside simc.exe")
    root = Path(__file__).resolve().parents[1]
    icon = root / "desktop-app" / "src" / "dpslab" / "assets" / "dpsfoundry-core.ico"
    if not icon.is_file():
        raise SystemExit("DpsFoundry icon missing: run tools/build_brand_icon.py first")
    casc = root / 'desktop-app/src/dpslab/native/CascLib.dll'
    if not casc.is_file():
        raise SystemExit('Local icon reader missing: run tools/build_casc_reader.py first')
    window_mode = "--console" if args.console else "--windowed"
    # PyInstaller collects PySide6 hooks and platform plugins from the venv.
    command = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onedir", window_mode, "--name", "DpsLab", "--icon", str(icon), "--paths", str(root / "desktop-app" / "src"), "--collect-submodules", "dpslab.locales", "--runtime-hook", str(qt_runtime_hook), "--distpath", str(output), "--workpath", str(output / "work"), "--specpath", str(output / "spec"), "--add-binary", f"{simc};simc", "--add-data", f"{notice};.", "--add-data", f"{copying};.", "--add-data", f"{root / 'LICENSE'};.", "--add-data", f"{root / 'addon' / 'DpsLab'};DpsLabAddon", "--add-data", f"{root / 'docs' / 'DISTRIBUTION.md'};Documentation", "--add-data", f"{root / 'docs' / 'DISTRIBUTION-es.md'};Documentation", "--add-data", f"{root / 'docs' / 'DISTRIBUTION-en.md'};Documentation", "--add-data", f"{root / 'docs' / 'DISTRIBUTION-pt-BR.md'};Documentation", str(root / "desktop-app" / "launch_dpslab.py")]
    command[3:3] = ["--add-data", f"{root / 'desktop-app' / 'src' / 'dpslab' / 'assets'};dpslab/assets"]
    command[3:3] = ['--add-binary', f'{casc};dpslab/native', '--add-data',
                    f'{casc.parent / "CascLib-LICENSE.txt"};dpslab/native',
                    '--add-data', f'{distribution("Pillow").locate_file("pillow-12.3.0.dist-info/licenses/LICENSE")};Pillow-license',
                    '--hidden-import', 'PIL.BlpImagePlugin']
    result = subprocess.run(command, check=False).returncode
    if result == 0:
        runtime = output / "DpsLab" / "_internal"
        for name in ("icudt78.dll", "icuuc.dll"):
            (runtime / name).unlink(missing_ok=True)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
