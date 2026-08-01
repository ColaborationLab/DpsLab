import copy
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from dpslab.production_release_readiness import (
    ProductionReleaseReadinessContext,
    ProductionReleaseReadinessError,
    assess_production_release_readiness,
)


ROOT = Path(__file__).resolve().parents[2]
BUNDLE_PATH = ROOT / "knowledge/releases/candidate_knowledge_release_bundle_synthetic_0_1.json"
REGISTRY_PATH = ROOT / "knowledge/trust/release_trust_registry_0_1.json"
KEY_ID = "dpslab.release.ed25519.001"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class ProductionReleaseReadinessTests(unittest.TestCase):
    def setUp(self):
        self.synthetic = load(BUNDLE_PATH)
        self.registry = load(REGISTRY_PATH)
        self.context = ProductionReleaseReadinessContext(
            datetime(2026, 8, 1, 16, 0, tzinfo=timezone.utc), 120500, 120500, "stable", KEY_ID
        )
        self.candidate = copy.deepcopy(self.synthetic)
        replacements = {
            "release.synthetic.001": "release.production.001",
            "candidate.synthetic.001": "candidate.production.001",
            "placeholder.local.001": KEY_ID,
        }
        def rewrite(value):
            if isinstance(value, str):
                for old, new in replacements.items():
                    value = value.replace(old, new)
                return value.replace("synthetic", "production").replace("placeholder", "production")
            if isinstance(value, list):
                return [rewrite(item) for item in value]
            if isinstance(value, dict):
                return {key: rewrite(item) for key, item in value.items()}
            return value
        self.candidate = rewrite(self.candidate)
        self.candidate["release_envelope"]["evidence"]["expires_at"] = "2027-01-01T00:00:00Z"
        self.candidate["release_envelope"]["integrity"]["publisher_key_id"] = KEY_ID

    def assess(self, candidate=None, registry=None, context=None):
        with patch("dpslab.production_release_readiness.validate_candidate_release_bundle", return_value=candidate or self.candidate), patch("dpslab.production_release_readiness.validate_release_trust_registry", return_value=registry or self.registry):
            return assess_production_release_readiness(candidate or self.candidate, registry or self.registry, context or self.context)

    def test_actual_synthetic_fixture_is_rejected(self):
        outcome = assess_production_release_readiness(self.synthetic, self.registry, self.context)
        self.assertIn("synthetic_material_forbidden", outcome.reasons)

    def test_exact_current_candidate_is_ready_for_review_only(self):
        outcome = self.assess()
        self.assertEqual("production_release_candidate_ready_for_attended_signing_review", outcome.status)
        self.assertEqual((), outcome.reasons)

    def test_placeholder_is_rejected(self):
        candidate = copy.deepcopy(self.candidate)
        candidate["manifest"]["identity"]["bundle_id"] = "placeholder.release.001"
        self.assertIn("placeholder_material_forbidden", self.assess(candidate=candidate).reasons)

    def test_expired_evidence_is_rejected(self):
        candidate = copy.deepcopy(self.candidate)
        candidate["release_envelope"]["evidence"]["expires_at"] = "2026-08-01T16:00:00Z"
        self.assertIn("evidence_expired", self.assess(candidate=candidate).reasons)

    def test_build_and_interface_mismatch_are_separate(self):
        context = ProductionReleaseReadinessContext(self.context.observed_at, 130000, 130000, "stable", KEY_ID)
        reasons = self.assess(context=context).reasons
        self.assertIn("wow_build_outside_manifest", reasons)
        self.assertIn("interface_outside_manifest", reasons)

    def test_review_must_match_exact_observed_build(self):
        candidate = copy.deepcopy(self.candidate)
        candidate["review_decision"]["assessment"]["wow_build"] = 120499
        self.assertIn("review_wow_build_mismatch", self.assess(candidate=candidate).reasons)

    def test_missing_trusted_key_is_rejected(self):
        registry = copy.deepcopy(self.registry)
        registry["keys"] = []
        self.assertIn("trusted_production_key_not_found", self.assess(registry=registry).reasons)

    def test_invalid_context_fails_before_validation(self):
        context = ProductionReleaseReadinessContext(datetime(2026, 8, 1, 16, 0), 120500, 120500, "stable", KEY_ID)
        with self.assertRaisesRegex(ProductionReleaseReadinessError, "observed_at_invalid"):
            assess_production_release_readiness(self.synthetic, self.registry, context)


if __name__ == "__main__":
    unittest.main()
