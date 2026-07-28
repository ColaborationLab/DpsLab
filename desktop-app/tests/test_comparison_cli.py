from __future__ import annotations

import io
import json
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from dpslab.__main__ import _arguments, main
from dpslab.comparison_readiness import ComparisonReadinessError
from dpslab.comparison_execution import ComparisonExecutionError


class ComparisonReadinessCliTests(unittest.TestCase):
    def _objects(self):
        protocol = SimpleNamespace(
            timeout_seconds=91.0,
            threads=3,
            iterations_per_run=5000,
        )
        spec = SimpleNamespace(
            comparison_id="flasil_neck_50228_vs_249368_v1",
            scenario=Path("scenario.toml"),
            protocol=protocol,
        )
        scenario = SimpleNamespace(
            scenario=SimpleNamespace(
                max_time=300,
                vary_combat_length=0.2,
                fight_style="LightMovement",
                desired_targets=1,
            )
        )
        config = object()
        software = object()
        preflight = SimpleNamespace(
            base_profile_sha256="a" * 64,
            comparison_id=spec.comparison_id,
            comparison_spec_sha256="b" * 64,
            evidence_manifest_sha256="c" * 64,
            runs_dir="results/runs",
            scenario_sha256="d" * 64,
        )
        readiness = SimpleNamespace(
            executable_source="explicit_cli",
            portable_probe_argv=("<SIMC_EXE>", "display_build=2"),
            preflight=preflight,
            ready=True,
            simulationcraft_branch="midnight",
        )
        return spec, scenario, config, software, readiness

    def test_arguments_have_frozen_defaults(self) -> None:
        args = _arguments(["comparison-ready"])
        self.assertEqual(args.command, "comparison-ready")
        self.assertEqual(
            args.comparison.name,
            "flasil_neck_50228_vs_249368_v1.toml",
        )
        self.assertIsNone(args.simc_exe)
        self.assertEqual(args.probe_timeout, 30.0)

    def test_execution_arguments_require_explicit_confirmation(self) -> None:
        args = _arguments(
            [
                "comparison-execute",
                "--simc-exe",
                "C:/private/simc.exe",
                "--confirm-comparison-id",
                "flasil_neck_50228_vs_249368_v1",
            ]
        )
        self.assertEqual(args.command, "comparison-execute")
        self.assertEqual(args.probe_timeout, 30.0)
        self.assertEqual(
            args.confirm_comparison_id,
            "flasil_neck_50228_vs_249368_v1",
        )

    @patch("subprocess.Popen", side_effect=AssertionError("process_forbidden"))
    @patch("dpslab.__main__.assess_comparison_readiness")
    @patch("dpslab.__main__.software_record")
    @patch("dpslab.__main__.resolve_simulation_config")
    @patch("dpslab.__main__.load_scenario")
    @patch("dpslab.__main__.load_comparison_spec")
    def test_command_composes_boundaries_and_emits_portable_json(
        self,
        load_spec: Mock,
        load_scenario: Mock,
        resolve_config: Mock,
        capture_software: Mock,
        assess: Mock,
        process: Mock,
    ) -> None:
        spec, scenario, config, software, readiness = self._objects()
        load_spec.return_value = spec
        load_scenario.return_value = scenario
        resolve_config.return_value = config
        capture_software.return_value = software
        assess.return_value = readiness
        private_executable = Path("C:/Users/private/simc.exe")
        stdout = io.StringIO()

        with patch("sys.stdout", stdout):
            result = main(
                [
                    "comparison-ready",
                    "--simc-exe",
                    str(private_executable),
                    "--probe-timeout",
                    "60",
                ]
            )

        self.assertEqual(result, 0)
        root = load_spec.call_args.kwargs["root"]
        load_scenario.assert_called_once_with(spec.scenario)
        resolve_config.assert_called_once_with(
            explicit_simc_exe=private_executable,
            root=root,
            timeout_seconds=91.0,
            generate_html=False,
            runs_dir=root / "results" / "runs",
            threads=3,
            iterations=5000,
            max_time=300,
            vary_combat_length=0.2,
            fight_style="LightMovement",
            desired_targets=1,
            target_error=None,
            scenario=scenario,
            variant=None,
            seed=None,
        )
        capture_software.assert_called_once_with(root)
        assess.assert_called_once_with(
            spec,
            config,
            software,
            root=root,
            probe_timeout_seconds=60.0,
        )
        payload = json.loads(stdout.getvalue())
        self.assertTrue(payload["ready"])
        self.assertEqual(payload["runs_dir"], "results/runs")
        self.assertEqual(
            payload["portable_probe_argv"],
            ["<SIMC_EXE>", "display_build=2"],
        )
        self.assertNotIn(str(private_executable), stdout.getvalue())
        process.assert_not_called()

    @patch("dpslab.__main__._comparison_ready")
    def test_dependency_failure_uses_cli_error_channel(
        self, command: Mock
    ) -> None:
        command.side_effect = ComparisonReadinessError(
            "comparison_preflight_failed"
        )
        stderr = io.StringIO()
        with patch("sys.stderr", stderr):
            result = main(["comparison-ready"])
        self.assertEqual(result, 1)
        self.assertEqual(
            stderr.getvalue(),
            "error: comparison_preflight_failed\n",
        )

    @patch("dpslab.__main__.load_comparison_spec")
    def test_invalid_probe_timeout_fails_before_dependencies(
        self, load_spec: Mock
    ) -> None:
        for value in ("0", "-1", "nan", "inf", "-inf", "60.0001", "61"):
            with self.subTest(value=value):
                stderr = io.StringIO()
                with patch("sys.stderr", stderr):
                    result = main(
                        [
                            "comparison-ready",
                            f"--probe-timeout={value}",
                        ]
                    )
                self.assertEqual(result, 1)
                self.assertEqual(
                    stderr.getvalue(), "error: probe_timeout_invalid\n"
                )
        load_spec.assert_not_called()

    @patch("dpslab.__main__.load_comparison_spec")
    def test_setup_failure_is_sanitized(
        self, load_spec: Mock
    ) -> None:
        private_path = "C:/Users/private/comparison.toml"
        load_spec.side_effect = OSError(2, "missing", private_path)
        stderr = io.StringIO()
        with patch("sys.stderr", stderr):
            result = main(
                ["comparison-ready", "--comparison", private_path]
            )
        self.assertEqual(result, 1)
        self.assertEqual(
            stderr.getvalue(),
            "error: comparison_readiness_setup_failed\n",
        )
        self.assertNotIn(private_path, stderr.getvalue())

    @patch("dpslab.__main__._comparison_execute")
    def test_execution_error_channel_is_static_and_sanitized(
        self, command: Mock
    ) -> None:
        command.side_effect = ComparisonExecutionError(
            "comparison_execution_setup_failed"
        )
        private_path = "C:/Users/private/simc.exe"
        stderr = io.StringIO()
        with patch("sys.stderr", stderr):
            result = main(
                [
                    "comparison-execute",
                    "--simc-exe",
                    private_path,
                    "--confirm-comparison-id",
                    "flasil_neck_50228_vs_249368_v1",
                ]
            )
        self.assertEqual(result, 1)
        self.assertEqual(
            stderr.getvalue(),
            "error: comparison_execution_setup_failed\n",
        )
        self.assertNotIn(private_path, stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
