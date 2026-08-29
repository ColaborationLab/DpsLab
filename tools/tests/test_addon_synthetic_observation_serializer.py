import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LUA = ROOT / "addon" / "DpsLab" / "SyntheticObservation.lua"


class AddonSyntheticObservationSerializerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = LUA.read_text(encoding="utf-8")

    def test_serializer_validates_before_emitting_exact_assignment(self) -> None:
        self.assertIn("function Observation.Serialize(value)", self.text)
        serialize = self.text[self.text.index("function Observation.Serialize(value)"):]
        self.assertLess(serialize.index("Observation.Validate(value)"), serialize.index("canonicalPayload(value)"))
        self.assertIn("#payload ~= value.observation.byte_count", serialize)
        self.assertIn("#payload > 4096", serialize)
        self.assertIn("DpsLabObservationExport", serialize)
        self.assertIn("validSyntheticObservationTransportNonActionable", serialize)

    def test_canonical_key_families_are_emitted_in_lexical_order(self) -> None:
        payload = self.text[self.text.index("local function canonicalPayload(value)"):self.text.index("local function lowerHex(value)")]
        positions = [payload.index(token) for token in (
            '"compatibility"', '"identity"', '"observation"',
            '"producer"', '"safety"', '"schema_version"', '"subject"',
        )]
        self.assertEqual(positions, sorted(positions))
        signal_positions = [payload.index(token) for token in (
            '"damage_events"', '"healing_events"', '"incoming_damage_events"',
        )]
        self.assertEqual(signal_positions, sorted(signal_positions))

    def test_hex_is_lowercase_two_digits_per_payload_byte(self) -> None:
        self.assertIn('string.format("%02x", string.byte(character))', self.text)
        self.assertIn('byte_count = 706', self.text)
        self.assertIn('DpsLabSyntheticObservationExportReason', self.text)

    def test_serializer_has_no_persistence_gameplay_or_network_surface(self) -> None:
        lower = self.text.lower()
        for prohibited in (
            "savedvariables", "loadstring", "dofile", "require(", "castspell",
            "sendchatmessage", "createframe", "http", "socket", "password",
            "credential", "telemetry",
        ):
            with self.subTest(prohibited=prohibited):
                self.assertNotIn(prohibited, lower)


if __name__ == "__main__":
    unittest.main()
