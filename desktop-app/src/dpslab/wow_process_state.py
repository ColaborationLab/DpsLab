"""Sanitized, fail-closed native Windows probe for the retail WoW process."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass
import os


@dataclass(frozen=True)
class WoWProcessState:
    state: str
    matching_process_count: int


_TH32CS_SNAPPROCESS = 0x00000002
_ERROR_NO_MORE_FILES = 18
_MAX_PATH = 260
_MAX_ENUMERATED_PROCESSES = 65536
_MAX_MATCHING_PROCESSES = 16
_INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value


class _PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.c_size_t),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", wintypes.LONG),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", wintypes.WCHAR * _MAX_PATH),
    ]


def _kernel32():
    if not hasattr(ctypes, "WinDLL"):
        raise OSError("native_windows_api_unavailable")
    library = ctypes.WinDLL("kernel32", use_last_error=True)
    library.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    library.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    pointer = ctypes.POINTER(_PROCESSENTRY32W)
    library.Process32FirstW.argtypes = [wintypes.HANDLE, pointer]
    library.Process32FirstW.restype = wintypes.BOOL
    library.Process32NextW.argtypes = [wintypes.HANDLE, pointer]
    library.Process32NextW.restype = wintypes.BOOL
    library.CloseHandle.argtypes = [wintypes.HANDLE]
    library.CloseHandle.restype = wintypes.BOOL
    return library


def _windows_matching_process_count() -> int:
    library = _kernel32()
    snapshot = library.CreateToolhelp32Snapshot(_TH32CS_SNAPPROCESS, 0)
    if snapshot is None or snapshot == _INVALID_HANDLE_VALUE:
        raise OSError("process_snapshot_unavailable")
    try:
        entry = _PROCESSENTRY32W()
        entry.dwSize = ctypes.sizeof(_PROCESSENTRY32W)
        ctypes.set_last_error(0)
        available = library.Process32FirstW(snapshot, ctypes.byref(entry))
        if not available:
            if ctypes.get_last_error() == _ERROR_NO_MORE_FILES:
                return 0
            raise OSError("process_snapshot_first_failed")
        enumerated = 0
        matching = 0
        while True:
            enumerated += 1
            if enumerated > _MAX_ENUMERATED_PROCESSES:
                raise OSError("process_snapshot_overflow")
            name = entry.szExeFile
            if not isinstance(name, str):
                raise OSError("process_snapshot_name_invalid")
            if name.casefold() == "wow.exe":
                matching += 1
                if matching > _MAX_MATCHING_PROCESSES:
                    raise OSError("process_snapshot_match_overflow")
            ctypes.set_last_error(0)
            if not library.Process32NextW(snapshot, ctypes.byref(entry)):
                if ctypes.get_last_error() != _ERROR_NO_MORE_FILES:
                    raise OSError("process_snapshot_next_failed")
                break
        return matching
    finally:
        if not library.CloseHandle(snapshot):
            raise OSError("process_snapshot_close_failed")


def probe_wow_process_state() -> WoWProcessState:
    """Return only a sanitized state and count; every uncertainty is unknown."""
    if os.name != "nt":
        return WoWProcessState("unknown", 0)
    try:
        matching = _windows_matching_process_count()
    except (OSError, ValueError, TypeError, AttributeError):
        return WoWProcessState("unknown", 0)
    if (
        isinstance(matching, bool)
        or not isinstance(matching, int)
        or not 0 <= matching <= _MAX_MATCHING_PROCESSES
    ):
        return WoWProcessState("unknown", 0)
    if matching:
        return WoWProcessState("running", matching)
    return WoWProcessState("stopped", 0)
