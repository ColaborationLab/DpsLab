import unittest
from dataclasses import FrozenInstanceError

from dpslab.addon_character_identity_transport import CharacterIdentitySnapshot
from dpslab.druid_identity_context import (
    DruidIdentityRegistry,
    DruidSpecializationBinding,
    bind_druid_identity_context,
)


def registry():
    return DruidIdentityRegistry(
        class_id=901,
        bindings=(
            DruidSpecializationBinding(9001, "balance", "damage"),
            DruidSpecializationBinding(9002, "feral", "damage"),
            DruidSpecializationBinding(9003, "guardian", "tank"),
            DruidSpecializationBinding(9004, "restoration", "healer"),
        ),
    )


def snapshot(specialization_id=9001, role="damage", class_id=901):
    return CharacterIdentitySnapshot(
        9_000_001,
        9_000_001,
        class_id,
        specialization_id,
        role,
        900,
        900,
        9_000_000_001,
    )


class DruidIdentityContextTests(unittest.TestCase):
    def test_all_four_synthetic_bindings_select_exact_policy(self):
        cases = (
            (9001, "damage", "balance"),
            (9002, "damage", "feral"),
            (9003, "tank", "guardian"),
            (9004, "healer", "restoration"),
        )
        for specialization_id, role, specialization in cases:
            with self.subTest(specialization=specialization):
                result = bind_druid_identity_context(
                    snapshot(specialization_id, role), registry()
                )
                self.assertEqual("context_available", result.status)
                self.assertEqual(specialization, result.policy.specialization)

    def test_guardian_and_restoration_keep_damage_secondary(self):
        for specialization_id, role in ((9003, "tank"), (9004, "healer")):
            with self.subTest(role=role):
                result = bind_druid_identity_context(
                    snapshot(specialization_id, role), registry()
                )
                self.assertEqual(("damage_output",), result.policy.secondary_objectives)

    def test_class_mismatch_fails_closed(self):
        result = bind_druid_identity_context(snapshot(class_id=902), registry())
        self.assertEqual(("context_unavailable", "class_mismatch", None), tuple(result.__dict__.values()))

    def test_unmapped_specialization_fails_closed(self):
        result = bind_druid_identity_context(snapshot(9999), registry())
        self.assertEqual("specialization_unmapped", result.reason)
        self.assertIsNone(result.policy)

    def test_role_mismatch_fails_closed(self):
        result = bind_druid_identity_context(snapshot(9003, "damage"), registry())
        self.assertEqual("role_mismatch", result.reason)
        self.assertIsNone(result.policy)

    def test_invalid_or_forged_observation_fails_closed(self):
        forged = CharacterIdentitySnapshot(True, 9_000_001, 901, 9001, "damage", 900, 900, 9_000_000_001)
        for value in (None, {}, forged):
            with self.subTest(value=type(value).__name__):
                result = bind_druid_identity_context(value, registry())
                self.assertEqual("observation_invalid", result.reason)

    def test_incomplete_duplicate_or_semantically_invalid_registry_fails_closed(self):
        valid = registry()
        invalid = (
            None,
            DruidIdentityRegistry(901, valid.bindings[:3]),
            DruidIdentityRegistry(901, valid.bindings[:3] + (DruidSpecializationBinding(9003, "restoration", "healer"),)),
            DruidIdentityRegistry(901, valid.bindings[:3] + (DruidSpecializationBinding(9004, "restoration", "damage"),)),
            DruidIdentityRegistry(True, valid.bindings),
        )
        for value in invalid:
            with self.subTest(value=value):
                result = bind_druid_identity_context(snapshot(), value)
                self.assertEqual("registry_invalid", result.reason)
                self.assertIsNone(result.policy)

    def test_result_registry_and_bindings_are_immutable_and_result_has_no_observation(self):
        value = registry()
        result = bind_druid_identity_context(snapshot(), value)
        self.assertEqual({"status", "reason", "policy"}, set(result.__dict__))
        with self.assertRaises(FrozenInstanceError):
            value.class_id = 902
        with self.assertRaises(FrozenInstanceError):
            value.bindings[0].role = "tank"
        with self.assertRaises(FrozenInstanceError):
            result.reason = "changed"


if __name__ == "__main__":
    unittest.main()
