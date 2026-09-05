from dataclasses import FrozenInstanceError
import unittest

from dpslab.druid_current_template_evidence import (
    CompatibilityReceipt,
    DruidTemplateEvidence,
    SemanticMappingReceipt,
    TemplateReceipt,
    evaluate_druid_template_evidence,
)
from dpslab.druid_role_context import select_druid_role_context


HASH = "a" * 64


def policy(role="damage"):
    result = select_druid_role_context("balance", role)
    assert result.policy is not None
    return result.policy


def receipt(identifier):
    return CompatibilityReceipt(identifier, HASH, 100, 200, 100, 200, True, True)


def evidence(role="damage", specialization="balance"):
    return DruidTemplateEvidence(
        receipt("synthetic.registry.001"),
        SemanticMappingReceipt(
            "synthetic.mapping.001", HASH, specialization, role, True, True
        ),
        receipt("synthetic.primary.001"),
        TemplateReceipt(
            "synthetic.template.001",
            HASH,
            role,
            {"damage": "damage_primary", "tank": "survival_first", "healer": "healing_safety_first"}[role],
            True,
            True,
        ),
    )


class DruidCurrentTemplateEvidenceTests(unittest.TestCase):
    def test_complete_synthetic_evidence_is_review_eligible(self):
        result = evaluate_druid_template_evidence(policy(), evidence(), 150, 150)
        self.assertEqual(("review_eligible", None), (result.status, result.reason))
        self.assertEqual("synthetic.template.001", result.template_id)

    def test_registry_and_primary_ranges_fail_closed(self):
        for field, changed, reason in (
            ("registry", receipt("synthetic.registry.001"), "registry_evidence_unavailable"),
            ("primary_source", receipt("synthetic.primary.001"), "primary_source_evidence_unavailable"),
        ):
            with self.subTest(field=field):
                changed = CompatibilityReceipt(
                    **{**changed.__dict__, "build_max": 149}
                )
                values = evidence().__dict__.copy()
                values[field] = changed
                self.assertEqual(
                    reason,
                    evaluate_druid_template_evidence(policy(), DruidTemplateEvidence(**values), 150, 150).reason,
                )

    def test_mapping_must_be_reviewed_synthetic_and_exact(self):
        for changes in (
            {"reviewed": False}, {"synthetic": False}, {"specialization": "feral"}, {"role": "tank"}
        ):
            with self.subTest(changes=changes):
                original = evidence().mapping
                values = evidence().__dict__.copy()
                values["mapping"] = SemanticMappingReceipt(**{**original.__dict__, **changes})
                self.assertEqual(
                    "mapping_evidence_unavailable",
                    evaluate_druid_template_evidence(policy(), DruidTemplateEvidence(**values), 150, 150).reason,
                )

    def test_template_requires_role_safety_closed_and_synthetic(self):
        for changes in (
            {"role": "tank"}, {"safety_ordering": "unsafe_ordering"}, {"closed": False}, {"synthetic": False}
        ):
            with self.subTest(changes=changes):
                values = evidence().__dict__.copy()
                values["template"] = TemplateReceipt(**{**evidence().template.__dict__, **changes})
                self.assertEqual(
                    "template_evidence_unavailable",
                    evaluate_druid_template_evidence(policy(), DruidTemplateEvidence(**values), 150, 150).reason,
                )

    def test_invalid_top_level_inputs_fail_closed(self):
        for args, reason in (
            ((object(), evidence(), 150, 150), "policy_invalid"),
            ((policy(), object(), 150, 150), "evidence_invalid"),
            ((policy(), evidence(), True, 150), "build_invalid"),
            ((policy(), evidence(), 150, 0), "interface_invalid"),
        ):
            with self.subTest(reason=reason):
                self.assertEqual(reason, evaluate_druid_template_evidence(*args).reason)

    def test_decision_is_immutable_and_minimal(self):
        result = evaluate_druid_template_evidence(policy(), evidence(), 150, 150)
        self.assertEqual({"status", "reason", "policy", "template_id"}, set(result.__dataclass_fields__))
        with self.assertRaises(FrozenInstanceError):
            result.status = "changed"


if __name__ == "__main__":
    unittest.main()
