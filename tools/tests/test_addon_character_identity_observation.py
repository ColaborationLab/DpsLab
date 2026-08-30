import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
IDENTITY = ROOT / "addon" / "DpsLab" / "CharacterIdentityObservation.lua"
RENDERER = ROOT / "addon" / "DpsLab" / "DpsLab.lua"
TOC = ROOT / "addon" / "DpsLab" / "DpsLab.toc"


class AddonCharacterIdentityObservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.identity = IDENTITY.read_text(encoding="utf-8")
        cls.renderer = RENDERER.read_text(encoding="utf-8")
        cls.toc = TOC.read_text(encoding="utf-8")

    def test_exact_attended_api_allowlist_is_declared(self):
        block = re.search(r"local API_NAMES = \{(.*?)\n\}", self.identity, re.DOTALL)
        self.assertIsNotNone(block)
        names = re.findall(r'"([A-Za-z]+)"', block.group(1))
        self.assertEqual(names, ["GetBuildInfo", "UnitClass", "GetSpecialization", "GetSpecializationInfo", "UnitLevel", "UnitRace", "GetServerTime"])

    def test_identity_module_loads_before_the_renderer(self):
        lines = self.toc.splitlines()
        self.assertLess(lines.index("CharacterIdentityObservation.lua"), lines.index("DpsLab.lua"))
        self.assertEqual([line for line in lines if line.startswith("## SavedVariables:")], ["## SavedVariables: DpsLabObservationExport"])

    def test_capture_is_manual_only_and_assigns_after_success(self):
        self.assertIn('role == "identity" and handleIdentityExport()', self.renderer)
        handler = re.search(r"local function handleIdentityExport\(\)(.*?)\nend", self.renderer, re.DOTALL).group(1)
        self.assertLess(handler.index("candidate == nil"), handler.index("_G.DpsLabObservationExport = candidate"))
        self.assertEqual(handler.count("_G.DpsLabObservationExport = candidate"), 1)
        self.assertNotRegex(self.identity + self.renderer, r"RegisterEvent|CreateFrame|C_Timer|OnUpdate")

    def test_closed_schema_and_safety_constants_are_serialized(self):
        for literal in ('"character_identity_snapshot"', '"manual_command"', '"retail"', '"0.1"', '"contains_character_data":true', '"contains_direct_identifiers":false', '"actionable":false', '"executable":false', '"no_automation":true'):
            self.assertIn(literal, self.identity)

    def test_roles_are_normalized_and_fail_closed(self):
        self.assertIn('DAMAGER = "damage"', self.identity)
        self.assertIn('TANK = "tank"', self.identity)
        self.assertIn('HEALER = "healer"', self.identity)
        self.assertIn('if candidate.role == nil then return nil, "identity_role_unsupported" end', self.identity)

    def test_all_numeric_values_are_bounded_before_serialization(self):
        for field in ("build", "interface_version", "class_id", "specialization_id", "level", "race_id", "captured_at"):
            self.assertRegex(self.identity, rf"{field}\s*=\s*boundedInteger")
        self.assertIn("value == math.floor(value)", self.identity)

    def test_transport_is_canonical_lowercase_hex_and_bounded(self):
        self.assertIn('string.format("%02x"', self.identity)
        self.assertIn("#payload > 4096", self.identity)
        self.assertIn("#encoded > 8192", self.identity)
        self.assertIn("#encoded % 2 ~= 0", self.identity)

    def test_failure_reasons_are_static_and_do_not_include_values(self):
        for reason in ("identity_api_unavailable", "identity_api_failed", "identity_context_invalid", "identity_role_unsupported", "identity_payload_invalid"):
            self.assertIn(reason, self.identity + self.renderer)
        self.assertNotRegex(self.identity, r"print\(|message\(|error\(")

    def test_prohibited_character_and_gameplay_fields_are_absent(self):
        lowered = self.identity.lower()
        for token in ("character_name", "realm", "guid", "account", "guild", "equipment", "item_id", "talent", "combat_event", "damage_events", "healing_events", "aura", "currency", "quest", "achievement"):
            self.assertNotIn(token, lowered)

    def test_no_network_execution_history_or_automation_surface(self):
        lowered = self.identity.lower()
        for token in ("http", "socket", "loadstring", "sendchatmessage", "savedvariables", "database", "history", "telemetry", "retry", "timer"):
            self.assertNotIn(token, lowered)


if __name__ == "__main__":
    unittest.main()
