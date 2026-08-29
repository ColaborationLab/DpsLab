import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "addon" / "DpsLab" / "SyntheticGuidance.lua"
RENDERER = ROOT / "addon" / "DpsLab" / "DpsLab.lua"
TOC = ROOT / "addon" / "DpsLab" / "DpsLab.toc"


class AddonSyntheticGuidanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.package = PACKAGE.read_text(encoding="utf-8")
        self.renderer = RENDERER.read_text(encoding="utf-8")

    def test_package_is_loaded_before_renderer(self) -> None:
        lines = [line for line in TOC.read_text(encoding="utf-8").splitlines() if line and not line.startswith("##")]
        self.assertEqual(lines, ["SyntheticGuidance.lua", "SyntheticExchange.lua", "SyntheticObservation.lua", "DpsLab.lua"])

    def test_package_is_versioned_pending_review_and_non_actionable(self) -> None:
        for token in ('schema_version = "0.1"', 'state = "pending_review"', "no_automation = true", "actionable = false", 'degradation_policy = "fail_closed"'):
            self.assertIn(token, self.package)

    def test_all_three_roles_are_present_and_safety_first(self) -> None:
        for role in ("damage", "tank", "healer"):
            self.assertRegex(self.package, rf"\b{role}\s*=\s*{{")
        self.assertIn("survival, mitigation, threat", self.package)
        self.assertIn("ally survival, healing, dispels", self.package)

    def test_package_contains_no_real_or_executable_surface(self) -> None:
        prohibited = ("SavedVariables", "loadstring", "http", "CastSpell", "SendChatMessage", "patreon", "donate")
        for token in prohibited:
            self.assertNotIn(token.lower(), self.package.lower())
        self.assertLessEqual(len(re.findall(r"priority\s*=", self.package)), 3)

    def test_renderer_fails_closed_and_requires_explicit_synthetic_command(self) -> None:
        self.assertIn("function DpsLab.ValidatePackage(package, build, interfaceVersion, role)", self.renderer)
        for reason in ("package_fields_invalid", "schema_incompatible", "identity_invalid", "compatibility_invalid", "context_unknown", "context_incompatible", "lifecycle_invalid", "evidence_invalid", "safety_invalid", "role_unsupported", "guidance_invalid"):
            self.assertIn(reason, self.renderer)
        self.assertIn("#package.guidance[role].priority > 240", self.renderer)
        self.assertIn('return true, "validSyntheticNonActionable"', self.renderer)
        self.assertIn('command == "synthetic"', self.renderer)


if __name__ == "__main__":
    unittest.main()
