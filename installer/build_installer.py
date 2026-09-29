"""Compile the per-user DpsFoundry Core installer from a packaged app directory."""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess


REQUIRED = ("DpsLab.exe", "_internal/LICENSE", "_internal/SIMULATIONCRAFT_NOTICE.txt", "_internal/COPYING", "_internal/simc/simc.exe", "_internal/DpsLabAddon/DpsLab.toc", "_internal/dpslab/assets/dpsfoundry-core.ico")


def build(iscc: Path, package: Path, output: Path) -> int:
    package = package.resolve()
    if not iscc.is_file() or any(not (package / entry).is_file() for entry in REQUIRED):
        raise ValueError("installer_input_invalid")
    output.mkdir(parents=True, exist_ok=True)
    script = Path(__file__).with_name("DpsFoundry.iss")
    return subprocess.run((str(iscc), f"/DSourceDir={package}", f"/DOutputDir={output.resolve()}", str(script)), check=False).returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile the DpsFoundry Core installer")
    parser.add_argument("--iscc", type=Path, required=True)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        return build(args.iscc, args.package, args.output)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    raise SystemExit(main())
