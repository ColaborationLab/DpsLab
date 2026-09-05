import json
import unittest

from dpslab.advisor_guidance_package import (
    MAX_BYTES,
    PREFIX,
    AdvisorGuidancePackageError,
    canonical_advisor_guidance_package_bytes,
    parse_synthetic_advisor_guidance_package,
)


def document():
    return {
        "schema_version": "0.1",
        "synthetic": True,
        "lifecycle": {"state": "synthetic_fixture"},
        "safety": {"actionable": False, "no_automation": True},
        "roles": {
            role: {
                "statistic_target": "stat",
                "gear_priority": "gear",
                "priority_display": "priority",
                "safety_first": safety,
            }
            for role, safety in (
                ("damage", "damage"),
                ("tank", "survival"),
                ("healer", "healing"),
            )
        },
    }


def payload(value=None):
    return PREFIX + canonical_advisor_guidance_package_bytes(value or document()).decode()


class AdvisorGuidanceTests(unittest.TestCase):
    def assert_rejected(self, value, reason, role="damage"):
        with self.assertRaisesRegex(AdvisorGuidancePackageError, reason):
            parse_synthetic_advisor_guidance_package(payload(value), role)

    def test_valid_role_result_is_immutable(self):
        result = parse_synthetic_advisor_guidance_package(payload(), "tank")
        self.assertEqual("survival", result.safety_first)
        with self.assertRaisesRegex(AttributeError, "cannot assign"):
            result.safety_first = "damage"

    def test_rejects_prefix_role_and_payload_size(self):
        with self.assertRaisesRegex(AdvisorGuidancePackageError, "prefix"):
            parse_synthetic_advisor_guidance_package("{}", "damage")
        with self.assertRaisesRegex(AdvisorGuidancePackageError, "role"):
            parse_synthetic_advisor_guidance_package(payload(), "support")
        with self.assertRaisesRegex(AdvisorGuidancePackageError, "size"):
            parse_synthetic_advisor_guidance_package(PREFIX + "x" * (MAX_BYTES + 1), "damage")

    def test_rejects_duplicate_keys_and_nonfinite_numbers(self):
        duplicate = '{"schema_version":"0.1","schema_version":"0.1"}'
        with self.assertRaisesRegex(AdvisorGuidancePackageError, "duplicate"):
            parse_synthetic_advisor_guidance_package(PREFIX + duplicate, "damage")
        with self.assertRaisesRegex(AdvisorGuidancePackageError, "nonfinite"):
            parse_synthetic_advisor_guidance_package(PREFIX + '{"value":NaN}', "damage")

    def test_rejects_noncanonical_and_non_object_json(self):
        with self.assertRaisesRegex(AdvisorGuidancePackageError, "noncanonical"):
            parse_synthetic_advisor_guidance_package(PREFIX + json.dumps(document(), indent=1) + "\n", "damage")
        with self.assertRaisesRegex(AdvisorGuidancePackageError, "root"):
            parse_synthetic_advisor_guidance_package(PREFIX + "[]", "damage")

    def test_rejects_closed_root_and_nested_fields(self):
        value = document()
        value["personalized"] = False
        self.assert_rejected(value, "root")
        value = document()
        value["roles"]["damage"]["live_source"] = "no"
        self.assert_rejected(value, "role")
        value = document()
        del value["roles"]["healer"]
        self.assert_rejected(value, "roles")

    def test_rejects_synthetic_lifecycle_and_safety_markers(self):
        value = document()
        value["synthetic"] = False
        self.assert_rejected(value, "schema")
        value = document()
        value["lifecycle"]["state"] = "current_content"
        self.assert_rejected(value, "lifecycle")
        value = document()
        value["safety"]["actionable"] = True
        self.assert_rejected(value, "safety")
        value = document()
        value["safety"]["no_automation"] = False
        self.assert_rejected(value, "safety")

    def test_rejects_role_safety_and_text_shape(self):
        value = document()
        value["roles"]["healer"]["safety_first"] = "damage"
        self.assert_rejected(value, "role", "healer")
        value = document()
        value["roles"]["tank"]["statistic_target"] = 1
        self.assert_rejected(value, "role", "tank")
        value = document()
        value["roles"]["damage"]["gear_priority"] = "x" * 161
        self.assert_rejected(value, "role")
