from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests.strict_temporary_cleanup import strict_temporary_directory

from dpslab import ProfileParseError, parse_profile, parse_profile_text


FIXTURE = Path(__file__).parent / "fixtures" / "minimal_profile.simc"


class ProfileParserTests(unittest.TestCase):
    def test_parses_character_and_talents(self) -> None:
        snapshot = parse_profile(FIXTURE)

        self.assertEqual(snapshot.character.name, "Testmage")
        self.assertEqual(snapshot.character.character_class, "mage")
        self.assertEqual(snapshot.character.specialization, "frost")
        self.assertEqual(snapshot.character.realm, "testrealm")
        self.assertEqual(snapshot.character.level, 80)
        self.assertEqual(snapshot.character.role, "spell")
        self.assertEqual(
            snapshot.character.professions,
            {"tailoring": 75, "enchanting": 60},
        )
        self.assertEqual(snapshot.character.loot_spec, "arcane")
        self.assertEqual(snapshot.active_talent_hash, "ACTIVE_HASH")
        self.assertEqual(snapshot.saved_loadouts[0].name, "Raid")
        self.assertEqual(snapshot.saved_loadouts[0].talent_hash, "RAID_HASH")

    def test_parses_snapshot_provenance_and_checksum(self) -> None:
        snapshot = parse_profile(FIXTURE)

        self.assertEqual(snapshot.schema_version, "0.1")
        self.assertEqual(snapshot.source_file, "minimal_profile.simc")
        self.assertEqual(len(snapshot.source_sha256), 64)
        self.assertEqual(snapshot.simc_checksum, "fixture123")

    def test_loot_spec_and_checksum_are_optional(self) -> None:
        text = FIXTURE.read_text(encoding="utf-8")
        text = text.replace("# loot_spec=arcane\n", "").replace("# Checksum: fixture123\n", "")

        snapshot = parse_profile_text(text)

        self.assertIsNone(snapshot.character.loot_spec)
        self.assertIsNone(snapshot.simc_checksum)

    def test_separates_equipped_and_bag_gear(self) -> None:
        snapshot = parse_profile(FIXTURE)

        self.assertEqual(len(snapshot.equipped_gear), 1)
        self.assertEqual(snapshot.equipped_gear[0].name, "Test Helm")
        self.assertEqual(snapshot.equipped_gear[0].item_id, 100)
        self.assertEqual(snapshot.equipped_gear[0].attributes["bonus_id"], "1/2")
        self.assertEqual(len(snapshot.bag_gear), 1)
        self.assertEqual(snapshot.bag_gear[0].name, "Spare Helm")
        self.assertEqual(snapshot.bag_gear[0].item_level, 190)

    def test_rejects_non_simc_input(self) -> None:
        with strict_temporary_directory() as directory:
            html = directory / "profile.simc.html"
            html.write_text("<html></html>", encoding="utf-8")
            with self.assertRaisesRegex(ProfileParseError, r"\.simc"):
                parse_profile(html)

    def test_reports_missing_required_fields(self) -> None:
        with self.assertRaisesRegex(ProfileParseError, "Faltan campos obligatorios"):
            parse_profile_text('warlock="Incomplete"\n')

    def test_reports_invalid_item_id(self) -> None:
        text = FIXTURE.read_text(encoding="utf-8").replace("id=100", "id=invalid")
        with self.assertRaisesRegex(ProfileParseError, "id no numérico"):
            parse_profile_text(text)


if __name__ == "__main__":
    unittest.main()
