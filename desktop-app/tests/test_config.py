from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from dpslab.config import ConfigurationError, resolve_simulation_config
from dpslab.scenario import load_scenario


class SimulationConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / "config").mkdir()
        self.local_exe = self.root / "local-simc.exe"
        self.env_exe = self.root / "env-simc.exe"
        self.explicit_exe = self.root / "explicit-simc.exe"
        for executable in (self.local_exe, self.env_exe, self.explicit_exe):
            executable.touch()
        (self.root / "config" / "dpslab.local.toml").write_text(
            "[simulationcraft]\n"
            f'simc_exe = "{self.local_exe.as_posix()}"\n'
            "timeout_seconds = 42\n"
            "generate_html = true\n"
            'runs_dir = "custom-runs"\n',
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_explicit_path_has_highest_priority(self) -> None:
        config = resolve_simulation_config(
            explicit_simc_exe=self.explicit_exe,
            environ={"DPSLAB_SIMC_EXE": str(self.env_exe)},
            root=self.root,
        )
        self.assertEqual(config.simc_exe, self.explicit_exe.resolve())
        self.assertEqual(config.executable_source, "explicit_cli")

    def test_environment_precedes_local_file(self) -> None:
        config = resolve_simulation_config(
            environ={"DPSLAB_SIMC_EXE": str(self.env_exe)}, root=self.root
        )
        self.assertEqual(config.simc_exe, self.env_exe.resolve())
        self.assertEqual(config.executable_source, "environment")

    def test_local_file_provides_defaults(self) -> None:
        config = resolve_simulation_config(environ={}, root=self.root)
        self.assertEqual(config.simc_exe, self.local_exe.resolve())
        self.assertEqual(config.timeout_seconds, 42)
        self.assertTrue(config.generate_html)
        self.assertEqual(config.threads, 4)
        self.assertEqual(config.runs_dir, (self.root / "custom-runs").resolve())
        self.assertEqual(config.executable_source, "local_config")

    def test_positive_seed_is_typed_and_invalid_seed_is_rejected(self) -> None:
        config = resolve_simulation_config(environ={}, root=self.root, seed=1367750201)
        self.assertEqual(config.seed, 1367750201)
        for seed in (0, -1, True):
            with self.subTest(seed=seed), self.assertRaisesRegex(ConfigurationError, "seed"):
                resolve_simulation_config(environ={}, root=self.root, seed=seed)

    def test_missing_configuration_has_actionable_error(self) -> None:
        (self.root / "config" / "dpslab.local.toml").unlink()
        with self.assertRaisesRegex(ConfigurationError, "DPSLAB_SIMC_EXE"):
            resolve_simulation_config(environ={}, root=self.root)

    def test_nonexistent_executable_is_rejected(self) -> None:
        with self.assertRaisesRegex(ConfigurationError, "No existe simc.exe"):
            resolve_simulation_config(
                explicit_simc_exe=self.root / "missing.exe", environ={}, root=self.root
            )

    def test_smoke_overrides_are_typed_and_preserve_normal_defaults(self) -> None:
        normal = resolve_simulation_config(environ={}, root=self.root)
        smoke = resolve_simulation_config(
            environ={},
            root=self.root,
            threads=1,
            iterations=100,
            max_time=60,
            vary_combat_length=0,
            timeout_seconds=180,
            generate_html=True,
        )
        self.assertEqual(normal.threads, 4)
        self.assertIsNone(normal.iterations)
        self.assertEqual(smoke.threads, 1)
        self.assertEqual(smoke.iterations, 100)
        self.assertEqual(smoke.max_time, 60)
        self.assertEqual(smoke.vary_combat_length, 0)
        self.assertEqual(smoke.timeout_seconds, 180)
        self.assertTrue(smoke.generate_html)

    def test_scenario_values_and_cli_priority_are_resolved_before_validation(self) -> None:
        scenario = load_scenario(Path(__file__).parent / "fixtures" / "valid_scenario.toml")
        inherited = resolve_simulation_config(environ={}, root=self.root, scenario=scenario)
        self.assertEqual(inherited.iterations, 0)
        self.assertEqual(inherited.target_error, 0.05)
        self.assertEqual(inherited.max_time, 120)
        self.assertEqual(inherited.fight_style, "Patchwerk")

        fixed = resolve_simulation_config(
            environ={}, root=self.root, scenario=scenario, iterations=250, max_time=90
        )
        self.assertEqual(fixed.iterations, 250)
        self.assertIsNone(fixed.target_error)
        self.assertEqual(fixed.max_time, 90)

    def test_explicit_fixed_iterations_and_target_error_are_both_preserved(self) -> None:
        scenario = load_scenario(Path(__file__).parent / "fixtures" / "valid_scenario.toml")
        config = resolve_simulation_config(
            environ={}, root=self.root, scenario=scenario, iterations=250, target_error=0.02
        )
        self.assertEqual(config.iterations, 250)
        self.assertEqual(config.target_error, 0.02)

    def test_iterations_zero_without_target_error_is_rejected(self) -> None:
        with self.assertRaisesRegex(ConfigurationError, "target_error"):
            resolve_simulation_config(environ={}, root=self.root, iterations=0)

    def test_without_scenario_preserves_previous_effective_arguments(self) -> None:
        config = resolve_simulation_config(
            environ={},
            root=self.root,
            threads=1,
            iterations=100,
            max_time=60,
            vary_combat_length=0,
            timeout_seconds=180,
            generate_html=True,
        )
        self.assertIsNone(config.scenario)
        self.assertIsNone(config.fight_style)
        self.assertIsNone(config.desired_targets)
        self.assertIsNone(config.target_error)

    def test_local_config_preserves_configured_executable_path(self) -> None:
        nested_exe = self.root / "portable" / "SimulationCraft" / "simc.exe"
        nested_exe.parent.mkdir(parents=True)
        nested_exe.touch()
        (self.root / "config" / "dpslab.local.toml").write_text(
            "[simulationcraft]\n"
            f'simc_exe = "{nested_exe.as_posix()}"\n'
            'runs_dir = "results/runs"\n'
            "threads = 2\n"
            "timeout_seconds = 900\n",
            encoding="utf-8"
        )
        config = resolve_simulation_config(environ={}, root=self.root)
        self.assertEqual(config.simc_exe, nested_exe.resolve())
        self.assertEqual(config.executable_source, "local_config")
        self.assertEqual(config.threads, 2)
        self.assertEqual(config.timeout_seconds, 900)
        self.assertEqual(
            config.runs_dir,
            (self.root / "results" / "runs").resolve(),
        )


if __name__ == "__main__":
    unittest.main()
