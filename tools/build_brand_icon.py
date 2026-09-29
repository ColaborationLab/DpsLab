"""Create the Windows icon from the Foundry emblem already used by Link."""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def build(source: Path, output: Path) -> None:
    image = Image.open(source).convert("RGBA")
    emblem = image.crop((90, 75, 602, 587))
    output.parent.mkdir(parents=True, exist_ok=True)
    emblem.save(output, format="ICO", sizes=((16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)))


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Build the DpsFoundry Windows icon")
    parser.add_argument("--source", type=Path, default=root / "addon" / "DpsLab" / "Media" / "foundry-brand-core.tga")
    parser.add_argument("--output", type=Path, default=root / "desktop-app" / "src" / "dpslab" / "assets" / "dpsfoundry-core.ico")
    args = parser.parse_args()
    build(args.source, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
