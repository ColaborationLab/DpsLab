"""The only JSON boundary for comparison_result schema 0.1."""

from __future__ import annotations

import json
import math
import os
import tempfile
from datetime import datetime
from dataclasses import fields, is_dataclass
from pathlib import Path
from types import UnionType
from typing import Literal, Union, get_args, get_origin, get_type_hints

from .comparison_models import ComparisonResult, ComparisonResultError, validate_result


class _ComparisonFileOperations:
    """Injectable physical file boundary used by ComparisonResultStore."""

    def exists(self, path: Path) -> bool:
        return path.exists()

    def read_text(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def make_directory(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)

    def temporary_file(self, directory: Path):
        return tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=directory,
            prefix=".comparison_result.", suffix=".tmp", delete=False,
        )

    def serialize(self, document: dict[str, object], stream: object) -> None:
        json.dump(document, stream, ensure_ascii=False, indent=2, allow_nan=False, sort_keys=True)
        stream.write("\n")  # type: ignore[attr-defined]

    def flush(self, stream: object) -> None:
        stream.flush()  # type: ignore[attr-defined]

    def sync(self, stream: object) -> None:
        os.fsync(stream.fileno())  # type: ignore[attr-defined]

    def close(self, stream: object) -> None:
        stream.close()  # type: ignore[attr-defined]

    def link(self, source: str, destination: Path) -> None:
        os.link(source, destination)

    def replace(self, source: str, destination: Path) -> None:
        os.replace(source, destination)

    def unlink(self, path: Path, *, missing_ok: bool = False) -> None:
        path.unlink(missing_ok=missing_ok)


def _encode(value: object) -> object:
    if is_dataclass(value):
        return {item.name: _encode(getattr(value, item.name)) for item in fields(value)}
    if isinstance(value, (list, tuple)):
        return [_encode(item) for item in value]
    return value


def result_to_document(result: ComparisonResult) -> dict[str, object]:
    validate_result(result)
    document = _encode(result)
    assert isinstance(document, dict)
    document = {"schema_version": "0.1", **document}
    return document


def _decode(annotation: object, value: object, path: str) -> object:
    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin in (Union, UnionType):
        if value is None and type(None) in args:
            return None
        choices = tuple(item for item in args if item is not type(None))
        errors: list[str] = []
        for choice in choices:
            try:
                return _decode(choice, value, path)
            except ComparisonResultError as exc:
                errors.append(str(exc))
        raise ComparisonResultError(f"{path}: tipo invalido")
    if origin is Literal:
        if value not in args or isinstance(value, bool) != any(item is value for item in args if isinstance(item, bool)):
            raise ComparisonResultError(f"{path}: enum invalido")
        return value
    if origin in (list, tuple):
        if not isinstance(value, list):
            raise ComparisonResultError(f"{path}: debe ser lista")
        decoded = [_decode(args[0], item, f"{path}[{index}]") for index, item in enumerate(value)]
        return decoded if origin is list else tuple(decoded)
    if isinstance(annotation, type) and is_dataclass(annotation):
        if not isinstance(value, dict):
            raise ComparisonResultError(f"{path}: debe ser objeto")
        hints = get_type_hints(annotation)
        expected = {item.name for item in fields(annotation)}
        unknown, missing = set(value) - expected, expected - set(value)
        if unknown or missing:
            raise ComparisonResultError(f"{path}: desconocidos={sorted(unknown)} ausentes={sorted(missing)}")
        return annotation(**{name: _decode(hints[name], value[name], f"{path}.{name}") for name in expected})
    if annotation is int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise ComparisonResultError(f"{path}: debe ser int")
        return value
    if annotation is float:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
            raise ComparisonResultError(f"{path}: debe ser numero finito")
        return float(value)
    if annotation is bool:
        if not isinstance(value, bool):
            raise ComparisonResultError(f"{path}: debe ser bool")
        return value
    if annotation is str:
        if not isinstance(value, str):
            raise ComparisonResultError(f"{path}: debe ser texto")
        return value
    if annotation is type(None):
        if value is not None:
            raise ComparisonResultError(f"{path}: debe ser null")
        return None
    raise ComparisonResultError(f"{path}: anotacion no soportada")


def result_from_document(raw: dict[str, object]) -> ComparisonResult:
    if not isinstance(raw, dict) or raw.get("schema_version") != "0.1":
        raise ComparisonResultError("comparison_result 0.1 invalido")
    document = dict(raw)
    document.pop("schema_version")
    result = _decode(ComparisonResult, document, "comparison_result")
    assert isinstance(result, ComparisonResult)
    validate_result(result)
    return result


class ComparisonResultStore:
    def __init__(self, path: Path, *, file_operations: _ComparisonFileOperations | None = None) -> None:
        self.path = path
        self._file_operations = file_operations or _ComparisonFileOperations()

    def read(self) -> ComparisonResult:
        try:
            raw = json.loads(self._file_operations.read_text(self.path))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ComparisonResultError(f"No se pudo leer comparison_result: {exc}") from exc
        if not isinstance(raw, dict):
            raise ComparisonResultError("comparison_result debe ser objeto")
        return result_from_document(raw)

    def write(self, result: ComparisonResult) -> None:
        if self._file_operations.exists(self.path): self.commit(self.read(), result)
        else: self.create(result)

    def create(self, candidate: ComparisonResult) -> ComparisonResult:
        if self._file_operations.exists(self.path): raise ComparisonResultError("comparison_result ya existe")
        self._write_document(result_to_document(candidate), exclusive=True)
        return candidate

    def commit(self, previous: ComparisonResult, candidate: ComparisonResult) -> ComparisonResult:
        if not self._file_operations.exists(self.path) or self.read() != previous: raise ComparisonResultError("previous no coincide con el estado confirmado")
        if len(candidate.events) < len(previous.events) or tuple(candidate.events[:len(previous.events)]) != tuple(previous.events): raise ComparisonResultError("Una actualizacion no puede modificar eventos anteriores")
        _validate_immutable(previous, candidate)
        for name in ("inputs", "normalization", "precision", "protocol"):
            if getattr(previous, name) != getattr(candidate, name): raise ComparisonResultError(f"Seccion congelada modificada: {name}")
        for name in ("blocking_errors", "protocol_failures", "analysis_warnings", "advisory_warnings"):
            old, new = getattr(previous, name), getattr(candidate, name)
            if len(new) < len(old) or new[:len(old)] != old: raise ComparisonResultError(f"Registro acumulativo modificado: {name}")
        self._write_document(result_to_document(candidate), exclusive=False)
        return candidate

    def commit_execution(self, previous: ComparisonResult, candidate: ComparisonResult) -> ComparisonResult:
        if previous is candidate: raise ComparisonResultError("candidate debe ser un objeto independiente")
        allowed = {("ready", "blocked"), ("ready", "running"), ("running", "completed"), ("running", "inconclusive"), ("running", "failed_protocol")}
        if (previous.status, candidate.status) not in allowed: raise ComparisonResultError("Transicion global no permitida")
        frozen = (
            "comparison_id", "comparison_execution_id", "spec_path", "spec_sha256",
            "created_at", "software", "inputs", "normalization", "precision",
            "protocol", "blocks", "validation", "analysis",
        )
        if any(getattr(previous, name) != getattr(candidate, name) for name in frozen): raise ComparisonResultError("Identidad o seccion congelada modificada")
        if len(candidate.events) != len(previous.events) + 1 or tuple(candidate.events[:-1]) != tuple(previous.events): raise ComparisonResultError("La transicion global requiere exactamente un evento nuevo")
        event = candidate.events[-1]
        if event.sequence != len(candidate.events) or not event.event_id or any(old.event_id == event.event_id for old in previous.events): raise ComparisonResultError("Secuencia o event_id global invalido")
        if (event.entity_type, event.entity_id, event.previous_status, event.new_status) != ("comparison_execution", previous.comparison_execution_id, previous.status, candidate.status): raise ComparisonResultError("Evento global no corresponde a la transicion")
        if not event.reason.strip(): raise ComparisonResultError("Motivo global vacio")
        try: event_time = datetime.fromisoformat(event.occurred_at.replace("Z", "+00:00"))
        except (TypeError, ValueError) as exc: raise ComparisonResultError("Timestamp global invalido") from exc
        try: updated_time = datetime.fromisoformat(candidate.updated_at.replace("Z", "+00:00"))
        except (TypeError, ValueError) as exc: raise ComparisonResultError("updated_at global invalido") from exc
        if candidate.updated_at == previous.updated_at or updated_time < event_time: raise ComparisonResultError("updated_at no corresponde al evento global")
        if (previous.status, candidate.status) == ("ready", "running"):
            if previous.started_at is not None or candidate.started_at is None: raise ComparisonResultError("started_at global invalido")
            try: datetime.fromisoformat(candidate.started_at.replace("Z", "+00:00"))
            except (TypeError, ValueError) as exc: raise ComparisonResultError("started_at global invalido") from exc
        elif candidate.started_at != previous.started_at: raise ComparisonResultError("started_at global modificado")
        if candidate.status in {"completed", "inconclusive", "failed_protocol"}:
            if previous.finished_at is not None or candidate.finished_at is None: raise ComparisonResultError("finished_at global invalido")
            try: datetime.fromisoformat(candidate.finished_at.replace("Z", "+00:00"))
            except (TypeError, ValueError) as exc: raise ComparisonResultError("finished_at global invalido") from exc
        elif candidate.finished_at != previous.finished_at: raise ComparisonResultError("finished_at global modificado")
        return self.commit(previous, candidate)

    def commit_member(
        self,
        previous: ComparisonResult,
        candidate: ComparisonResult,
        member_id: str,
    ) -> ComparisonResult:
        from .comparison_transitions import validate_member_candidate

        validate_member_candidate(previous, candidate, member_id)
        return self.commit(previous, candidate)

    def _write_document(self, document: dict[str, object], *, exclusive: bool) -> None:
        operations = self._file_operations
        operations.make_directory(self.path.parent)
        temporary: str | None = None
        try:
            stream = operations.temporary_file(self.path.parent)
            temporary = stream.name
            try:
                operations.serialize(document, stream)
                operations.flush(stream)
                operations.sync(stream)
            finally:
                operations.close(stream)
            if exclusive:
                try: operations.link(temporary, self.path)
                except FileExistsError as exc: raise ComparisonResultError("comparison_result ya existe") from exc
                operations.unlink(Path(temporary))
            else: operations.replace(temporary, self.path)
            temporary = None
        finally:
            if temporary is not None:
                operations.unlink(Path(temporary), missing_ok=True)


def _validate_immutable(old: ComparisonResult, new: ComparisonResult) -> None:
    frozen = ("comparison_id", "comparison_execution_id", "spec_sha256", "spec_path", "created_at")
    if any(getattr(old, name) != getattr(new, name) for name in frozen):
        raise ComparisonResultError("Identidad durable modificada")
    old_members = {m.member_id: m for b in old.blocks for a in b.attempts for m in a.members}
    new_members = {m.member_id: m for b in new.blocks for a in b.attempts for m in a.members}
    for member_id, member in old_members.items():
        current = new_members.get(member_id)
        if current is None:
            raise ComparisonResultError("Miembro durable eliminado")
        immutable = ("comparison_execution_id", "comparison_spec_sha256", "block_index", "attempt", "arm", "order_position", "seed", "planned_run_id")
        if any(getattr(member, name) != getattr(current, name) for name in immutable):
            raise ComparisonResultError("Identidad de miembro modificada")
        if member.run_id is not None and member.run_id != current.run_id:
            raise ComparisonResultError("run_id modificado")
        if member.reservation.owner_execution_id != current.reservation.owner_execution_id or member.reservation.owner_member_id != current.reservation.owner_member_id:
            raise ComparisonResultError("Owner de reserva modificado")
        if member.status in {"completed", "invalid", "interrupted"} and member != current:
            raise ComparisonResultError("Entidad terminal modificada")
        if member.integrity is not None and member.integrity.artifacts_verified and member.artifacts != current.artifacts:
            raise ComparisonResultError("Artefactos verificados sustituidos")
