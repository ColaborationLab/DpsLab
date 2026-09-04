import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "addon" / "DpsLab" / "CharacterSpecializationRegistryObservation.lua"
RENDERER = ROOT / "addon" / "DpsLab" / "DpsLab.lua"
TOC = ROOT / "addon" / "DpsLab" / "DpsLab.toc"


class AddonSpecializationRegistryObservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = REGISTRY.read_text(encoding="utf-8")
        cls.renderer = RENDERER.read_text(encoding="utf-8")
        cls.toc = TOC.read_text(encoding="utf-8")

    def test_exact_attended_api_allowlist_is_declared(self):
        block = re.search(r"local API_NAMES = \{(.*?)\n\}", self.registry, re.DOTALL)
        self.assertIsNotNone(block)
        self.assertEqual(
            re.findall(r'"([A-Za-z]+)"', block.group(1)),
            ["GetBuildInfo", "UnitClass", "UnitSex", "GetNumSpecializationsForClassID", "GetSpecializationInfoForClassID", "GetServerTime"],
        )

    def test_registry_module_loads_after_identity_and_before_renderer(self):
        lines = self.toc.splitlines()
        self.assertLess(lines.index("CharacterIdentityObservation.lua"), lines.index(REGISTRY.name))
        self.assertLess(lines.index(REGISTRY.name), lines.index("DpsLab.lua"))
        self.assertEqual([line for line in lines if line.startswith("## SavedVariables:")], ["## SavedVariables: DpsLabObservationExport"])

    def test_capture_is_manual_only_and_assigns_after_success(self):
        self.assertIn('role == "specialization-registry" and handleSpecializationRegistryExport()', self.renderer)
        handler = re.search(r"local function handleSpecializationRegistryExport\(\)(.*?)\nend", self.renderer, re.DOTALL).group(1)
        self.assertLess(handler.index("candidate == nil"), handler.index("_G.DpsLabObservationExport = candidate"))
        self.assertEqual(handler.count("_G.DpsLabObservationExport = candidate"), 1)
        self.assertNotRegex(self.registry + self.renderer, r"RegisterEvent|C_Timer|OnUpdate")

    def test_closed_schema_and_safety_constants_are_serialized(self):
        for literal in ('"class_specialization_registry_snapshot"', '"manual_command"', '"retail"', '"0.1"', '"contains_character_data":true', '"contains_direct_identifiers":false', '"actionable":false', '"executable":false', '"no_automation":true'):
            self.assertIn(literal, self.registry)

    def test_exact_four_role_shape_and_unique_ids_fail_closed(self):
        self.assertIn('if count ~= 4 then return nil, "registry_shape_unsupported" end', self.registry)
        self.assertIn("seen[specializationId]", self.registry)
        self.assertIn("roleCounts.damage ~= 2", self.registry)
        self.assertIn("roleCounts.tank ~= 1", self.registry)
        self.assertIn("roleCounts.healer ~= 1", self.registry)

    def test_numeric_values_are_bounded_before_serialization(self):
        for field in ("build", "interface_version", "class_id", "captured_at"):
            self.assertRegex(self.registry, rf"{field}\s*=\s*(?:classId|boundedInteger)")
        self.assertRegex(self.registry, r"specializationId\s*=\s*boundedInteger")
        self.assertIn("value == math.floor(value)", self.registry)

    def test_transport_is_canonical_lowercase_hex_and_bounded(self):
        self.assertIn('string.format("%02x"', self.registry)
        self.assertIn("#payload > 4096", self.registry)
        self.assertIn("#encoded > 8192", self.registry)
        self.assertIn("#encoded % 2 ~= 0", self.registry)

    def test_failure_reasons_are_static_and_do_not_include_values(self):
        for reason in ("registry_api_unavailable", "registry_api_failed", "registry_context_invalid", "registry_shape_unsupported", "registry_role_unsupported", "registry_payload_invalid"):
            self.assertIn(reason, self.registry + self.renderer)
        self.assertNotRegex(self.registry, r"print\(|message\(|error\(")

    def test_prohibited_data_and_automation_surfaces_are_absent(self):
        lowered = self.registry.lower()
        for token in ("character_name", "realm", "guid", "account", "guild", "equipment", "item_id", "talent", "spell", "combat_event", "damage_events", "healing_events", "http", "socket", "loadstring", "sendchatmessage", "database", "history", "telemetry", "retry", "timer"):
            self.assertNotIn(token, lowered)


if __name__ == "__main__":
    unittest.main()
