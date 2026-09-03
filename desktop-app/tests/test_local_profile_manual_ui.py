import tempfile
import unittest
from pathlib import Path

from dpslab.addon_character_identity_transport import CharacterIdentitySnapshot
from dpslab.addon_profile_manual_transfer import CREATE_CONFIRMATION, PREVIEW_CONFIRMATION, REPLACE_CONFIRMATION
from dpslab.local_character_context_profile import CharacterContextProfileInput, create_profile, inspect_profile
from dpslab.local_profile_manual_ui import (
    CLEAR_CONFIRMATION,
    DELETE_CONFIRMATION,
    LocalProfileManualController,
)


class FakeProtector:
    def protect(self, value):
        return b"protected:" + value

    def unprotect(self, value):
        if not value.startswith(b"protected:"):
            raise ValueError("wrong_protector")
        return value[len(b"protected:"):]


def synthetic_snapshot():
    return CharacterIdentitySnapshot(120500, 120500, 11, 123, "healer", 90, 1, 1_788_079_200)


def controller(root, supplier=synthetic_snapshot):
    return LocalProfileManualController(
        root, FakeProtector(), expected_build=120500, expected_interface_version=120500,
        now_epoch=lambda: 1_788_079_300, snapshot_supplier=supplier,
    )


class LocalProfileManualUiTests(unittest.TestCase):
    def test_absent_profile_is_bounded_and_has_no_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            state = controller(Path(directory)).inspect()
        self.assertEqual(("no_selected_profile", None, None, None, False), (state.state, state.reason, state.display_name, state.realm, state.can_delete))

    def test_selected_profile_exposes_only_local_display_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_profile(root, CharacterContextProfileInput("SyntheticName", "SyntheticRealm", 11, 123, "healer", 90, 1, "120500", "2026-09-02T00:00:00Z"), FakeProtector())
            state = controller(root).inspect()
        self.assertEqual(("selected_profile_available", "SyntheticName", "SyntheticRealm", True), (state.state, state.display_name, state.realm, state.can_delete))
        self.assertNotIn("profile_id", state.__dataclass_fields__)

    def test_preview_requires_explicit_consent_and_a_supplier(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            denied = controller(root).preview("SyntheticName", "SyntheticRealm", "no")
            unavailable = controller(root, supplier=None).preview("SyntheticName", "SyntheticRealm", PREVIEW_CONFIRMATION)
        self.assertEqual(("preview_unavailable", "consent_required"), (denied.state, denied.reason))
        self.assertEqual(("preview_unavailable", "source_unavailable"), (unavailable.state, unavailable.reason))

    def test_preview_then_create_requires_its_own_confirmation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            value = controller(root)
            self.assertEqual("preview_ready", value.preview("SyntheticName", "SyntheticRealm", PREVIEW_CONFIRMATION).state)
            denied = value.create("no")
            created = value.create(CREATE_CONFIRMATION)
            stored = inspect_profile(root, FakeProtector())
        self.assertEqual(("action_rejected", "create_confirmation_required"), (denied.state, denied.reason))
        self.assertEqual(("selected_profile_available", "SyntheticName"), (created.state, stored.context.display_name))

    def test_selected_profile_uses_replace_not_create(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            value = controller(root)
            value.inspect()
            value.preview("SyntheticName", "SyntheticRealm", PREVIEW_CONFIRMATION)
            value.create(CREATE_CONFIRMATION)
            value.preview("Replacement", "SyntheticRealm", PREVIEW_CONFIRMATION)
            replaced = value.replace(REPLACE_CONFIRMATION)
            stored = inspect_profile(root, FakeProtector())
        self.assertEqual(("selected_profile_available", "Replacement", "Replacement"), (replaced.state, replaced.display_name, stored.context.display_name))

    def test_delete_and_clear_require_separate_destructive_confirmations(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            value = controller(root)
            value.preview("SyntheticName", "SyntheticRealm", PREVIEW_CONFIRMATION)
            value.create(CREATE_CONFIRMATION)
            denied = value.delete("no")
            deleted = value.delete(DELETE_CONFIRMATION)
            clear_denied = value.clear_all("no")
            cleared = value.clear_all(CLEAR_CONFIRMATION)
        self.assertEqual(("action_rejected", "delete_confirmation_required"), (denied.state, denied.reason))
        self.assertEqual("no_selected_profile", deleted.state)
        self.assertEqual(("action_rejected", "clear_confirmation_required"), (clear_denied.state, clear_denied.reason))
        self.assertEqual("no_selected_profile", cleared.state)

    def test_visible_adapter_keeps_confirmation_and_action_state_boundaries(self):
        source = Path(__file__).parents[1] / "src" / "dpslab" / "local_profile_manual_ui.py"
        text = source.read_text(encoding="utf-8")
        self.assertIn("askyesno", text)
        self.assertIn("_update_actions", text)
        self.assertIn('else "disabled"', text)


if __name__ == "__main__":
    unittest.main()
