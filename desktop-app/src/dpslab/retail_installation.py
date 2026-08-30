"""Strict validation for one caller-selected World of Warcraft Retail root."""

from __future__ import annotations

import os
from pathlib import Path
import stat as stat_module


class RetailInstallationError(ValueError):
    """The selected path is not a safe, exact Retail installation root."""


_SELECTION_TOKEN = object()
_REPARSE_ATTRIBUTE = getattr(stat_module, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)


class RetailInstallationSelection:
    """Runtime-only validated selection with a path-redacted representation."""

    __slots__ = ("_root",)

    def __init__(self, token: object, root: Path) -> None:
        if token is not _SELECTION_TOKEN:
            raise TypeError("retail_installation_selection_factory_required")
        object.__setattr__(self, "_root", root)

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("retail_installation_selection_immutable")

    @property
    def root(self) -> Path:
        return self._root

    @property
    def product(self) -> str:
        return "retail"

    def __repr__(self) -> str:
        return "RetailInstallationSelection(product='retail', path=<redacted>)"

    __str__ = __repr__


def _fail(reason: str) -> None:
    raise RetailInstallationError(reason)


def _snapshot(value: os.stat_result) -> tuple[int, int, int, int]:
    return value.st_dev, value.st_ino, value.st_mode, value.st_mtime_ns


def _lstat(path: Path, reason: str) -> os.stat_result:
    try:
        value = path.lstat()
    except OSError as exc:
        raise RetailInstallationError(reason) from exc
    if stat_module.S_ISLNK(value.st_mode) or bool(
        getattr(value, "st_file_attributes", 0) & _REPARSE_ATTRIBUTE
    ):
        _fail("retail_installation_reparse_rejected")
    return value


def _direct_child(root: Path, exact_name: str, reason: str) -> Path:
    try:
        matches = [entry for entry in root.iterdir() if entry.name == exact_name]
    except OSError as exc:
        raise RetailInstallationError("retail_installation_root_unreadable") from exc
    if len(matches) != 1:
        _fail(reason)
    return matches[0]


def validate_retail_installation_root(root: Path) -> RetailInstallationSelection:
    """Validate exact local structure without discovery, execution, or file reads."""
    if not isinstance(root, Path) or not root.is_absolute() or root.name != "_retail_":
        _fail("retail_installation_root_invalid")
    root_stat = _lstat(root, "retail_installation_root_invalid")
    if not stat_module.S_ISDIR(root_stat.st_mode):
        _fail("retail_installation_root_invalid")
    executable = _direct_child(root, "Wow.exe", "retail_installation_executable_missing")
    executable_stat = _lstat(executable, "retail_installation_executable_invalid")
    if not stat_module.S_ISREG(executable_stat.st_mode) or executable_stat.st_size < 1:
        _fail("retail_installation_executable_invalid")
    interface = _direct_child(root, "Interface", "retail_installation_interface_missing")
    interface_stat = _lstat(interface, "retail_installation_interface_invalid")
    if not stat_module.S_ISDIR(interface_stat.st_mode):
        _fail("retail_installation_interface_invalid")
    if _snapshot(_lstat(root, "retail_installation_root_changed")) != _snapshot(root_stat):
        _fail("retail_installation_root_changed")
    return RetailInstallationSelection(_SELECTION_TOKEN, root)
