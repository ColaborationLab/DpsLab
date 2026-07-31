import copy, json
from pathlib import Path
import unittest

from dpslab.patch_evidence import validate_patch_evidence
from dpslab.patch_format_adapter import (PatchFormatError,
    calculate_input_sha256, canonical_input_bytes, convert_structured_patch,
    validate_structured_patch_input)

ROOT=Path(__file__).parents[2]
FIXTURE=ROOT/"knowledge/snapshots/structured_patch_input_synthetic_0_1.json"
MAPPING={"synthetic.damage.coefficient":"synthetic.role.damage","synthetic.safety":"synthetic.role.safety"}

def rehash(value): value["integrity"]["input_sha256"]=calculate_input_sha256(value); return value

class PatchFormatAdapterTests(unittest.TestCase):
    def setUp(self): self.value=json.loads(FIXTURE.read_text(encoding="utf-8"))
    def mutate(self,path,content):
        value=copy.deepcopy(self.value); target=value
        for part in path[:-1]: target=target[part]
        target[path[-1]]=content; return rehash(value)
    def test_fixture_canonical_and_valid(self): self.assertEqual(FIXTURE.read_bytes(),canonical_input_bytes(validate_structured_patch_input(self.value)))
    def test_hash_projection(self):
        value=copy.deepcopy(self.value); value["integrity"]["input_sha256"]="f"*64
        self.assertEqual(calculate_input_sha256(value),calculate_input_sha256(self.value))
    def test_wrong_hash_rejected(self):
        value=copy.deepcopy(self.value); value["integrity"]["input_sha256"]="f"*64
        with self.assertRaises(PatchFormatError): validate_structured_patch_input(value)
    def test_root_closed(self):
        value=copy.deepcopy(self.value); value["extra"]=True
        with self.assertRaises(PatchFormatError): validate_structured_patch_input(value)
    def test_identity_closed(self):
        value=copy.deepcopy(self.value); value["identity"]["extra"]=True
        with self.assertRaises(PatchFormatError): validate_structured_patch_input(value)
    def test_source_closed(self):
        value=copy.deepcopy(self.value); value["source"]["extra"]=True
        with self.assertRaises(PatchFormatError): validate_structured_patch_input(value)
    def test_change_closed(self):
        value=copy.deepcopy(self.value); value["changes"][0]["extra"]=True
        with self.assertRaises(PatchFormatError): validate_structured_patch_input(value)
    def test_schema_rejected(self):
        with self.assertRaises(PatchFormatError): validate_structured_patch_input(self.mutate(["schema_version"],"0.2"))
    def test_lifecycle_rejected(self):
        with self.assertRaises(PatchFormatError): validate_structured_patch_input(self.mutate(["identity","lifecycle"],"future"))
    def test_timestamps_rejected(self):
        for path in (["identity","created_at"],["source","published_at"],["source","captured_at"]):
            with self.assertRaises(PatchFormatError): validate_structured_patch_input(self.mutate(path,"not-a-time"))
    def test_timestamp_order_rejected(self):
        with self.assertRaises(PatchFormatError): validate_structured_patch_input(self.mutate(["source","captured_at"],"2026-07-31T14:00:00Z"))
    def test_self_supersession_rejected(self):
        with self.assertRaises(PatchFormatError): validate_structured_patch_input(self.mutate(["source","supersedes_evidence_id"],"synthetic.structured.patch.1"))
    def test_source_media_policy_rejected(self):
        with self.assertRaises(PatchFormatError): validate_structured_patch_input(self.mutate(["source","media_type"],"text/html"))
    def test_source_acquisition_policy_rejected(self):
        with self.assertRaises(PatchFormatError): validate_structured_patch_input(self.mutate(["source","acquisition_class"],"scraped"))
    def test_source_license_and_authenticity_rejected(self):
        for field in ("license_class","authenticity_class"):
            with self.assertRaises(PatchFormatError): validate_structured_patch_input(self.mutate(["source",field],"unknown"))
    def test_product_rejected(self):
        with self.assertRaises(PatchFormatError): validate_structured_patch_input(self.mutate(["source","wow_product"],"classic"))
    def test_content_hash_rejected(self):
        with self.assertRaises(PatchFormatError): validate_structured_patch_input(self.mutate(["source","content_sha256"],"bad"))
    def test_bool_range_rejected(self):
        with self.assertRaises(PatchFormatError): validate_structured_patch_input(self.mutate(["source","build_min"],True))
    def test_reversed_range_rejected(self):
        with self.assertRaises(PatchFormatError): validate_structured_patch_input(self.mutate(["source","build_min"],120501))
    def test_changes_must_be_list(self):
        with self.assertRaises(PatchFormatError): validate_structured_patch_input(self.mutate(["changes"],{}))
    def test_duplicate_change_id_rejected(self):
        value=copy.deepcopy(self.value); value["changes"].append(copy.deepcopy(value["changes"][0]))
        with self.assertRaises(PatchFormatError): validate_structured_patch_input(rehash(value))
    def test_conflicting_target_rejected(self):
        value=copy.deepcopy(self.value); other=copy.deepcopy(value["changes"][0]); other["change_id"]="other"; value["changes"].append(other)
        with self.assertRaises(PatchFormatError): validate_structured_patch_input(rehash(value))
    def test_operation_rejected(self):
        with self.assertRaises(PatchFormatError): validate_structured_patch_input(self.mutate(["changes",0,"operation"],"approve"))
    def test_subject_list_rejected(self):
        for content in ([],"class.synthetic",[None]):
            with self.assertRaises(PatchFormatError): validate_structured_patch_input(self.mutate(["changes",0,"subject_tokens"],content))
    def test_certainty_rejected(self):
        with self.assertRaises(PatchFormatError): validate_structured_patch_input(self.mutate(["changes",0,"certainty"],"guessed"))
    def test_invalidation_list_rejected(self):
        with self.assertRaises(PatchFormatError): validate_structured_patch_input(self.mutate(["changes",0,"invalidation_kinds"],"kind"))
    def test_conversion_validates_as_patch_evidence(self): self.assertEqual("0.1",validate_patch_evidence(convert_structured_patch(self.value,MAPPING))["schema_version"])
    def test_mapping_controls_family(self): self.assertEqual("synthetic.role.damage",convert_structured_patch(self.value,MAPPING)["assertions"][0]["parameter_family_id"])
    def test_unknown_kind_rejected(self):
        with self.assertRaisesRegex(PatchFormatError,"unknown"): convert_structured_patch(self.value,{"other":"family.other"})
    def test_empty_mapping_rejected(self):
        with self.assertRaises(PatchFormatError): convert_structured_patch(self.value,{})
    def test_invalid_mapping_token_rejected(self):
        with self.assertRaises(PatchFormatError): convert_structured_patch(self.value,{"Bad Kind":"family"})
    def test_ambiguous_change_rejected(self):
        with self.assertRaisesRegex(PatchFormatError,"ambiguous"): convert_structured_patch(self.mutate(["changes",0,"certainty"],"ambiguous"),MAPPING)
    def test_unknown_invalidation_rejected(self):
        value=self.mutate(["changes",0,"invalidation_kinds"],["synthetic.unknown"])
        with self.assertRaises(PatchFormatError): convert_structured_patch(value,MAPPING)
    def test_invalidation_is_mapped(self):
        value=self.mutate(["changes",0,"invalidation_kinds"],["synthetic.safety"])
        self.assertEqual(["synthetic.role.safety"],convert_structured_patch(value,MAPPING)["assertions"][0]["invalidation_families"])
    def test_output_order_is_deterministic(self):
        value=copy.deepcopy(self.value); other=copy.deepcopy(value["changes"][0]); other["change_id"]="a-change"; other["semantic_kind"]="synthetic.safety"; other["subject_tokens"]=["spec.other"] ; value["changes"].append(other); rehash(value)
        self.assertEqual(["a-change","synthetic-change-1"],[x["assertion_id"] for x in convert_structured_patch(value,MAPPING)["assertions"]])
    def test_subject_order_is_canonical(self): self.assertEqual(["class.synthetic","spec.synthetic"],convert_structured_patch(self.value,MAPPING)["assertions"][0]["subject_tokens"])
    def test_historical_lifecycle_preserved(self):
        value=self.mutate(["identity","lifecycle"],"historical")
        self.assertEqual("historical",convert_structured_patch(value,MAPPING)["identity"]["lifecycle"])
    def test_empty_changes_produce_valid_empty_evidence(self):
        self.assertEqual([],convert_structured_patch(self.mutate(["changes"],[]),MAPPING)["assertions"])
    def test_fixture_has_no_real_or_prose_sources(self):
        text=FIXTURE.read_text().lower()
        for forbidden in ("http://","https://","battle.net","blizzard","wowhead","description","markdown","html"):
            self.assertNotIn(forbidden,text)

if __name__=="__main__": unittest.main()
