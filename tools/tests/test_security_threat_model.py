import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "security" / "threat_model_0_1.json"
BASELINE = ROOT / "security" / "security_baseline_0_1.json"


class SecurityThreatModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.model = json.loads(MODEL.read_text(encoding="utf-8"))
        cls.baseline = json.loads(BASELINE.read_text(encoding="utf-8"))

    def test_model_is_closed_and_versioned(self) -> None:
        self.assertEqual(set(self.model), {"schema_version", "model_id", "review_triggers", "threats"})
        self.assertEqual(self.model["schema_version"], "0.1")
        self.assertEqual(self.model["model_id"], "dpslab.threat-model.0.1")

    def test_threat_ids_are_complete_ordered_and_unique(self) -> None:
        ids = [threat["id"] for threat in self.model["threats"]]
        self.assertEqual(ids, [f"TM-{number:02d}" for number in range(1, 13)])
        self.assertEqual(len(ids), len(set(ids)))

    def test_each_threat_has_closed_fields_and_controls(self) -> None:
        statuses = {"open_beta_gate", "partial_control"}
        for threat in self.model["threats"]:
            self.assertEqual(set(threat), {"id", "boundary", "assets", "status", "mitigations"})
            self.assertIn(threat["status"], statuses)
            self.assertTrue(threat["boundary"])
            self.assertEqual(threat["assets"], sorted(set(threat["assets"])))
            self.assertEqual(threat["mitigations"], sorted(set(threat["mitigations"])))
            self.assertTrue(threat["assets"])
            self.assertTrue(threat["mitigations"])

    def test_beta_cannot_be_ready_while_open_gates_exist(self) -> None:
        open_ids = [threat["id"] for threat in self.model["threats"] if threat["status"] == "open_beta_gate"]
        self.assertGreaterEqual(set(open_ids), {"TM-02", "TM-07", "TM-08", "TM-09"})
        self.assertIn("threat_model_review", self.baseline["external_beta_required_gates"])

    def test_review_triggers_are_sorted_and_cover_material_changes(self) -> None:
        triggers = self.model["review_triggers"]
        self.assertEqual(triggers, sorted(set(triggers)))
        self.assertGreaterEqual(set(triggers), {"addon_api_or_exchange_change", "release_key_change", "update_channel_change"})


if __name__ == "__main__":
    unittest.main()
