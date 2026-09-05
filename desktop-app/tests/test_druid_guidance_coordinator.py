from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
import copy
import json
from pathlib import Path
import unittest

from dpslab.addon_character_identity_transport import CharacterIdentitySnapshot
from dpslab.druid_guidance_coordinator import coordinate_druid_guidance
from dpslab.druid_current_template_evidence import (
    CompatibilityReceipt,
    DruidTemplateEvidence,
    SemanticMappingReceipt,
    TemplateReceipt,
)
from dpslab.druid_identity_context import (
    DruidIdentityRegistry,
    DruidSpecializationBinding,
)
from dpslab.static_template_catalog import ApprovalEvidence, calculate_catalog_sha256


ROOT = Path(__file__).parents[2]
CATALOG = ROOT / "knowledge/catalogs/static_template_catalog_synthetic_0_1.json"
NOW = datetime(2026, 8, 1, tzinfo=timezone.utc)
HASH = "a" * 64


def registry() -> DruidIdentityRegistry:
    return DruidIdentityRegistry(
        1,
        (
            DruidSpecializationBinding(71, "balance", "damage"),
            DruidSpecializationBinding(81002, "feral", "damage"),
            DruidSpecializationBinding(81003, "guardian", "tank"),
            DruidSpecializationBinding(81004, "restoration", "healer"),
        ),
    )


def snapshot(specialization_id=71, role="damage", class_id=1):
    return CharacterIdentitySnapshot(
        120500, 120500, class_id, specialization_id, role, 80, 1, 1_800_000_000
    )


def approved_catalog():
    document = json.loads(CATALOG.read_text(encoding="utf-8"))
    entry = document["entries"][0]
    entry["lifecycle_state"] = "approved"
    entry["source_coverage_complete"] = True
    entry["review"].update(
        {
            "decision_id": "synthetic.approval.001",
            "reviewer_id": "synthetic.reviewer",
            "decided_at": "2026-07-31T12:00:00Z",
        }
    )
    document["integrity"]["catalog_sha256"] = calculate_catalog_sha256(document)
    return document


def approval(document):
    entry = document["entries"][0]
    return ApprovalEvidence(
        document["identity"]["catalog_id"],
        document["identity"]["content_version"],
        entry["entry_id"],
        "synthetic.retail.damage.001",
        entry["envelope_sha256"],
        "approved",
        "synthetic.approval.001",
        "synthetic.reviewer",
        datetime(2026, 7, 31, 12, tzinfo=timezone.utc),
    )


def template_evidence(role="damage", specialization="balance"):
    receipt = lambda identifier: CompatibilityReceipt(
        identifier, HASH, 120500, 120500, 120500, 120500, True, True
    )
    safety = {
        "damage": "damage_primary",
        "tank": "survival_first",
        "healer": "healing_safety_first",
    }[role]
    return DruidTemplateEvidence(
        receipt("synthetic.registry.001"),
        SemanticMappingReceipt(
            "synthetic.mapping.001", HASH, specialization, role, True, True
        ),
        receipt("synthetic.primary.001"),
        TemplateReceipt("synthetic.template.001", HASH, role, safety, True, True),
    )


class DruidGuidanceCoordinatorTests(unittest.TestCase):
    def decide(self, **changes):
        document = changes.pop("catalog", approved_catalog())
        if "approval" in changes:
            evidence = changes.pop("approval")
        elif isinstance(document, dict) and document.get("entries"):
            evidence = approval(document)
        else:
            evidence = None
        values = {
            "snapshot": snapshot(),
            "registry": registry(),
            "catalog": document,
            "repository_root": ROOT,
            "content_context": "synthetic_single_target",
            "observed_at": NOW,
            "approval": evidence,
            "template_evidence": template_evidence(),
        }
        values.update(changes)
        return coordinate_druid_guidance(**values)

    def test_complete_synthetic_damage_path_returns_explained_guidance(self):
        result = self.decide()
        self.assertEqual("guidance_available", result.status)
        self.assertEqual("synthetic.damage.001", result.entry_id)
        self.assertEqual(("damage_output",), result.policy.primary_objectives)
        self.assertEqual(2, len(result.statements))

    def test_pending_catalog_and_missing_approval_fail_closed(self):
        pending = json.loads(CATALOG.read_text(encoding="utf-8"))
        self.assertEqual(
            "no_eligible_entry", self.decide(catalog=pending, approval=None).reason
        )
        document = approved_catalog()
        self.assertEqual(
            "approval_missing", self.decide(catalog=document, approval=None).reason
        )

    def test_missing_or_incompatible_evidence_short_circuits_catalog(self):
        self.assertEqual(
            "evidence_invalid", self.decide(template_evidence=None, catalog={}).reason
        )
        self.assertEqual(
            "mapping_evidence_unavailable",
            self.decide(template_evidence=template_evidence(specialization="feral"), catalog={}).reason,
        )

    def test_mismatched_approval_fails_closed(self):
        document = approved_catalog()
        evidence = approval(document)
        changed = ApprovalEvidence(
            **{**evidence.__dict__, "catalog_content_version": "9.9.9"}
        )
        self.assertEqual(
            "approval_mismatch", self.decide(catalog=document, approval=changed).reason
        )

    def test_identity_failure_short_circuits_invalid_knowledge(self):
        result = self.decide(snapshot=snapshot(class_id=2), catalog={})
        self.assertEqual(
            ("guidance_unavailable", "class_mismatch"),
            (result.status, result.reason),
        )
        self.assertIsNone(result.policy)

    def test_role_mismatch_never_reaches_catalog(self):
        result = self.decide(snapshot=snapshot(role="tank"), catalog={})
        self.assertEqual("role_mismatch", result.reason)
        self.assertEqual((), result.statements)

    def test_guardian_policy_remains_available_but_damage_catalog_does_not(self):
        result = self.decide(
            snapshot=snapshot(81003, "tank"),
            template_evidence=template_evidence("tank", "guardian"),
        )
        self.assertEqual(
            ("guidance_unavailable", "no_eligible_entry"),
            (result.status, result.reason),
        )
        self.assertEqual("guardian", result.policy.specialization)
        self.assertEqual(("damage_output",), result.policy.secondary_objectives)

    def test_malformed_catalog_becomes_bounded_unavailable_state(self):
        document = approved_catalog()
        document["integrity"]["catalog_sha256"] = "0" * 64
        result = self.decide(catalog=document, approval=None)
        self.assertEqual(
            ("guidance_unavailable", "knowledge_invalid"),
            (result.status, result.reason),
        )

    def test_invalid_request_inputs_fail_closed(self):
        for field, value, reason in (
            ("catalog", [], "catalog_invalid"),
            ("repository_root", str(ROOT), "repository_root_invalid"),
            ("content_context", "Synthetic Context", "content_context_invalid"),
            ("observed_at", datetime(2026, 8, 1), "observed_at_invalid"),
            ("approval", object(), "approval_invalid"),
        ):
            with self.subTest(field=field):
                self.assertEqual(reason, self.decide(**{field: value}).reason)

    def test_result_is_frozen_and_exposes_no_identity_fields(self):
        result = self.decide()
        self.assertEqual(
            {"status", "reason", "policy", "entry_id", "statements"},
            set(result.__dataclass_fields__),
        )
        with self.assertRaises(FrozenInstanceError):
            result.status = "changed"

    def test_input_objects_are_not_mutated(self):
        document = approved_catalog()
        original = copy.deepcopy(document)
        self.decide(catalog=document, approval=approval(document))
        self.assertEqual(original, document)


if __name__ == "__main__":
    unittest.main()
