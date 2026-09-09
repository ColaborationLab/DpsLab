import unittest
from pathlib import Path


class LiveAnalysisExportAddonTests(unittest.TestCase):
    def test_manual_export_has_no_chat_network_or_savedvariable_surface(self):
        root = Path(__file__).parents[2]
        lua = (root / "addon/DpsLab/DpsLab.lua").read_text()
        module = (root / "addon/DpsLab/CharacterEquipmentObservation.lua").read_text()
        toc = (root / "addon/DpsLab/DpsLab.toc").read_text()
        self.assertIn("CharacterEquipmentObservation.lua", toc)
        self.assertIn("showManualAnalysisExport(payload)", lua)
        self.assertIn("DPSLAB-LIVE-ANALYSIS-0.1", module)
        self.assertEqual(2, lua.count("CreateFrame("))
        for fragment in ("RegisterEvent", "C_Timer", "OnUpdate", "SendChatMessage", "DpsLabObservationExport = payload", "http"):
            self.assertNotIn(fragment, lua + module)

    def test_druid_export_uses_real_equipment_and_two_client_loadouts(self):
        root = Path(__file__).parents[2]
        module = (root / "addon/DpsLab/CharacterEquipmentObservation.lua").read_text()
        for fragment in (
            "[105]", "[102]", "GetDetailedItemLevelInfo",
            "GetActiveConfigID", "GetConfigIDsBySpecID", "GenerateImportString",
            '"schema_version":"0.4"',
        ):
            self.assertIn(fragment, module)
        self.assertNotIn("C_Container", module)

    def test_real_result_file_is_loaded_and_rendered_only_as_bounded_text(self):
        root = Path(__file__).parents[2]
        toc = (root / "addon/DpsLab/DpsLab.toc").read_text()
        lua = (root / "addon/DpsLab/DpsLab.lua").read_text()
        self.assertIn("DpsLabRealRecommendation.lua", toc)
        self.assertIn('command == "result"', lua)
        self.assertIn("realRecommendation", lua)
