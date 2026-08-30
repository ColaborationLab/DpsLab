from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path
import unittest
from unittest.mock import patch

from dpslab.wow_process_state import (
    WoWProcessState,
    _windows_matching_process_count,
    probe_wow_process_state,
)


class _FakeKernel32:
    def __init__(self, names: list[str], *, first_error: bool = False) -> None:
        self.names = names
        self.index = 0
        self.first_error = first_error
        self.closed = False

    def CreateToolhelp32Snapshot(self, flags, process_id):
        return 123

    def Process32FirstW(self, snapshot, entry_pointer):
        if self.first_error or not self.names:
            return 0
        entry_pointer._obj.szExeFile = self.names[0]
        return 1

    def Process32NextW(self, snapshot, entry_pointer):
        self.index += 1
        if self.index >= len(self.names):
            return 0
        entry_pointer._obj.szExeFile = self.names[self.index]
        return 1

    def CloseHandle(self, snapshot):
        self.closed = True
        return 1


class WoWProcessStateTests(unittest.TestCase):
    def test_zero_and_positive_counts_map_to_stopped_and_running(self) -> None:
        with patch("dpslab.wow_process_state.os.name", "nt"):
            with patch("dpslab.wow_process_state._windows_matching_process_count", return_value=0):
                self.assertEqual(WoWProcessState("stopped", 0), probe_wow_process_state())
            with patch("dpslab.wow_process_state._windows_matching_process_count", return_value=2):
                self.assertEqual(WoWProcessState("running", 2), probe_wow_process_state())

    def test_unsupported_platform_and_native_failure_are_unknown(self) -> None:
        with patch("dpslab.wow_process_state.os.name", "posix"):
            with patch("dpslab.wow_process_state._windows_matching_process_count") as provider:
                self.assertEqual(WoWProcessState("unknown", 0), probe_wow_process_state())
                provider.assert_not_called()
        with patch("dpslab.wow_process_state.os.name", "nt"):
            with patch("dpslab.wow_process_state._windows_matching_process_count", side_effect=OSError):
                self.assertEqual(WoWProcessState("unknown", 0), probe_wow_process_state())

    def test_malformed_or_excessive_counts_are_unknown(self) -> None:
        with patch("dpslab.wow_process_state.os.name", "nt"):
            for value in (-1, 17, True, None, "1"):
                with self.subTest(value=value):
                    with patch("dpslab.wow_process_state._windows_matching_process_count", return_value=value):
                        self.assertEqual(WoWProcessState("unknown", 0), probe_wow_process_state())

    def test_result_is_immutable_and_contains_no_process_identity(self) -> None:
        result = WoWProcessState("running", 1)
        self.assertEqual({"state", "matching_process_count"}, set(result.__dataclass_fields__))
        with self.assertRaises(FrozenInstanceError):
            result.state = "stopped"  # type: ignore[misc]

    def test_native_enumeration_matches_only_exact_wow_name_and_closes_handle(self) -> None:
        kernel = _FakeKernel32(["Battle.net.exe", "WowVoiceProxy.exe", "WOW.EXE", "WowT.exe"])
        with patch("dpslab.wow_process_state._kernel32", return_value=kernel):
            with patch("dpslab.wow_process_state.ctypes.set_last_error"):
                with patch("dpslab.wow_process_state.ctypes.get_last_error", return_value=18):
                    self.assertEqual(1, _windows_matching_process_count())
        self.assertTrue(kernel.closed)

    def test_native_enumeration_failure_still_closes_handle(self) -> None:
        kernel = _FakeKernel32([], first_error=True)
        with patch("dpslab.wow_process_state._kernel32", return_value=kernel):
            with patch("dpslab.wow_process_state.ctypes.set_last_error"):
                with patch("dpslab.wow_process_state.ctypes.get_last_error", return_value=5):
                    with self.assertRaisesRegex(OSError, "process_snapshot_first_failed"):
                        _windows_matching_process_count()
        self.assertTrue(kernel.closed)

    def test_source_has_native_read_only_surface_and_no_process_launcher(self) -> None:
        source = (Path(__file__).parents[1] / "src" / "dpslab" / "wow_process_state.py").read_text(encoding="utf-8")
        for token in ("CreateToolhelp32Snapshot", "Process32FirstW", "Process32NextW", "CloseHandle"):
            self.assertIn(token, source)
        for forbidden in ("subprocess", "tasklist", "psutil", "TerminateProcess", "OpenProcess", "PowerShell", "registry", "winreg"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
