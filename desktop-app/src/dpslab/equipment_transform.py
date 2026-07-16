"""Typed, neck-only profile transformation independent from ProfileVariant."""

from __future__ import annotations

import os
import re
import tempfile
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from .comparison_spec import ComparisonArm


class EquipmentTransformError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class EquipmentTransformResult:
    arm: str
    source_line: str
    effective_line: str
    base_sha256: str
    effective_sha256: str
    only_neck_changed: bool


def materialize_neck_profile(base: bytes, arm: ComparisonArm, destination: Path) -> EquipmentTransformResult:
    if arm.slot != "neck":
        raise EquipmentTransformError("La transformacion solo acepta el slot neck")
    text = base.decode("utf-8", errors="strict")
    matches = list(re.finditer(r"(?m)^neck=[^\r\n]*(?=\r?$)", text))
    if len(matches) != 1:
        raise EquipmentTransformError(f"Se esperaba una linea neck activa; se encontraron {len(matches)}")
    source_line = matches[0].group(0)
    prefix, suffix = text[:matches[0].start()], text[matches[0].end():]
    output_text = prefix + arm.expected_profile_line + suffix
    if not output_text.startswith(prefix) or not output_text.endswith(suffix):
        raise EquipmentTransformError("La transformacion intento cambiar contenido fuera de neck")
    output = output_text.encode("utf-8")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile("wb", dir=destination.parent, prefix=".equipment_profile.", suffix=".tmp", delete=False) as stream:
            temporary = stream.name
            stream.write(output)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
        temporary = None
    finally:
        if temporary is not None:
            Path(temporary).unlink(missing_ok=True)
    return EquipmentTransformResult(arm.key, source_line, arm.expected_profile_line, sha256(base).hexdigest(), sha256(output).hexdigest(), True)
