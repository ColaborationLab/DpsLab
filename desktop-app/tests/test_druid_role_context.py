import unittest
from dataclasses import FrozenInstanceError

from dpslab.druid_role_context import select_druid_role_context


class DruidRoleContextTests(unittest.TestCase):
    def test_balance_is_damage_primary(self):
        result = select_druid_role_context("balance", "damage")
        self.assertEqual("context_available", result.status)
        self.assertEqual(("damage_output",), result.policy.primary_objectives)
        self.assertNotIn("damage_output", result.policy.secondary_objectives)

    def test_feral_is_damage_primary(self):
        result = select_druid_role_context("feral", "damage")
        self.assertEqual("context_available", result.status)
        self.assertEqual("damage", result.policy.role)

    def test_guardian_subordinates_damage_to_tank_safety(self):
        result = select_druid_role_context("guardian", "tank")
        self.assertEqual(
            ("survival", "active_mitigation", "threat_stability"),
            result.policy.primary_objectives,
        )
        self.assertEqual(("damage_output",), result.policy.secondary_objectives)

    def test_restoration_subordinates_damage_to_group_safety(self):
        result = select_druid_role_context("restoration", "healer")
        self.assertEqual(
            (
                "ally_survival",
                "healing_stability",
                "dispel_readiness",
                "emergency_capacity",
            ),
            result.policy.primary_objectives,
        )
        self.assertEqual(("damage_output",), result.policy.secondary_objectives)

    def test_every_role_keeps_hard_constraints(self):
        pairs = (
            ("balance", "damage"),
            ("feral", "damage"),
            ("guardian", "tank"),
            ("restoration", "healer"),
        )
        for specialization, role in pairs:
            with self.subTest(specialization=specialization):
                policy = select_druid_role_context(specialization, role).policy
                self.assertEqual(
                    ("encounter_obligations", "character_survival"),
                    policy.hard_constraints,
                )

    def test_unknown_and_noncanonical_specializations_fail_closed(self):
        for value in ("unknown", "Balance", " balance", "balance ", None, 102):
            with self.subTest(value=value):
                result = select_druid_role_context(value, "damage")
                self.assertEqual("context_unavailable", result.status)
                self.assertEqual("specialization_unknown", result.reason)
                self.assertIsNone(result.policy)

    def test_role_mismatch_and_invalid_role_fail_closed(self):
        for value in ("tank", "healer", "Damage", None, 3):
            with self.subTest(value=value):
                result = select_druid_role_context("balance", value)
                self.assertEqual("context_unavailable", result.status)
                self.assertEqual("role_mismatch", result.reason)
                self.assertIsNone(result.policy)

    def test_selection_and_policy_are_immutable(self):
        result = select_druid_role_context("guardian", "tank")
        with self.assertRaises(FrozenInstanceError):
            result.status = "changed"
        with self.assertRaises(FrozenInstanceError):
            result.policy.role = "damage"


if __name__ == "__main__":
    unittest.main()
