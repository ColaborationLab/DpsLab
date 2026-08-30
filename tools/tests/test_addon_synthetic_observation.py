import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OBSERVATION = ROOT / "addon" / "DpsLab" / "SyntheticObservation.lua"
TOC = ROOT / "addon" / "DpsLab" / "DpsLab.toc"


class AddonSyntheticObservationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = OBSERVATION.read_text(encoding="utf-8")

    def test_observation_loads_before_renderer_with_one_manual_export(self) -> None:
        lines = [line for line in TOC.read_text(encoding="utf-8").splitlines() if line and not line.startswith("##")]
        self.assertIn("SyntheticObservation.lua", lines)
        self.assertLess(lines.index("SyntheticObservation.lua"), lines.index("DpsLab.lua"))
        saved = [line for line in TOC.read_text(encoding="utf-8").splitlines() if line.startswith("## SavedVariables:")]
        self.assertEqual(saved, ["## SavedVariables: DpsLabObservationExport"])

    def test_closed_validator_covers_identity_subject_payload_and_safety(self) -> None:
        self.assertIn("function Observation.Validate(value)", self.text)
        for reason in (
            "observationFieldsInvalid", "observationSchemaIncompatible",
            "observationIdentityInvalid", "observationProducerUnsupported",
            "observationCompatibilityInvalid", "observationSubjectInvalid",
            "observationPayloadInvalid", "observationSignalsInvalid",
            "observationEventCountMismatch", "observationSafetyInvalid",
            "validSyntheticObservationNonActionable",
        ):
            self.assertIn(reason, self.text)

    def test_role_relevant_signals_are_bounded_and_self_consistent(self) -> None:
        for token in ("damage_events", "incoming_damage_events", "healing_events"):
            self.assertIn(token, self.text)
        self.assertIn("value == math.floor(value)", self.text)
        self.assertIn("value.observation.event_count, 0, 100000", self.text)
        self.assertIn("value.observation.byte_count, 1, 4096", self.text)
        self.assertIn("~= value.observation.event_count", self.text)

    def test_fixture_is_synthetic_private_and_non_actionable(self) -> None:
        for token in (
            'state = "synthetic_fixture"', "contains_personal_data = false",
            "executable = false", "actionable = false", "no_automation = true",
        ):
            self.assertIn(token, self.text)
        prohibited = (
            "SavedVariables", "character_name", "realm", "equipment", "talent",
            "loadstring", "http", "socket", "CastSpell", "SendChatMessage",
            "password", "credential", "telemetry",
        )
        for token in prohibited:
            with self.subTest(token=token):
                self.assertNotIn(token.lower(), self.text.lower())

    def test_timestamp_and_serialized_byte_count_are_fixed_for_the_fixture(self) -> None:
        self.assertIn('captured_at:match("^%d%d%d%d%-%d%d%-%d%dT%d%d:%d%d:%d%dZ$")', self.text)
        self.assertIn("byte_count = 706", self.text)


if __name__ == "__main__":
    unittest.main()
