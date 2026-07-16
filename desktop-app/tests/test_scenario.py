from __future__ import annotations

import tempfile
import unittest
from hashlib import sha256
from pathlib import Path

from dpslab.scenario import ScenarioError, load_scenario


FIXTURES = Path(__file__).parent / "fixtures"


class ScenarioTests(unittest.TestCase):
    def test_loads_valid_adaptive_scenario_and_hashes_bytes(self) -> None:
        path = FIXTURES / "valid_scenario.toml"
        before = path.read_bytes()
        loaded = load_scenario(path)
        self.assertEqual(loaded.scenario.id, "anonymous_scenario_v1")
        self.assertEqual(loaded.scenario.precision.iterations, 0)
        self.assertEqual(loaded.scenario.precision.target_error, 0.05)
        self.assertEqual(loaded.source_sha256, sha256(before).hexdigest())
        self.assertEqual(path.read_bytes(), before)

    def test_missing_file_has_clear_error(self) -> None:
        with self.assertRaisesRegex(ScenarioError, "No existe el escenario"):
            load_scenario(Path("missing-scenario.toml"))

    def test_invalid_toml_has_clear_error(self) -> None:
        with self.assertRaisesRegex(ScenarioError, "TOML UTF-8 válido"):
            load_scenario(FIXTURES / "invalid_scenario.toml")

    def test_rejects_invalid_ranges(self) -> None:
        valid = (FIXTURES / "valid_scenario.toml").read_text(encoding="utf-8")
        replacements = (
            ("desired_targets = 1", "desired_targets = 0", "desired_targets"),
            ("max_time = 120", "max_time = 0", "max_time"),
            ("vary_combat_length = 0.10", "vary_combat_length = 1.5", "vary_combat_length"),
            ("iterations = 0", "iterations = -1", "iterations"),
        )
        for old, new, error in replacements:
            with self.subTest(field=error), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "scenario.toml"
                path.write_text(valid.replace(old, new), encoding="utf-8")
                with self.assertRaisesRegex(ScenarioError, error):
                    load_scenario(path)

    def test_iterations_zero_requires_target_error(self) -> None:
        source = (FIXTURES / "valid_scenario.toml").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scenario.toml"
            path.write_text(source.replace("target_error = 0.05\n", ""), encoding="utf-8")
            with self.assertRaisesRegex(ScenarioError, "target_error"):
                load_scenario(path)


if __name__ == "__main__":
    unittest.main()

