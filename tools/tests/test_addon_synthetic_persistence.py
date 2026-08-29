import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOC = ROOT / "addon" / "DpsLab" / "DpsLab.toc"
LUA = ROOT / "addon" / "DpsLab" / "DpsLab.lua"


class AddonSyntheticPersistenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.toc = TOC.read_text(encoding="utf-8")
        self.lua = LUA.read_text(encoding="utf-8")
        match = re.search(
            r"local function handleSyntheticExport\(action\)(.*?)\nend\n\nSLASH_DPSLAB1",
            self.lua,
            re.DOTALL,
        )
        self.assertIsNotNone(match)
        self.handler = match.group(1)

    def test_one_account_wide_saved_variable_is_declared(self) -> None:
        declarations = [line for line in self.toc.splitlines() if line.startswith("## SavedVariables")]
        self.assertEqual(declarations, ["## SavedVariables: DpsLabObservationExport"])

    def test_only_two_exact_manual_export_actions_are_implemented(self) -> None:
        self.assertIn('if action == "clear" then', self.handler)
        self.assertIn('if action ~= "synthetic" then return "unsupported" end', self.handler)
        self.assertIn('if command == "export" then', self.lua)
        self.assertNotIn("export automatic", self.lua.lower())

    def test_invalid_serializer_and_unknown_action_preserve_existing_value(self) -> None:
        unsupported = self.handler.index('if action ~= "synthetic"')
        candidate = self.handler.index("local candidate = syntheticExportCandidate()")
        unavailable = self.handler.index('if candidate == nil then return "unavailable" end')
        assignment = self.handler.index("_G.DpsLabObservationExport = candidate")
        self.assertLess(unsupported, candidate)
        self.assertLess(candidate, unavailable)
        self.assertLess(unavailable, assignment)
        self.assertEqual(self.handler.count("_G.DpsLabObservationExport = candidate"), 1)

    def test_retained_value_is_strict_lowercase_hex_not_nested_assignment(self) -> None:
        self.assertIn(
            "DpsLabSyntheticObservationExport:match('^DpsLabObservationExport = \"([0-9a-f]+)\"\\n$')",
            self.lua,
        )
        self.assertIn("DpsLabSyntheticObservationExportReason ~= SYNTHETIC_EXPORT_REASON", self.lua)
        self.assertIn("#candidate > 8192", self.lua)
        self.assertIn("#candidate % 2 ~= 0", self.lua)
        self.assertNotIn("_G.DpsLabObservationExport = DpsLabSyntheticObservationExport", self.lua)

    def test_clear_is_idempotent_and_does_not_touch_other_state(self) -> None:
        clear = re.search(r'if action == "clear" then(.*?)\n  end', self.handler, re.DOTALL)
        self.assertIsNotNone(clear)
        self.assertEqual(clear.group(1).count("_G.DpsLabObservationExport = nil"), 1)
        for token in ("DpsLabSyntheticGuidance", "DpsLabSyntheticExchange", "DpsLabSyntheticObservation"):
            self.assertNotIn(token, clear.group(1))

    def test_no_payload_logging_or_automatic_surface_is_added(self) -> None:
        print_lines = [line for line in self.lua.splitlines() if "print(" in line]
        for line in print_lines:
            self.assertNotIn("candidate", line)
            self.assertNotIn("DpsLabObservationExport", line)
            self.assertNotIn("DpsLabSyntheticObservationExport", line)
        for token in (
            "CreateFrame", "RegisterEvent", "C_Timer", "OnUpdate", "PLAYER_LOGIN",
            "PLAYER_LOGOUT", "ZONE_CHANGED", "COMBAT_LOG", "SendAddonMessage",
            "UnitName", "GetRealmName", "GetInventoryItem", "http", "socket",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token.lower(), self.lua.lower())


if __name__ == "__main__":
    unittest.main()
