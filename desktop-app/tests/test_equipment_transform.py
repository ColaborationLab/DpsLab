from __future__ import annotations

import tempfile
import unittest
from dataclasses import replace
from hashlib import sha256
from pathlib import Path

from tests.strict_temporary_cleanup import strict_temporary_cleanup

from dpslab.comparison_spec import load_comparison_spec
from dpslab.equipment_transform import EquipmentTransformError, materialize_neck_profile


ROOT = Path(__file__).resolve().parents[2]
SPEC = load_comparison_spec(ROOT / "comparisons/flasil_neck_50228_vs_249368_v1.toml", root=ROOT)


class EquipmentTransformTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(strict_temporary_cleanup, self.temp, Path(self.temp.name))
        self.destination = Path(self.temp.name) / "effective.simc"

    def test_a_materialization_is_equivalent_to_equipped_line(self) -> None:
        base = (ROOT / "profiles" / "flasil.simc").read_bytes()
        result = materialize_neck_profile(base, SPEC.arm_a, self.destination)
        self.assertEqual(self.destination.read_bytes(), base)
        self.assertEqual(result.base_sha256, result.effective_sha256)

    def test_b_changes_only_neck_and_preserves_bonus_ids(self) -> None:
        base = (ROOT / "profiles" / "flasil.simc").read_bytes()
        result = materialize_neck_profile(base, SPEC.arm_b, self.destination)
        before, after = base.decode().splitlines(), self.destination.read_text(encoding="utf-8").splitlines()
        differences = [(left, right) for left, right in zip(before, after) if left != right]
        self.assertEqual(differences, [(SPEC.arm_a.expected_profile_line, SPEC.arm_b.expected_profile_line)])
        self.assertIn("bonus_id=6652/13668/13334/12798", result.effective_line)
        self.assertNotIn("enchant_id", result.effective_line)

    def test_materialization_is_atomic_and_hashes_output(self) -> None:
        base = b"warlock=x\nneck=,id=1\n"
        result = materialize_neck_profile(base, SPEC.arm_b, self.destination)
        self.assertEqual(result.effective_sha256, sha256(self.destination.read_bytes()).hexdigest())
        self.assertEqual(list(Path(self.temp.name).glob(".equipment_profile.*.tmp")), [])

    def test_missing_neck_is_rejected(self) -> None:
        with self.assertRaisesRegex(EquipmentTransformError, "linea neck"):
            materialize_neck_profile(b"warlock=x\n", SPEC.arm_b, self.destination)

    def test_multiple_active_necks_are_rejected(self) -> None:
        with self.assertRaisesRegex(EquipmentTransformError, "encontraron 2"):
            materialize_neck_profile(b"neck=,id=1\nneck=,id=2\n", SPEC.arm_b, self.destination)

    def test_crlf_and_lf_are_preserved_byte_for_byte_outside_neck(self) -> None:
        for ending in (b"\n", b"\r\n"):
            with self.subTest(ending=ending):
                base = ending.join((b"warlock=x", SPEC.arm_a.expected_profile_line.encode(), b"# neck=bag", b"tail")) + ending
                materialize_neck_profile(base, SPEC.arm_b, self.destination)
                expected = ending.join((b"warlock=x", SPEC.arm_b.expected_profile_line.encode(), b"# neck=bag", b"tail")) + ending
                self.assertEqual(self.destination.read_bytes(), expected)

    def test_non_neck_arm_is_rejected(self) -> None:
        with self.assertRaisesRegex(EquipmentTransformError, "solo acepta"):
            materialize_neck_profile(b"neck=,id=1\n", replace(SPEC.arm_b, slot="head"), self.destination)

    def test_bonus_ids_have_canonical_form_without_changing_serialization(self) -> None:
        reordered = replace(SPEC.arm_b, bonus_ids=(12798, 6652, 13334, 13668))
        duplicated = replace(SPEC.arm_b, bonus_ids=(6652, 13668, 13334, 12798, 6652))
        self.assertEqual(reordered.canonical_bonus_ids, SPEC.arm_b.canonical_bonus_ids)
        self.assertEqual(duplicated.canonical_bonus_ids.count(6652), 2)
        self.assertEqual(reordered.expected_profile_line, SPEC.arm_b.expected_profile_line)


if __name__ == "__main__":
    unittest.main()
