"""Bounded local acquisition for one synthetic DpsLab SavedVariables export."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import os
from pathlib import Path
import stat as stat_module

from .addon_observation_transport import (
    AddonObservationTransportError,
    MAX_PAYLOAD_BYTES,
    SyntheticAddonObservation,
    parse_synthetic_saved_variable,
)


class AddonObservationAcquisitionError(ValueError):
    """The local observation source is unsafe, ambiguous, or incompatible."""


@dataclass(frozen=True)
class SyntheticObservationAcquisition:
    state: str
    byte_count: int
    source_sha256: str | None
    observation: SyntheticAddonObservation | None


MAX_TRANSPORT_BYTES = 2 * MAX_PAYLOAD_BYTES + 64
_CLEARED_ASSIGNMENT = b"\r\nDpsLabObservationExport = nil\r\n"
_REPARSE_ATTRIBUTE = getattr(stat_module, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)


def _fail(reason: str) -> None:
    raise AddonObservationAcquisitionError(reason)


def _snapshot(value: os.stat_result) -> tuple[int, int, int, int]:
    return (
        value.st_dev,
        value.st_ino,
        value.st_size,
        value.st_mtime_ns,
    )


def _is_reparse(value: os.stat_result) -> bool:
    return bool(getattr(value, "st_file_attributes", 0) & _REPARSE_ATTRIBUTE)


def _lstat(path: Path, reason: str) -> os.stat_result:
    try:
        value = path.lstat()
    except OSError as exc:
        raise AddonObservationAcquisitionError(reason) from exc
    if stat_module.S_ISLNK(value.st_mode) or _is_reparse(value):
        _fail("addon_observation_acquisition_reparse_rejected")
    return value


def _directory(path: Path, reason: str) -> None:
    if not stat_module.S_ISDIR(_lstat(path, reason).st_mode):
        _fail(reason)


def _candidate_files(retail_root: Path) -> list[Path]:
    wtf_root = retail_root / "WTF"
    if not os.path.lexists(wtf_root):
        return []
    _directory(wtf_root, "addon_observation_acquisition_wtf_root_invalid")
    account_root = wtf_root / "Account"
    if not os.path.lexists(account_root):
        return []
    _directory(account_root, "addon_observation_acquisition_account_root_invalid")
    candidates: list[Path] = []
    try:
        accounts = list(account_root.iterdir())
    except OSError as exc:
        raise AddonObservationAcquisitionError(
            "addon_observation_acquisition_account_root_unreadable"
        ) from exc
    for account in accounts:
        account_stat = _lstat(account, "addon_observation_acquisition_account_entry_invalid")
        if not stat_module.S_ISDIR(account_stat.st_mode):
            continue
        saved_variables = account / "SavedVariables"
        if not os.path.lexists(saved_variables):
            continue
        _directory(
            saved_variables,
            "addon_observation_acquisition_saved_variables_invalid",
        )
        try:
            entries = list(saved_variables.iterdir())
        except OSError as exc:
            raise AddonObservationAcquisitionError(
                "addon_observation_acquisition_saved_variables_unreadable"
            ) from exc
        for entry in entries:
            if entry.name != "DpsLab.lua":
                continue
            value = _lstat(entry, "addon_observation_acquisition_file_invalid")
            if not stat_module.S_ISREG(value.st_mode):
                _fail("addon_observation_acquisition_file_invalid")
            candidates.append(entry)
    return candidates


def _read_bounded(path: Path) -> bytes:
    initial = _lstat(path, "addon_observation_acquisition_file_invalid")
    if not stat_module.S_ISREG(initial.st_mode):
        _fail("addon_observation_acquisition_file_invalid")
    if not 1 <= initial.st_size <= MAX_TRANSPORT_BYTES:
        _fail("addon_observation_acquisition_file_size_invalid")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise AddonObservationAcquisitionError(
            "addon_observation_acquisition_file_unreadable"
        ) from exc
    try:
        opened = os.fstat(descriptor)
        if (
            not stat_module.S_ISREG(opened.st_mode)
            or _is_reparse(opened)
            or _snapshot(opened) != _snapshot(initial)
        ):
            _fail("addon_observation_acquisition_file_changed")
        raw = os.read(descriptor, MAX_TRANSPORT_BYTES + 1)
        final_handle = os.fstat(descriptor)
    except OSError as exc:
        raise AddonObservationAcquisitionError(
            "addon_observation_acquisition_file_unreadable"
        ) from exc
    finally:
        os.close(descriptor)
    final_path = _lstat(path, "addon_observation_acquisition_file_changed")
    if (
        _snapshot(opened) != _snapshot(final_handle)
        or _snapshot(opened) != _snapshot(final_path)
        or len(raw) != opened.st_size
    ):
        _fail("addon_observation_acquisition_file_changed")
    if len(raw) > MAX_TRANSPORT_BYTES:
        _fail("addon_observation_acquisition_file_size_invalid")
    return raw


def acquire_synthetic_observation(
    retail_root: Path, *, wow_process_state: str
) -> SyntheticObservationAcquisition:
    """Acquire one sanitized synthetic observation without retaining its path or bytes."""
    if wow_process_state != "stopped":
        _fail("addon_observation_acquisition_wow_not_stopped")
    if not isinstance(retail_root, Path) or not retail_root.is_absolute():
        _fail("addon_observation_acquisition_root_invalid")
    _directory(retail_root, "addon_observation_acquisition_root_invalid")
    candidates = _candidate_files(retail_root)
    if not candidates:
        return SyntheticObservationAcquisition("absent", 0, None, None)
    if len(candidates) != 1:
        _fail("addon_observation_acquisition_ambiguous")
    raw = _read_bounded(candidates[0])
    digest = sha256(raw).hexdigest()
    if raw == _CLEARED_ASSIGNMENT:
        return SyntheticObservationAcquisition("cleared", len(raw), digest, None)
    try:
        observation = parse_synthetic_saved_variable(raw)
    except AddonObservationTransportError as exc:
        raise AddonObservationAcquisitionError(
            "addon_observation_acquisition_transport_invalid"
        ) from exc
    return SyntheticObservationAcquisition("available", len(raw), digest, observation)
