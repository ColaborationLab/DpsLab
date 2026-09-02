import base64
import json
import tempfile
import unittest
from pathlib import Path

from dpslab.local_character_context_profile import (
    CharacterContextProfileError, CharacterContextProfileInput, clear_all_profiles,
    create_profile, delete_selected_profile, inspect_profile, replace_selected_profile,
)


class _Protector:
    def protect(self, value: bytes) -> bytes:
        return b"p:" + value[::-1]
    def unprotect(self, value: bytes) -> bytes:
        if not value.startswith(b"p:"):
            raise CharacterContextProfileError("character_context_profile_protection_failed")
        return value[2:][::-1]


class CharacterContextProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.protector = _Protector()
        self.value = CharacterContextProfileInput("Synthetic", "Example", 11, 104, "healer", 80, 4, "12345", "2026-09-01T00:00:00Z")

    def tearDown(self):
        self.temp.cleanup()

    def test_create_inspect_replace_delete_and_clear_are_explicit(self):
        created = create_profile(self.root, self.value, self.protector)
        self.assertEqual(created.state, "selected")
        self.assertEqual(inspect_profile(self.root, self.protector).context.display_name, "Synthetic")
        replaced = replace_selected_profile(self.root, created.profile_id, CharacterContextProfileInput("Synthetic", "Example", 11, 105, "damage", 80, 4, "12345", "2026-09-01T00:00:01Z"), self.protector)
        self.assertEqual(replaced.context.specialization_id, 105)
        delete_selected_profile(self.root, created.profile_id, self.protector)
        self.assertEqual(inspect_profile(self.root, self.protector).state, "absent")
        clear_all_profiles(self.root, "CLEAR_LOCAL_CHARACTER_CONTEXT_PROFILE")

    def test_input_and_clear_fail_closed(self):
        for value in (CharacterContextProfileInput("", "Example", 11, 104, "healer", 80, 4, "12345", "2026-09-01T00:00:00Z"), CharacterContextProfileInput("Synthetic", "Example", True, 104, "healer", 80, 4, "12345", "2026-09-01T00:00:00Z"), CharacterContextProfileInput("Synthetic", "Example", 11, 104, "unknown", 80, 4, "12345", "2026-09-01T00:00:00Z")):
            with self.assertRaises(CharacterContextProfileError):
                create_profile(self.root, value, self.protector)
        with self.assertRaises(CharacterContextProfileError):
            clear_all_profiles(self.root, "yes")

    def test_tampering_and_cross_profile_substitution_are_rejected(self):
        created = create_profile(self.root, self.value, self.protector)
        with self.assertRaises(CharacterContextProfileError):
            replace_selected_profile(self.root, "0" * 32, self.value, self.protector)
        target = self.root / "character_context_profile_0_1.json"
        envelope = json.loads(target.read_text(encoding="utf-8"))
        envelope["ciphertext_base64"] = base64.b64encode(b"wrong").decode("ascii")
        target.write_text(json.dumps(envelope, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        with self.assertRaises(CharacterContextProfileError):
            inspect_profile(self.root, self.protector)
        self.assertIsNotNone(created.profile_id)

    def test_non_directory_root_is_rejected_before_any_write(self):
        invalid_root = self.root / "not-a-directory"
        invalid_root.write_text("synthetic", encoding="utf-8")
        with self.assertRaises(CharacterContextProfileError):
            create_profile(invalid_root, self.value, self.protector)

    def test_raw_content_is_protected_and_errors_are_non_sensitive(self):
        create_profile(self.root, self.value, self.protector)
        content = (self.root / "character_context_profile_0_1.json").read_text(encoding="utf-8")
        self.assertNotIn("Synthetic", content)
        self.assertNotIn("Example", content)
        with self.assertRaises(CharacterContextProfileError) as caught:
            create_profile(self.root, self.value, self.protector)
        self.assertNotIn("Synthetic", str(caught.exception))
