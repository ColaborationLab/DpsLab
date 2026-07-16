from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dpslab.deep_audit import (
    _comparison,
    canonical_damage_key,
    compare_profiles,
    extract_apl,
    extract_embedded_profile,
    extract_json_candidates,
    run_audit,
)


class DeepAuditTests(unittest.TestCase):
    def test_valid_embedded_json_and_braces_inside_strings(self) -> None:
        candidates = extract_json_candidates('<script>{"target":"x","data":{"label":"a } { b"}}</script>')
        self.assertEqual(len(candidates), 1)
        self.assertIsNone(candidates[0].error)
        self.assertEqual(candidates[0].value["data"]["label"], "a } { b")

    def test_javascript_object_is_parse_failed_without_execution(self) -> None:
        candidates = extract_json_candidates("<script>{target: 'x', data: dangerous()}</script>")
        self.assertEqual(len(candidates), 1)
        self.assertIsNotNone(candidates[0].error)
        self.assertIsNone(candidates[0].value)

    def test_embedded_profile_decodes_entities_and_br(self) -> None:
        lines = extract_embedded_profile('<p>warlock="Flasil"<br>actions=/spell,if=a&amp;b<br/>x=1</p>')
        self.assertEqual(lines, ['warlock="Flasil"', "actions=/spell,if=a&b", "x=1"])

    def test_profile_duplicates_and_crlf_lf(self) -> None:
        manual = 'a=1\r\na=2\r\n# c\r\n'.replace("\r\n", "\n").split("\n")
        formal = 'a=1\na=2\n# c\n'.split("\n")
        result = compare_profiles(manual, formal)
        self.assertTrue(result["exact_active_sequence_equal"])
        self.assertEqual(result["duplicate_keys"]["manual"]["a"], [1, 2])

    def test_comparison_status_and_relevance_are_independent(self) -> None:
        item = _comparison("x", 1, 2, manual_source="m", formal_source="f",
                           manual_locator="/m", formal_locator="/f", relevance="potentially_material")
        self.assertEqual(item.comparison_status, "different")
        self.assertEqual(item.relevance, "potentially_material")

    def test_not_exposed_is_unavailable_not_different(self) -> None:
        item = _comparison("x", None, 2, manual_source="m", formal_source="f",
                           manual_locator="/m", formal_locator="/f", manual_availability="not_exposed")
        self.assertEqual(item.comparison_status, "unavailable")

    def test_apl_complete_hash_and_partial_no_hash(self) -> None:
        lines = ["actions.precombat=flask", "actions=/spell", "actions+=/spell"]
        complete = extract_apl(lines, "profile", completeness="complete")
        partial = extract_apl(lines, "stdout", completeness="partial")
        self.assertIsNotNone(complete.normalized_sha256)
        self.assertIsNone(partial.normalized_sha256)
        self.assertEqual(complete.action_count, 3)
        self.assertTrue(complete.duplicates)

    def test_pet_mapping_by_ids_and_unmappable(self) -> None:
        key, confidence = canonical_damage_key({"owner_id": 1, "pet_id": 2, "action_id": 3})
        self.assertEqual((key, confidence), ("1/2/3", "high"))
        self.assertEqual(canonical_damage_key({"owner_name": "x"}), (None, "unmappable"))

    def test_full_audit_separates_options_and_atomically_writes_four_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manual = root / "manual.html"
            profile = root / "profiles" / "x.simc"
            run = root / "run"
            output = root / "audit"
            profile.parent.mkdir(); run.mkdir()
            manual.write_text('<p>warlock="Flasil"<br>actions=/spell</p>{"target":"actor1dps_sources","data":{}}', encoding="utf-8")
            profile.write_text('warlock="Flasil"\n', encoding="utf-8")
            simc = {"sim":{"options":{"threads":2,"fight_style":"Patchwerk","expected_iteration_time":1.0},"raid_events":[],"players":[{"name":"Flasil","stats":[],"stats_pets":{"imp":[{"name":"bolt","portion_amount":0.5,"id":4}]}}]}}
            (run / "simc.json").write_text(json.dumps(simc), encoding="utf-8")
            (run / "metadata.json").write_text("{}", encoding="utf-8")
            (run / "run_summary.json").write_text("{}", encoding="utf-8")
            (run / "stdout.txt").write_text("", encoding="utf-8")
            (run / "stderr.txt").write_text("", encoding="utf-8")
            real_replace = os.replace
            with patch("dpslab.deep_audit.os.replace", wraps=real_replace) as replace:
                run_audit(manual, profile, run, output)
            self.assertEqual(replace.call_count, 4)
            options = json.loads((output / "sim_options_diff.json").read_text(encoding="utf-8"))
            self.assertTrue(any(x["field"].endswith("fight_style") for x in options["input_configuration"]))
            self.assertTrue(any(x["field"].endswith("threads") for x in options["runtime_configuration"]))
            self.assertTrue(any(x["field"].endswith("expected_iteration_time") for x in options["derived_results"]))


if __name__ == "__main__":
    unittest.main()
