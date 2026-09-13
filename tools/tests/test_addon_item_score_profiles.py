from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
LUA = (ROOT / "addon/DpsLab/ItemScoreProfiles.lua").read_text(encoding="utf-8")
TOC = (ROOT / "addon/DpsLab/DpsLab.toc").read_text(encoding="utf-8")


class AddonItemScoreProfilesTests(unittest.TestCase):
    def test_tooltip_hook_displays_each_selected_profile_score(self):
        self.assertIn('pcall(GameTooltip.HookScript, GameTooltip, "OnTooltipSetItem", addTooltipScores)', LUA)
        self.assertIn("Scores.ScoreItem(link, profile)", LUA)
        self.assertIn("tooltip:AddDoubleLine", LUA)
        self.assertIn("profile.name .. \" (\" .. profile.source", LUA)

    def test_visible_menu_persists_profile_selection_without_automation(self):
        self.assertIn("function Scores.ShowConfig()", LUA)
        self.assertIn("DpsLabItemScorePreferences.selected[profile.id]", LUA)
        self.assertIn("ItemScoreProfiles.lua", TOC)
        forbidden = ("C_Timer", "CastSpell", "RunMacro", "SendChatMessage", "http", "socket")
        self.assertTrue(all(token not in LUA for token in forbidden))
