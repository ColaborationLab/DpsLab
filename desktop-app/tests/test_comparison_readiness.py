from __future__ import annotations

import tempfile
import unittest
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from unittest.mock import Mock, patch

from tests.strict_temporary_cleanup import strict_temporary_cleanup

from dpslab.comparison_models import (
    ComparisonSoftware,
    DpsLabSourceIdentity,
    PlatformIdentity,
    PythonIdentity,
    ScipyIdentity,
    SimulationCraftIdentity,
)
from dpslab.comparison_preflight import ComparisonExecutionPreflight
from dpslab.comparison_readiness import (
    ComparisonReadinessError,
    assess_comparison_readiness,
)
from dpslab.comparison_spec import load_comparison_spec
from dpslab.config import SimulationConfig
from dpslab.scenario import load_scenario
from dpslab.simc_identity import SimulationCraftIdentityProbe


ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "comparisons" / "flasil_neck_50228_vs_249368_v1.toml"


class ComparisonReadinessTests(unittest.TestCase):
    class _FalseyCallable:
        def __init__(self, value: object) -> None:
            self.value = value
            self.calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

        def __bool__(self) -> bool:
            return False

        def __call__(self, *args: object, **kwargs: object) -> object:
            self.calls.append((args, kwargs))
            return self.value

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(strict_temporary_cleanup, self.temp, Path(self.temp.name))
        self.exe = Path(self.temp.name) / "simc.exe"
        self.exe.write_bytes(b"controlled-simc-binary")
        self.spec = load_comparison_spec(SPEC, root=ROOT)
        scenario = load_scenario(self.spec.scenario)
        values = scenario.scenario
        self.config = SimulationConfig(
            simc_exe=self.exe,
            runs_dir=ROOT / "results" / "runs",
            timeout_seconds=self.spec.protocol.timeout_seconds,
            threads=self.spec.protocol.threads,
            iterations=self.spec.protocol.iterations_per_run,
            max_time=values.max_time,
            vary_combat_length=values.vary_combat_length,
            fight_style=values.fight_style,
            desired_targets=values.desired_targets,
            target_error=None,
            scenario=scenario,
            seed=None,
            executable_source="explicit_cli",
        )
        self.identity = SimulationCraftIdentity(
            self.spec.simc_version,
            self.spec.simc_revision,
            sha256(self.exe.read_bytes()).hexdigest(),
        )
        self.probe = SimulationCraftIdentityProbe(
            self.identity,
            "midnight",
            "explicit_cli",
        )
        self.software = ComparisonSoftware(
            PythonIdentity("3.13.14", "CPython"),
            DpsLabSourceIdentity(
                "git_commit", "0.1.0", "a" * 40, False, None
            ),
            ScipyIdentity(">=1.11.0,<2.0.0", "1.16.3"),
            PlatformIdentity("Windows", "11", "AMD64", "win32"),
            SimulationCraftIdentity(None, None, None),
        )
        self.report = ComparisonExecutionPreflight(
            self.spec.comparison_id,
            self.spec.source_sha256,
            self.spec.base_profile_sha256,
            self.spec.scenario_sha256,
            self.spec.evidence_sha256,
            "results/runs",
            replace(self.software, simulationcraft=self.identity),
        )

    def _assess(
        self,
        *,
        probe: object | None = None,
        preflight: object | None = None,
        timeout: float = 17.0,
    ):
        identity_boundary = Mock(return_value=self.probe)
        preflight_boundary = Mock(return_value=self.report)
        if probe is not None:
            identity_boundary = probe
        if preflight is not None:
            preflight_boundary = preflight
        result = assess_comparison_readiness(
            self.spec,
            self.config,
            self.software,
            root=ROOT,
            probe_timeout_seconds=timeout,
            identity_probe=identity_boundary,
            preflight=preflight_boundary,
        )
        return result, identity_boundary, preflight_boundary

    @patch(
        "dpslab.comparison_readiness.preflight_comparison_execution"
    )
    @patch(
        "dpslab.comparison_readiness.capture_simulationcraft_identity"
    )
    def test_default_boundaries_compose_exactly_without_run_artifacts(
        self,
        identity_boundary: Mock,
        preflight_boundary: Mock,
    ) -> None:
        before = set((ROOT / "results" / "runs").glob("*"))
        identity_boundary.return_value = self.probe
        preflight_boundary.return_value = self.report

        result = assess_comparison_readiness(
            self.spec,
            self.config,
            self.software,
            root=ROOT,
            probe_timeout_seconds=17,
        )

        self.assertTrue(result.ready)
        self.assertEqual(result.simulationcraft_branch, "midnight")
        self.assertEqual(
            result.portable_probe_argv,
            ("<SIMC_EXE>", "display_build=2"),
        )
        identity_boundary.assert_called_once_with(
            self.config, timeout_seconds=17
        )
        preflight_boundary.assert_called_once_with(
            self.spec,
            self.config,
            self.identity,
            self.software,
            root=ROOT,
        )
        self.assertEqual(
            before, set((ROOT / "results" / "runs").glob("*"))
        )

    def test_probe_contract_matrix_fails_closed(self) -> None:
        cases = (
            object(),
            replace(self.probe, identity=object()),
            replace(self.probe, branch=None),
            replace(
                self.probe,
                identity=replace(self.identity, version=object()),
            ),
            replace(
                self.probe,
                identity=replace(self.identity, revision=object()),
            ),
            replace(
                self.probe,
                identity=replace(
                    self.identity, executable_sha256=object()
                ),
            ),
            replace(self.probe, isolated=False),
            replace(self.probe, portable_argv=("<SIMC_EXE>", "--other")),
            replace(self.probe, executable_source="environment"),
            replace(self.probe, branch=""),
            replace(
                self.probe,
                identity=replace(self.identity, revision=None),
            ),
            replace(
                self.probe,
                identity=replace(
                    self.identity, executable_sha256="0" * 63
                ),
            ),
        )
        for candidate in cases:
            with self.subTest(candidate=candidate):
                boundary = Mock(return_value=candidate)
                with self.assertRaisesRegex(
                    ComparisonReadinessError,
                    "identity_probe_contract_invalid",
                ):
                    self._assess(probe=boundary)

    def test_identity_dependency_failures_are_sanitized(self) -> None:
        personal = str(Path(self.temp.name) / "private" / "simc.exe")
        for failure in (RuntimeError(personal), OSError(2, "missing", personal)):
            with self.subTest(failure=type(failure).__name__):
                boundary = Mock(side_effect=failure)
                with self.assertRaisesRegex(
                    ComparisonReadinessError, "identity_probe_failed"
                ) as raised:
                    self._assess(probe=boundary)
                self.assertIsNone(raised.exception.__cause__)
                self.assertIsNone(raised.exception.__context__)
                self.assertNotIn(personal, repr(raised.exception))

    def test_preflight_dependency_failures_are_sanitized(self) -> None:
        personal = str(Path(self.temp.name) / "private" / "result.json")
        boundary = Mock(side_effect=RuntimeError(personal))
        with self.assertRaisesRegex(
            ComparisonReadinessError, "comparison_preflight_failed"
        ) as raised:
            self._assess(preflight=boundary)
        self.assertIsNone(raised.exception.__cause__)
        self.assertIsNone(raised.exception.__context__)
        self.assertNotIn(personal, repr(raised.exception))

    def test_preflight_contract_matrix_fails_closed(self) -> None:
        cases = (
            object(),
            replace(self.report, ready=False),
            replace(self.report, comparison_id="other"),
            replace(self.report, comparison_spec_sha256="0" * 64),
            replace(self.report, base_profile_sha256="0" * 64),
            replace(self.report, scenario_sha256="0" * 64),
            replace(self.report, evidence_manifest_sha256="0" * 64),
            replace(self.report, runs_dir="other"),
            replace(
                self.report,
                software=replace(
                    self.report.software,
                    python=PythonIdentity("3.12.13", "CPython"),
                ),
            ),
            replace(
                self.report,
                software=replace(
                    self.report.software,
                    simulationcraft=replace(
                        self.identity, revision="0123456"
                    ),
                ),
            ),
        )
        for candidate in cases:
            with self.subTest(candidate=candidate):
                boundary = Mock(return_value=candidate)
                with self.assertRaisesRegex(
                    ComparisonReadinessError,
                    "comparison_preflight_contract_invalid",
                ):
                    self._assess(preflight=boundary)

    @patch(
        "dpslab.comparison_readiness.preflight_comparison_execution",
        side_effect=AssertionError("real_preflight_selected"),
    )
    @patch(
        "dpslab.comparison_readiness.capture_simulationcraft_identity",
        side_effect=AssertionError("real_probe_selected"),
    )
    def test_falsey_injected_boundaries_remain_authoritative(
        self,
        real_probe: Mock,
        real_preflight: Mock,
    ) -> None:
        probe = self._FalseyCallable(self.probe)
        preflight = self._FalseyCallable(self.report)
        result = assess_comparison_readiness(
            self.spec,
            self.config,
            self.software,
            root=ROOT,
            identity_probe=probe,
            preflight=preflight,
        )
        self.assertTrue(result.ready)
        self.assertEqual(len(probe.calls), 1)
        self.assertEqual(len(preflight.calls), 1)
        real_probe.assert_not_called()
        real_preflight.assert_not_called()

    @patch("subprocess.Popen", side_effect=AssertionError("process_forbidden"))
    def test_injected_route_never_starts_a_process(
        self, process: Mock
    ) -> None:
        result, identity_boundary, preflight_boundary = self._assess()
        self.assertTrue(result.ready)
        self.assertEqual(result.preflight, self.report)
        identity_boundary.assert_called_once()
        preflight_boundary.assert_called_once()
        process.assert_not_called()


if __name__ == "__main__":
    unittest.main()
