"""Lossless PNG -> padded TGA for WoW; UV selection is done by Link at runtime."""
from pathlib import Path
import struct

from PySide6.QtGui import QImage, QPainter

ROOT = Path(__file__).resolve().parents[1]
source = QImage(str(ROOT / "desktop-app/src/dpslab/assets/foundry-brand-forged-v1.png"))
if source.isNull():
    raise SystemExit("Core brand asset unavailable")
width = 1 << (source.width() - 1).bit_length()
height = 1 << (source.height() - 1).bit_length()
canvas = QImage(width, height, QImage.Format.Format_ARGB32)
canvas.fill(0)
painter = QPainter(canvas)
painter.drawImage(0, 0, source)
painter.end()
target = ROOT / "addon/DpsLab/Media/foundry-brand-core.tga"
target.parent.mkdir(parents=True, exist_ok=True)
# Uncompressed BGRA, top-left origin. Original pixels are neither resized nor edited.
header = struct.pack("<BBBHHBHHHHBB", 0, 0, 2, 0, 0, 0, 0, 0, width, height, 32, 0x28)
target.write_bytes(header + bytes(canvas.constBits()))
print(f"{source.width()}x{source.height()} -> {width}x{height}; {target.name}")
