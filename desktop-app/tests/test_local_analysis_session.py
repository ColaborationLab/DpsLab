import unittest

from dpslab.local_analysis_session import (
    AnalysisCompatibility,
    AnalysisItem,
    MAX_SELECTED_CANDIDATES,
    VirtualVariant,
    build_local_analysis_session,
)


def compatibility():
    return AnalysisCompatibility("retail", 120500, 120500, "current-test")


def equipped():
    return (AnalysisItem("equipped-head", 1, "head", "equipped", True),)


def candidate(key="candidate-head", item_id=2, current_expansion=True):
    return AnalysisItem(key, item_id, "head", "designated_bag", current_expansion)


class LocalAnalysisSessionTests(unittest.TestCase):
    def build(self, candidates=(candidate(),), variants=()):
        return build_local_analysis_session(
            compatibility(), "damage", "open_world", equipped(), candidates, variants
        )

    def test_valid_selected_current_expansion_candidate_is_ephemeral(self):
        result = self.build(variants=(VirtualVariant("gem-head", "candidate-head", "gem", True),))
        self.assertEqual(("session_ready", None), (result.state, result.reason))
        self.assertEqual("designated_bag", result.session.selected_candidates[0].source)
        self.assertTrue(result.session.virtual_variants[0].hypothetical)
        self.assertNotIn("path", result.session.__dataclass_fields__)
        self.assertNotIn("history", result.session.__dataclass_fields__)

    def test_missing_or_untrusted_compatibility_fails_closed(self):
        result = build_local_analysis_session(None, "damage", "open_world", equipped(), (candidate(),), ())
        boolean = build_local_analysis_session(
            AnalysisCompatibility("retail", True, 120500, "current-test"),
            "damage", "open_world", equipped(), (candidate(),), (),
        )
        self.assertEqual("compatibility_unavailable", result.reason)
        self.assertEqual("compatibility_unavailable", boolean.reason)

    def test_duplicate_item_identity_and_old_expansion_candidate_are_rejected(self):
        duplicate = self.build(candidates=(candidate(), candidate()))
        old = self.build(candidates=(candidate(current_expansion=False),))
        self.assertEqual("analysis_items_invalid", duplicate.reason)
        self.assertEqual("analysis_items_invalid", old.reason)

    def test_candidate_must_map_to_an_equipped_slot(self):
        invalid = AnalysisItem("candidate-ring", 2, "ring", "designated_bag", True)
        self.assertEqual("analysis_slot_invalid", self.build(candidates=(invalid,)).reason)

    def test_virtual_variant_targets_only_selected_candidate_copy(self):
        invalid = self.build(variants=(VirtualVariant("gem-equipped", "equipped-head", "gem", True),))
        valid = self.build(variants=(VirtualVariant("gem-head", "candidate-head", "gem", True),))
        self.assertEqual("analysis_variants_invalid", invalid.reason)
        self.assertEqual("candidate-head", valid.session.virtual_variants[0].target_item_key)
        self.assertEqual("equipped-head", valid.session.equipped_items[0].item_key)

    def test_candidate_capacity_and_variant_flags_are_bounded(self):
        candidates = tuple(candidate(f"candidate-{index}", index + 2) for index in range(MAX_SELECTED_CANDIDATES + 1))
        excess = self.build(candidates=candidates)
        non_hypothetical = self.build(variants=(VirtualVariant("real-gem", "candidate-head", "gem", False),))
        self.assertEqual("analysis_items_invalid", excess.reason)
        self.assertEqual("analysis_variants_invalid", non_hypothetical.reason)

    def test_module_has_no_filesystem_process_or_network_imports(self):
        source = (__import__("pathlib").Path(__file__).parents[1] / "src" / "dpslab" / "local_analysis_session.py").read_text(encoding="utf-8")
        for forbidden in ("import os", "import pathlib", "import socket", "import subprocess", "open("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
