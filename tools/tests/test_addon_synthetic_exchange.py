import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXCHANGE = ROOT / "addon" / "DpsLab" / "SyntheticExchange.lua"
TOC = ROOT / "addon" / "DpsLab" / "DpsLab.toc"


class AddonSyntheticExchangeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = EXCHANGE.read_text(encoding="utf-8")

    def test_exchange_loads_after_guidance_and_before_renderer(self) -> None:
        lines = [line for line in TOC.read_text(encoding="utf-8").splitlines() if line and not line.startswith("##")]
        self.assertEqual(lines, ["SyntheticGuidance.lua", "SyntheticExchange.lua", "DpsLab.lua"])

    def test_envelope_is_closed_versioned_and_non_actionable(self) -> None:
        self.assertIn("function Exchange.Validate(value)", self.text)
        self.assertIn('schema_version = "0.1"', self.text)
        self.assertIn("synthetic = true", self.text)
        self.assertIn("executable = false", self.text)
        self.assertIn("contains_credentials = false", self.text)
        self.assertIn("actionable = false", self.text)

    def test_validator_has_identity_integrity_and_bounds(self) -> None:
        for token in ("envelopeFieldsInvalid", "schemaIncompatible", "identityInvalid", "producerUnsupported", "compatibilityInvalid", "payloadInvalid", "integrityInvalid", "safetyInvalid"):
            self.assertIn(token, self.text)
        self.assertIn("value.payload.role_count > 3", self.text)
        self.assertIn("value.payload.byte_count > 8192", self.text)
        self.assertIn('#value == 64', self.text)
        self.assertIn('value:match("^[0-9a-f]+$")', self.text)

    def test_exchange_contains_no_real_input_or_execution_surface(self) -> None:
        prohibited = ("SavedVariables", "loadstring", "http", "socket", "CastSpell", "SendChatMessage", "password", "token", "character_name", "realm")
        lower = self.text.lower()
        for token in prohibited:
            with self.subTest(token=token):
                self.assertNotIn(token.lower(), lower)


if __name__ == "__main__":
    unittest.main()
