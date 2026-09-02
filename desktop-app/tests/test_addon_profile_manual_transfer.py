import tempfile
import unittest
from pathlib import Path

from dpslab.addon_character_identity_transport import CharacterIdentitySnapshot
from dpslab.addon_profile_manual_transfer import (
    CREATE_CONFIRMATION,
    PREVIEW_CONFIRMATION,
    REPLACE_CONFIRMATION,
    LocalDisplayIdentity,
    apply_manual_identity_transfer,
    preview_manual_identity_transfer,
)
from dpslab.local_character_context_profile import inspect_profile


class FakeProtector:
    def protect(self, value):
        return b"protected:" + value

    def unprotect(self, value):
        if not value.startswith(b"protected:"):
            raise ValueError("wrong_protector")
        return value[len(b"protected:"):]


def snapshot(captured_at=1_788_079_200, build=120500, interface_version=120500):
    return CharacterIdentitySnapshot(build, interface_version, 11, 123, "healer", 90, 1, captured_at)


def preview(captured_at=1_788_079_200):
    return preview_manual_identity_transfer(
        snapshot(captured_at), LocalDisplayIdentity("SyntheticName", "SyntheticRealm"),
        expected_build=120500, expected_interface_version=120500, now_epoch=1_788_079_300,
        confirmation=PREVIEW_CONFIRMATION,
    )


class AddonProfileManualTransferTests(unittest.TestCase):
    def test_confirmed_preview_and_create_retains_only_protected_profile(self):
        candidate = preview()
        self.assertEqual(("ready", None), (candidate.state, candidate.reason))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = apply_manual_identity_transfer(root, candidate, FakeProtector(), operation="create", confirmation=CREATE_CONFIRMATION)
            self.assertEqual(("created", None), (result.state, result.reason))
            stored = inspect_profile(root, FakeProtector())
            self.assertEqual(("selected", result.profile_id, "SyntheticName", "SyntheticRealm"), (stored.state, stored.profile_id, stored.context.display_name, stored.context.realm))

    def test_replace_requires_exact_selected_profile_identifier(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = apply_manual_identity_transfer(root, preview(), FakeProtector(), operation="create", confirmation=CREATE_CONFIRMATION)
            denied = apply_manual_identity_transfer(root, preview(1_788_079_250), FakeProtector(), operation="replace", confirmation=REPLACE_CONFIRMATION, selected_profile_id="0" * 32)
            self.assertEqual(("rejected", "profile_mismatch", None), (denied.state, denied.reason, denied.profile_id))
            replaced = apply_manual_identity_transfer(root, preview(1_788_079_250), FakeProtector(), operation="replace", confirmation=REPLACE_CONFIRMATION, selected_profile_id=first.profile_id)
            self.assertEqual(("replaced", None, first.profile_id), (replaced.state, replaced.reason, replaced.profile_id))

    def test_missing_confirmations_never_create_a_profile(self):
        denied = preview_manual_identity_transfer(snapshot(), LocalDisplayIdentity("SyntheticName", "SyntheticRealm"), expected_build=120500, expected_interface_version=120500, now_epoch=1_788_079_300, confirmation="no")
        self.assertEqual(("rejected", "consent_required", None), (denied.state, denied.reason, denied.context))
        with tempfile.TemporaryDirectory() as directory:
            result = apply_manual_identity_transfer(Path(directory), preview(), FakeProtector(), operation="create", confirmation="no")
            self.assertEqual(("rejected", "create_confirmation_required", None), (result.state, result.reason, result.profile_id))
            self.assertEqual("absent", inspect_profile(Path(directory), FakeProtector()).state)

    def test_stale_future_and_incompatible_snapshots_fail_closed(self):
        cases = (
            (snapshot(1_788_078_000), 120500, 120500, "transport_stale"),
            (snapshot(1_788_079_301), 120500, 120500, "transport_from_future"),
            (snapshot(), 120501, 120500, "compatibility_unavailable"),
            (snapshot(), 120500, 120501, "compatibility_unavailable"),
        )
        for value, build, interface, reason in cases:
            with self.subTest(reason=reason):
                result = preview_manual_identity_transfer(value, LocalDisplayIdentity("SyntheticName", "SyntheticRealm"), expected_build=build, expected_interface_version=interface, now_epoch=1_788_079_300, confirmation=PREVIEW_CONFIRMATION)
                self.assertEqual(("rejected", reason, None), (result.state, result.reason, result.context))

    def test_invalid_display_source_and_operation_are_bounded(self):
        invalid = preview_manual_identity_transfer(snapshot(), LocalDisplayIdentity("", "SyntheticRealm"), expected_build=120500, expected_interface_version=120500, now_epoch=1_788_079_300, confirmation=PREVIEW_CONFIRMATION)
        self.assertEqual(("rejected", "display_identity_invalid", None), (invalid.state, invalid.reason, invalid.context))
        source = preview_manual_identity_transfer(object(), LocalDisplayIdentity("SyntheticName", "SyntheticRealm"), expected_build=120500, expected_interface_version=120500, now_epoch=1_788_079_300, confirmation=PREVIEW_CONFIRMATION)
        self.assertEqual(("rejected", "source_invalid", None), (source.state, source.reason, source.context))
        with tempfile.TemporaryDirectory() as directory:
            result = apply_manual_identity_transfer(Path(directory), preview(), FakeProtector(), operation="automatic", confirmation=CREATE_CONFIRMATION)
            self.assertEqual(("rejected", "operation_invalid", None), (result.state, result.reason, result.profile_id))


if __name__ == "__main__":
    unittest.main()
