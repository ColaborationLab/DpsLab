import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOC = ROOT / "addon" / "DpsLab" / "DpsLab.toc"
LUA = ROOT / "addon" / "DpsLab" / "DpsLab.lua"


class AddonSyntheticRendererTests(unittest.TestCase):
    def setUp(self) -> None:
        self.toc = TOC.read_text(encoding="utf-8")
        self.lua = LUA.read_text(encoding="utf-8")

    def test_toc_declares_only_the_single_renderer(self) -> None:
        self.assertIn("## Interface: 120000", self.toc)
        self.assertIn("DpsLab.lua", self.toc)
        self.assertNotIn("SavedVariables", self.toc)

    def test_renderer_has_only_safe_synthetic_and_unavailable_states(self) -> None:
        self.assertIn('status = "unavailable"', self.lua)
        self.assertIn('status = "synthetic"', self.lua)
        self.assertIn("function DpsLab.Render(state)", self.lua)
        self.assertIn("function DpsLab.IsActionable(view)", self.lua)
        self.assertIn('view.status == "approved"', self.lua)

    def test_prohibited_automation_network_and_data_surfaces_are_absent(self) -> None:
        prohibited = (
            "C_", "CastSpell", "UseAction", "RunMacro", "SendChatMessage",
            "CreateFrame", "LoadAddOn", "SavedVariables", "http", "socket",
            "donate", "patreon", "telemetry",
        )
        lower = self.lua.lower()
        for token in prohibited:
            with self.subTest(token=token):
                self.assertNotIn(token.lower(), lower)


if __name__ == "__main__":
    unittest.main()
