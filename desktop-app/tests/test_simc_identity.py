from __future__ import annotations

import os
import io
import subprocess
import tempfile
import unittest
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch

from dpslab.config import SimulationConfig
from dpslab.simc_identity import (
    SimulationCraftIdentityProbeError,
    capture_simulationcraft_identity,
)


ROOT = Path(__file__).resolve().parents[2]
BUILD_OUTPUT = (
    "SimulationCraft 1205-01 for World of Warcraft 12.0.7 Live "
    "(hotfix 2026-07-13/68453, git build midnight a81c39d)\n"
)


class SimulationCraftIdentityProbeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.exe = Path(self.temp.name) / "simc.exe"
        self.exe.write_bytes(b"controlled-simulationcraft-binary")
        self.config = SimulationConfig(
            simc_exe=self.exe,
            runs_dir=ROOT / "results" / "runs",
            executable_source="explicit_cli",
        )

    class _Process:
        def __init__(
            self,
            *,
            stdout: str = BUILD_OUTPUT,
            stderr: str = "",
            returncode: int = 0,
            running: bool = False,
            resists_stop: bool = False,
        ) -> None:
            self.stdout = io.BytesIO(stdout.encode("utf-8"))
            self.stderr = io.BytesIO(stderr.encode("utf-8"))
            self.returncode = None if running else returncode
            self._final_returncode = returncode
            self.resists_stop = resists_stop
            self.terminated = False
            self.killed = False

        def wait(self, timeout: float | None = None) -> int:
            if self.returncode is None:
                raise subprocess.TimeoutExpired("simc.exe", timeout)
            return self.returncode

        def terminate(self) -> None:
            self.terminated = True
            if not self.resists_stop:
                self.returncode = -15

        def kill(self) -> None:
            self.killed = True
            if not self.resists_stop:
                self.returncode = -9

    @patch("dpslab.simc_identity.subprocess.Popen")
    def test_complete_identity_is_captured_without_run_artifacts(
        self, process: object
    ) -> None:
        before = set((ROOT / "results" / "runs").glob("*"))
        process.return_value = self._Process()

        probe = capture_simulationcraft_identity(self.config)

        self.assertEqual(probe.identity.version, "1205-01")
        self.assertEqual(probe.identity.revision, "a81c39d")
        self.assertEqual(
            probe.identity.executable_sha256,
            sha256(self.exe.read_bytes()).hexdigest(),
        )
        self.assertEqual(probe.branch, "midnight")
        self.assertEqual(probe.executable_source, "explicit_cli")
        self.assertEqual(
            probe.portable_argv, ("<SIMC_EXE>", "display_build=2")
        )
        self.assertTrue(probe.isolated)
        self.assertEqual(before, set((ROOT / "results" / "runs").glob("*")))

    @patch("dpslab.simc_identity.subprocess.Popen")
    def test_process_boundary_is_closed_and_environment_isolated(
        self, process: object
    ) -> None:
        process.return_value = self._Process()
        with patch.dict(
            os.environ,
            {
                "DPSLAB_TEST_SECRET": "must-not-cross-boundary",
                "HOME": "personal-home",
                "USERPROFILE": "personal-profile",
            },
            clear=False,
        ):
            capture_simulationcraft_identity(
                self.config, timeout_seconds=12
            )

        args, kwargs = process.call_args
        self.assertEqual(
            args[0], [str(self.exe.resolve()), "display_build=2"]
        )
        self.assertEqual(kwargs["cwd"], Path(kwargs["env"]["TEMP"]))
        self.assertEqual(kwargs["env"]["TEMP"], kwargs["env"]["TMP"])
        self.assertEqual(
            kwargs["env"]["HOME"], kwargs["env"]["USERPROFILE"]
        )
        self.assertNotIn("DPSLAB_TEST_SECRET", kwargs["env"])
        self.assertEqual(kwargs["stdin"], subprocess.DEVNULL)
        self.assertEqual(kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(kwargs["stderr"], subprocess.PIPE)
        self.assertFalse(kwargs["shell"])
        self.assertFalse(Path(kwargs["cwd"]).exists())

    @patch("dpslab.simc_identity.subprocess.Popen")
    def test_identity_may_be_reported_on_stderr(
        self, process: object
    ) -> None:
        process.return_value = self._Process(
            stdout="", stderr=BUILD_OUTPUT
        )
        probe = capture_simulationcraft_identity(self.config)
        self.assertEqual(
            (probe.identity.version, probe.identity.revision),
            ("1205-01", "a81c39d"),
        )

    @patch("dpslab.simc_identity.subprocess.Popen")
    def test_missing_or_ambiguous_identity_fails_closed(
        self, process: object
    ) -> None:
        cases = {
            "version": "(git build midnight a81c39d)\n",
            "revision": "SimulationCraft 1205-01\n",
            "split_line": (
                "SimulationCraft 1205-01\n"
                "details (git build midnight a81c39d)\n"
            ),
            "ambiguous_version": BUILD_OUTPUT + BUILD_OUTPUT.replace(
                "1205-01", "1205-02"
            ),
            "ambiguous_revision": BUILD_OUTPUT + BUILD_OUTPUT.replace(
                "a81c39d", "b81c39d"
            ),
            "two_identities_same_line": BUILD_OUTPUT.rstrip()
            + " (git build ptr 0123456)\n",
            "malformed_then_valid_same_line": BUILD_OUTPUT.replace(
                "git build", "git build ??? git build"
            ),
        }
        for label, output in cases.items():
            with self.subTest(label=label):
                process.return_value = self._Process(stdout=output)
                with self.assertRaises(
                    SimulationCraftIdentityProbeError
                ):
                    capture_simulationcraft_identity(self.config)

    @patch("dpslab.simc_identity.subprocess.Popen")
    def test_nonzero_exit_fails_closed(self, process: object) -> None:
        process.return_value = self._Process(returncode=2)
        with self.assertRaisesRegex(
            SimulationCraftIdentityProbeError, "nonzero_exit"
        ):
            capture_simulationcraft_identity(self.config)

    @patch("dpslab.simc_identity.subprocess.Popen")
    def test_timeout_fails_closed(self, process: object) -> None:
        fake = self._Process(stdout="", running=True)
        process.return_value = fake
        with self.assertRaisesRegex(
            SimulationCraftIdentityProbeError, "probe_timeout"
        ) as raised:
            capture_simulationcraft_identity(
                self.config, timeout_seconds=0.01
            )
        self.assertTrue(fake.terminated)
        self.assertIsNone(raised.exception.__cause__)
        self.assertIsNone(raised.exception.__context__)

    @patch("dpslab.simc_identity.subprocess.Popen")
    def test_process_that_resists_termination_fails_closed(
        self, process: object
    ) -> None:
        fake = self._Process(
            stdout="",
            running=True,
            resists_stop=True,
        )
        process.return_value = fake
        with self.assertRaisesRegex(
            SimulationCraftIdentityProbeError, "capture_failed"
        ) as raised:
            capture_simulationcraft_identity(
                self.config, timeout_seconds=0.01
            )
        self.assertTrue(fake.terminated)
        self.assertTrue(fake.killed)
        self.assertIsNone(raised.exception.__cause__)
        self.assertIsNone(raised.exception.__context__)

    @patch("dpslab.simc_identity.subprocess.Popen")
    def test_executable_mutation_is_rejected(
        self, process: object
    ) -> None:
        def mutate(args: list[str], **kwargs: object) -> object:
            self.exe.write_bytes(b"changed-during-probe")
            return self._Process()

        process.side_effect = mutate
        with self.assertRaisesRegex(
            SimulationCraftIdentityProbeError, "changed_during_probe"
        ):
            capture_simulationcraft_identity(self.config)

    @patch("dpslab.simc_identity.subprocess.Popen")
    def test_invalid_inputs_fail_before_process(
        self, process: object
    ) -> None:
        missing = SimulationConfig(
            simc_exe=Path(self.temp.name) / "missing.exe",
            runs_dir=self.config.runs_dir,
            executable_source="explicit_cli",
        )
        invalid_source = SimulationConfig(
            simc_exe=self.exe,
            runs_dir=self.config.runs_dir,
            executable_source="untrusted",
        )
        relative = SimulationConfig(
            simc_exe=Path("relative/simc.exe"),
            runs_dir=self.config.runs_dir,
            executable_source="explicit_cli",
        )
        cases = (
            (missing, 30),
            (invalid_source, 30),
            (relative, 30),
            (self.config, 0),
            (self.config, 61),
            (self.config, float("nan")),
            (self.config, True),
        )
        for config, timeout in cases:
            with self.subTest(config=config, timeout=timeout):
                with self.assertRaises(
                    SimulationCraftIdentityProbeError
                ):
                    capture_simulationcraft_identity(
                        config, timeout_seconds=timeout
                    )
        process.assert_not_called()

    @patch("dpslab.simc_identity.subprocess.Popen")
    def test_excessive_output_is_rejected(self, process: object) -> None:
        fake = self._Process(
            stdout=BUILD_OUTPUT + ("x" * (64 * 1024)),
            running=True,
        )
        process.return_value = fake
        with self.assertRaisesRegex(
            SimulationCraftIdentityProbeError, "output_too_large"
        ):
            capture_simulationcraft_identity(self.config)
        self.assertTrue(fake.terminated)

        personal = str(Path(self.temp.name) / "private" / "simc.exe")
        process.side_effect = OSError(2, "missing", personal)
        process.return_value = None
        with self.assertRaisesRegex(
            SimulationCraftIdentityProbeError, "start_failed"
        ) as raised:
            capture_simulationcraft_identity(self.config)
        self.assertIsNone(raised.exception.__cause__)
        self.assertIsNone(raised.exception.__context__)
        self.assertNotIn(personal, repr(raised.exception))


if __name__ == "__main__":
    unittest.main()
