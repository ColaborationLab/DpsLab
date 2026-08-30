"""Atomic local store for one explicitly selected Retail installation root."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import stat as stat_module
import tempfile
from typing import Any

from .retail_installation import (
    RetailInstallationError,
    RetailInstallationSelection,
    validate_retail_installation_root,
)


class RetailInstallationStoreError(ValueError):
    """The local selection document is unsafe, invalid, or unavailable."""


@dataclass(frozen=True)
class RetailInstallationStoreReceipt:
    state: str
    byte_count: int


@dataclass(frozen=True)
class StoredRetailInstallation:
    state: str
    byte_count: int
    selection: RetailInstallationSelection | None


DOCUMENT_NAME = "retail_installation_0_1.json"
MAX_DOCUMENT_BYTES = 2048
_FIELDS = {"schema_version", "product", "retail_root"}
_REPARSE_ATTRIBUTE = getattr(stat_module, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)


def _fail(reason: str) -> None:
    raise RetailInstallationStoreError(reason)


def _identity(value: os.stat_result) -> tuple[int, int, int]:
    return value.st_dev, value.st_ino, value.st_mode


def _snapshot(value: os.stat_result) -> tuple[int, int, int, int]:
    return value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns


def _lstat(path: Path, reason: str) -> os.stat_result:
    try:
        value = path.lstat()
    except OSError as exc:
        raise RetailInstallationStoreError(reason) from exc
    if stat_module.S_ISLNK(value.st_mode) or bool(
        getattr(value, "st_file_attributes", 0) & _REPARSE_ATTRIBUTE
    ):
        _fail("retail_installation_store_reparse_rejected")
    return value


def _config_root(path: Path) -> os.stat_result:
    if not isinstance(path, Path) or not path.is_absolute():
        _fail("retail_installation_store_root_invalid")
    value = _lstat(path, "retail_installation_store_root_invalid")
    if not stat_module.S_ISDIR(value.st_mode):
        _fail("retail_installation_store_root_invalid")
    return value


def _canonical(document: dict[str, Any]) -> bytes:
    return (
        json.dumps(document, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _fail("retail_installation_store_duplicate_key")
        result[key] = value
    return result


def _read_bounded(path: Path) -> bytes:
    initial = _lstat(path, "retail_installation_store_file_invalid")
    if not stat_module.S_ISREG(initial.st_mode) or not 1 <= initial.st_size <= MAX_DOCUMENT_BYTES:
        _fail("retail_installation_store_file_invalid")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise RetailInstallationStoreError("retail_installation_store_file_unreadable") from exc
    try:
        opened = os.fstat(descriptor)
        if not stat_module.S_ISREG(opened.st_mode) or _snapshot(opened) != _snapshot(initial):
            _fail("retail_installation_store_file_changed")
        raw = os.read(descriptor, MAX_DOCUMENT_BYTES + 1)
        final_handle = os.fstat(descriptor)
    except OSError as exc:
        raise RetailInstallationStoreError("retail_installation_store_file_unreadable") from exc
    finally:
        os.close(descriptor)
    final_path = _lstat(path, "retail_installation_store_file_changed")
    if (
        _snapshot(opened) != _snapshot(final_handle)
        or _snapshot(opened) != _snapshot(final_path)
        or len(raw) != opened.st_size
    ):
        _fail("retail_installation_store_file_changed")
    return raw


def _validated_selection(selection: RetailInstallationSelection) -> RetailInstallationSelection:
    if not isinstance(selection, RetailInstallationSelection):
        _fail("retail_installation_store_selection_invalid")
    try:
        return validate_retail_installation_root(selection.root)
    except RetailInstallationError as exc:
        raise RetailInstallationStoreError("retail_installation_store_selection_invalid") from exc


def store_retail_installation(
    config_root: Path, selection: RetailInstallationSelection
) -> RetailInstallationStoreReceipt:
    """Atomically persist one explicit validated selection in a caller-provided root."""
    root_before = _config_root(config_root)
    current = _validated_selection(selection)
    document = {
        "schema_version": "0.1",
        "product": "retail",
        "retail_root": str(current.root),
    }
    raw = _canonical(document)
    if len(raw) > MAX_DOCUMENT_BYTES:
        _fail("retail_installation_store_document_too_large")
    target = config_root / DOCUMENT_NAME
    if os.path.lexists(target):
        existing = _lstat(target, "retail_installation_store_file_invalid")
        if not stat_module.S_ISREG(existing.st_mode):
            _fail("retail_installation_store_file_invalid")
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=config_root,
            prefix=".retail-installation-",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary_path = Path(stream.name)
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        temporary = _lstat(temporary_path, "retail_installation_store_temporary_invalid")
        if not stat_module.S_ISREG(temporary.st_mode) or temporary.st_size != len(raw):
            _fail("retail_installation_store_temporary_invalid")
        if _identity(_config_root(config_root)) != _identity(root_before):
            _fail("retail_installation_store_root_changed")
        os.replace(temporary_path, target)
        temporary_path = None
        if _read_bounded(target) != raw:
            _fail("retail_installation_store_commit_mismatch")
    except RetailInstallationStoreError:
        raise
    except OSError as exc:
        raise RetailInstallationStoreError("retail_installation_store_write_failed") from exc
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
    return RetailInstallationStoreReceipt("stored", len(raw))


def load_retail_installation(config_root: Path) -> StoredRetailInstallation:
    """Load and revalidate the local selection without exposing its path in the result repr."""
    _config_root(config_root)
    target = config_root / DOCUMENT_NAME
    if not os.path.lexists(target):
        return StoredRetailInstallation("absent", 0, None)
    raw = _read_bounded(target)
    try:
        document = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RetailInstallationStoreError("retail_installation_store_document_invalid") from exc
    if not isinstance(document, dict) or set(document) != _FIELDS:
        _fail("retail_installation_store_document_fields_invalid")
    if document["schema_version"] != "0.1" or document["product"] != "retail":
        _fail("retail_installation_store_document_incompatible")
    value = document["retail_root"]
    if not isinstance(value, str) or not 1 <= len(value) <= 1024 or "\x00" in value:
        _fail("retail_installation_store_path_invalid")
    if raw != _canonical(document):
        _fail("retail_installation_store_document_noncanonical")
    try:
        selection = validate_retail_installation_root(Path(value))
    except RetailInstallationError as exc:
        raise RetailInstallationStoreError("retail_installation_store_selection_invalid") from exc
    return StoredRetailInstallation("selected", len(raw), selection)
