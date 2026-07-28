from __future__ import annotations

import tempfile
import unittest
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch

from dpslab.comparison_environment import (
    source_tree_inventory,
    source_tree_sha256,
)
from dpslab.comparison_models import (
    ComparisonSoftware,
    DpsLabSourceIdentity,
    PlatformIdentity,
    PythonIdentity,
    ScipyIdentity,
    SimulationCraftIdentity,
)
from dpslab.comparison_preflight import (
    ComparisonExecutionPreflightError,
    preflight_comparison_execution,
)
from dpslab.comparison_spec import load_comparison_spec
from dpslab.config import SimulationConfig
from dpslab.scenario import load_scenario


ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "comparisons" / "flasil_neck_50228_vs_249368_v1.toml"


class ComparisonExecutionPreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.exe = Path(self.temp.name) / "simc.exe"
        self.exe.write_bytes(b"controlled-simc-binary")
        self.spec = load_comparison_spec(SPEC, root=ROOT)
        self.scenario = load_scenario(self.spec.scenario)
        scenario = self.scenario.scenario
        self.config = SimulationConfig(
            simc_exe=self.exe,
            runs_dir=ROOT / "results" / "runs",
            timeout_seconds=self.spec.protocol.timeout_seconds,
            threads=self.spec.protocol.threads,
            iterations=self.spec.protocol.iterations_per_run,
            max_time=scenario.max_time,
            vary_combat_length=scenario.vary_combat_length,
            fight_style=scenario.fight_style,
            desired_targets=scenario.desired_targets,
            target_error=None,
            scenario=self.scenario,
            seed=None,
            executable_source="explicit_cli",
        )
        self.identity = SimulationCraftIdentity(
            self.spec.simc_version,
            self.spec.simc_revision,
            sha256(self.exe.read_bytes()).hexdigest(),
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

    def _preflight(
        self,
        *,
        config: SimulationConfig | None = None,
        identity: SimulationCraftIdentity | None = None,
        software: ComparisonSoftware | None = None,
    ):
        return preflight_comparison_execution(
            self.spec,
            config or self.config,
            identity or self.identity,
            software or self.software,
            root=ROOT,
        )

    def test_ready_snapshot_is_pure_and_complete(self) -> None:
        before = set((ROOT / "results" / "runs").glob("*"))
        report = self._preflight()
        after = set((ROOT / "results" / "runs").glob("*"))
        self.assertTrue(report.ready)
        self.assertEqual(report.comparison_id, self.spec.comparison_id)
        self.assertEqual(report.runs_dir, "results/runs")
        self.assertEqual(report.software.simulationcraft, self.identity)
        self.assertEqual(before, after)

    def test_execution_configuration_matrix_fails_closed(self) -> None:
        cases = {
            "iterations": replace(self.config, iterations=4999),
            "threads": replace(self.config, threads=1),
            "timeout": replace(self.config, timeout_seconds=899),
            "target_error": replace(self.config, target_error=0.1),
            "seed": replace(self.config, seed=self.spec.protocol.seeds[0]),
            "runs_dir": replace(self.config, runs_dir=Path(self.temp.name) / "runs"),
            "variant": replace(self.config, variant=object()),
            "source": replace(self.config, executable_source="test"),
        }
        for label, config in cases.items():
            with self.subTest(label=label):
                with self.assertRaises(ComparisonExecutionPreflightError):
                    self._preflight(config=config)

    def test_scenario_and_simulationcraft_identity_fail_closed(self) -> None:
        with self.assertRaisesRegex(
            ComparisonExecutionPreflightError, "scenario_identity_mismatch"
        ):
            self._preflight(config=replace(self.config, scenario=None))
        identities = (
            replace(self.identity, version="other"),
            replace(self.identity, revision="other"),
            replace(self.identity, executable_sha256="0" * 64),
            SimulationCraftIdentity(None, None, None),
        )
        for identity in identities:
            with self.subTest(identity=identity):
                with self.assertRaisesRegex(
                    ComparisonExecutionPreflightError,
                    "simulationcraft_identity_mismatch",
                ):
                    self._preflight(identity=identity)

    def test_assets_are_rehashed_at_the_preflight_boundary(self) -> None:
        changed = Path(self.temp.name) / "changed.simc"
        changed.write_bytes(b"changed")
        with self.assertRaisesRegex(
            ComparisonExecutionPreflightError, "base_profile_hash_mismatch"
        ):
            preflight_comparison_execution(
                replace(self.spec, base_profile=changed),
                self.config,
                self.identity,
                self.software,
                root=ROOT,
            )

    @patch("subprocess.run", side_effect=AssertionError("subprocess_not_allowed"))
    def test_normal_preflight_route_starts_no_process(
        self, process: object
    ) -> None:
        self.assertTrue(self._preflight().ready)
        process.assert_not_called()

    def test_semantically_altered_spec_with_valid_bytes_is_rejected(self) -> None:
        altered = replace(
            self.spec,
            status="draft",
            protocol=replace(self.spec.protocol, threads=1),
        )
        with self.assertRaisesRegex(
            ComparisonExecutionPreflightError,
            "comparison_spec_semantic_mismatch",
        ):
            preflight_comparison_execution(
                altered,
                self.config,
                self.identity,
                self.software,
                root=ROOT,
            )

    def test_semantically_altered_scenario_and_precision_are_rejected(self) -> None:
        scenario = self.scenario.scenario
        cases = (
            replace(
                self.scenario,
                scenario=replace(scenario, fight_style="Other"),
            ),
            replace(
                self.scenario,
                scenario=replace(
                    scenario,
                    precision=replace(
                        scenario.precision, iterations=4999
                    ),
                ),
            ),
        )
        for altered in cases:
            with self.subTest(altered=altered):
                config = replace(self.config, scenario=altered)
                with self.assertRaisesRegex(
                    ComparisonExecutionPreflightError,
                    "scenario_semantic_mismatch",
                ):
                    self._preflight(config=config)

    def test_runtime_and_source_identity_matrix_fails_closed(self) -> None:
        cases = (
            replace(
                self.software,
                python=PythonIdentity("3.10.14", "CPython"),
            ),
            replace(
                self.software,
                scipy=ScipyIdentity(">=1.11.0,<2.0.0", "2.0.0"),
            ),
            replace(
                self.software,
                dpslab=replace(self.software.dpslab, dirty_state=True),
            ),
            replace(
                self.software,
                dpslab=DpsLabSourceIdentity(
                    "dpslab_source_tree_sha256_v1",
                    "0.1.0",
                    None,
                    None,
                    "b" * 64,
                    "sorted_portable_paths_v1",
                    (),
                ),
            ),
        )
        for software in cases:
            with self.subTest(software=software):
                with self.assertRaises(ComparisonExecutionPreflightError):
                    self._preflight(software=software)

    def test_source_tree_identity_is_canonical_and_recomputed(self) -> None:
        source = ROOT / "desktop-app" / "src" / "dpslab"
        valid = DpsLabSourceIdentity(
            "dpslab_source_tree_sha256_v1",
            "0.1.0",
            None,
            None,
            source_tree_sha256(source),
            "sorted_portable_paths_v1",
            source_tree_inventory(source),
        )
        self.assertTrue(
            self._preflight(
                software=replace(self.software, dpslab=valid)
            ).ready
        )
        cases = (
            replace(valid, commit="a" * 40),
            replace(valid, dirty_state=False),
            replace(valid, source_tree_sha256="0" * 64),
            replace(valid, source_inventory_method="other"),
            replace(valid, source_inventory=tuple(reversed(valid.source_inventory))),
            replace(valid, source_inventory=("../escape.py",)),
        )
        for identity in cases:
            with self.subTest(identity=identity):
                with self.assertRaisesRegex(
                    ComparisonExecutionPreflightError,
                    "dpslab_source_identity_invalid",
                ):
                    self._preflight(
                        software=replace(self.software, dpslab=identity)
                    )

    def test_runtime_versions_reject_arbitrary_suffixes(self) -> None:
        cases = (
            replace(
                self.software,
                python=PythonIdentity("3.11evil", "CPython"),
            ),
            replace(
                self.software,
                scipy=ScipyIdentity(
                    ">=1.11.0,<2.0.0", "1.16.3garbage"
                ),
            ),
        )
        for software in cases:
            with self.subTest(software=software):
                with self.assertRaises(ComparisonExecutionPreflightError):
                    self._preflight(software=software)


if __name__ == "__main__":
    unittest.main()
