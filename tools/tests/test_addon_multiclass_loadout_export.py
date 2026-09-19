import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXPORTER = (ROOT / "addon" / "DpsLab" / "CharacterEquipmentObservation.lua").read_text(encoding="utf-8")
RENDERER = (ROOT / "addon" / "DpsLab" / "DpsLab.lua").read_text(encoding="utf-8")


class AddonMulticlassLoadoutExportTests(unittest.TestCase):
    def test_capture_uses_the_client_role_without_a_druid_specialization_allowlist(self):
        self.assertIn('local ROLE_MAP = { DAMAGER = "damage", TANK = "tank", HEALER = "healer" }', EXPORTER)
        self.assertIn('local subjectRole = ROLE_MAP[role]', EXPORTER)
        self.assertNotIn("DRUID_CLASS_ID", EXPORTER)
        self.assertNotIn("SUPPORTED_SPECS", EXPORTER)
        self.assertNotIn("analysis_druid_specialization_required", EXPORTER + RENDERER)

    def test_result_reader_accepts_contextual_generic_results_without_relaxing_balance_weights(self):
        self.assertIn('value.schema_version ~= "0.3"', RENDERER)
        self.assertIn('context.specialization_id', RENDERER)
        self.assertIn('advisor.specialization_id ~= 102', RENDERER)


if __name__ == "__main__":
    unittest.main()
