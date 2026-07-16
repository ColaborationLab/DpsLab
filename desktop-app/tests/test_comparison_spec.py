from __future__ import annotations

import tempfile
import unittest
import json
import shutil
from pathlib import Path

from dpslab.comparison_spec import ComparisonSpecError, _validate_evidence, load_comparison_spec


ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "comparisons" / "flasil_neck_50228_vs_249368_v1.toml"


class ComparisonSpecTests(unittest.TestCase):
    def test_repository_spec_is_frozen_and_closed(self) -> None:
        spec = load_comparison_spec(SPEC, root=ROOT)
        self.assertEqual(spec.comparison_id, "flasil_neck_50228_vs_249368_v1")
        self.assertEqual(spec.protocol.iterations_per_run, 5000)
        self.assertEqual(spec.protocol.threads, 2)
        self.assertEqual(len(spec.protocol.seeds), 8)
        self.assertEqual(spec.arm_b.expected_profile_line, "neck=,id=249368,gem_id=240906,bonus_id=6652/13668/13334/12798")

    def _mutated(self, old: str, new: str) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / "spec.toml"
        path.write_text(SPEC.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")
        return path

    def test_unknown_root_field_is_rejected(self) -> None:
        with self.assertRaisesRegex(ComparisonSpecError, "Campos desconocidos"):
            load_comparison_spec(self._mutated('schema_version = "0.1"', 'schema_version = "0.1"\nunknown = 1'), root=ROOT)

    def test_unknown_nested_field_is_rejected(self) -> None:
        with self.assertRaisesRegex(ComparisonSpecError, "Campos desconocidos"):
            load_comparison_spec(self._mutated('slot = "neck"', 'slot = "neck"\nother = true'), root=ROOT)

    def test_draft_spec_is_rejected(self) -> None:
        with self.assertRaisesRegex(ComparisonSpecError, "congelado"):
            load_comparison_spec(self._mutated('status = "frozen"', 'status = "draft"'), root=ROOT)

    def test_changed_seed_is_rejected(self) -> None:
        with self.assertRaisesRegex(ComparisonSpecError, "Seeds"):
            load_comparison_spec(self._mutated("1367750201", "1367750202"), root=ROOT)

    def test_changed_order_is_rejected(self) -> None:
        with self.assertRaisesRegex(ComparisonSpecError, "Seeds"):
            load_comparison_spec(self._mutated('orders = ["AB", "BA"', 'orders = ["BA", "BA"'), root=ROOT)

    def test_evidence_hash_is_verified(self) -> None:
        with self.assertRaisesRegex(ComparisonSpecError, "evidencia"):
            load_comparison_spec(self._mutated("0472ee720a94e8bb46d446b671bedd5d15c95a72cce808de6f20f69dd374e8fe", "0" * 64), root=ROOT)

    def test_target_error_field_is_rejected(self) -> None:
        with self.assertRaisesRegex(ComparisonSpecError, "Campos desconocidos"):
            load_comparison_spec(self._mutated('iterations_per_run = 5000', 'iterations_per_run = 5000\ntarget_error = 0.1'), root=ROOT)

    def test_every_frozen_contract_family_is_rejected_when_changed(self) -> None:
        mutations = (
            ('comparison_id = "flasil_neck_50228_vs_249368_v1"', 'comparison_id = "other"'),
            ('sha256 = "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738"', 'sha256 = "' + '0' * 64 + '"'),
            ('item_id = 50228', 'item_id = 50229'),
            ('item_level = 276', 'item_level = 277'),
            ('declared_gem_id = 240906', 'declared_gem_id = 240907'),
            ('declared_bonus_ids = [13440, 6652, 13668, 12699, 12798]', 'declared_bonus_ids = [13440, 6652]'),
            ('blocks = 8', 'blocks = 7'),
            ('iterations_per_run = 5000', 'iterations_per_run = 4999'),
            ('threads = 2', 'threads = 3'),
            ('within_pair_pause_seconds = 30', 'within_pair_pause_seconds = 29'),
            ('timeout_seconds = 900', 'timeout_seconds = 901'),
            ('max_pair_attempts = 2', 'max_pair_attempts = 3'),
            ('confidence_level = 0.95', 'confidence_level = 0.90'),
            ('epsilon_percent = 0.5', 'epsilon_percent = 0.6'),
            ('primary_method = "welch_delta_ratio_percent_v1"', 'primary_method = "other"'),
            ('simulationcraft_revision = "a81c39d"', 'simulationcraft_revision = "other"'),
        )
        for old, new in mutations:
            with self.subTest(old=old), self.assertRaises(ComparisonSpecError):
                load_comparison_spec(self._mutated(old, new), root=ROOT)

    def test_missing_required_field_is_rejected(self) -> None:
        with self.assertRaises(ComparisonSpecError):
            load_comparison_spec(self._mutated('description = "Barbed Ymirheim Choker vs Eternal Voidsong Chain"\n', ''), root=ROOT)

    def test_manifest_missing_image_changed_identity_and_conclusion_fail(self) -> None:
        source = ROOT / "comparisons/evidence/flasil_neck_50228_vs_249368_v1"
        for mutation in ("missing_image", "identity", "conclusion"):
            with self.subTest(mutation=mutation):
                temporary = tempfile.TemporaryDirectory()
                self.addCleanup(temporary.cleanup)
                package = Path(temporary.name) / "evidence"
                shutil.copytree(source, package)
                manifest = package / "evidence_manifest.json"
                document = json.loads(manifest.read_text(encoding="utf-8"))
                if mutation == "missing_image":
                    (package / document["images"][0]["file"]).unlink()
                elif mutation == "identity":
                    document["profile_correlation"]["gem_identity"] = "Other"
                    manifest.write_text(json.dumps(document), encoding="utf-8")
                else:
                    document["compatibility_conclusion"] = "Other"
                    manifest.write_text(json.dumps(document), encoding="utf-8")
                with self.assertRaises(ComparisonSpecError):
                    _validate_evidence(manifest, ROOT)


if __name__ == "__main__":
    unittest.main()
