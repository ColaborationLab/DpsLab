import copy,hashlib,json
from pathlib import Path
import unittest
from dpslab.blizzard_patch_notes_extractor import BlizzardPatchNotesExtractorError,calculate_extraction_sha256,canonical_extraction_bytes,extract_patch_notes,validate_extraction
from dpslab.official_source_receipt import calculate_receipt_sha256
ROOT=Path(__file__).parents[2];HTML=ROOT/"knowledge/fixtures/blizzard_patch_notes_synthetic_0_1.html";SNAPSHOT=ROOT/"knowledge/snapshots/blizzard_patch_notes_extraction_synthetic_0_1.json"
SUBJECTS={("synthetic_class","synthetic_spec"):("class.synthetic","spec.synthetic")};FAMILIES={"synthetic_ability":"synthetic.role.damage"}
def receipt_for(body,status="captured_pending_review"):
 value={"schema_version":"0.1","identity":{"receipt_id":"synthetic.receipt.001","captured_at":"2026-08-01T20:00:00Z"},"source":{"source_id":"blizzard.wow.content_update_notes","final_host":"worldofwarcraft.blizzard.com","media_type":"text/html"},"capture":{"transport_status":"response_quarantined_pending_capture_validation","capture_status":status,"complete":True,"byte_count":len(body),"content_sha256":hashlib.sha256(body).hexdigest(),"etag":'"s1"',"last_modified":None,"reused_previous":status!="captured_pending_review"},"integrity":{"hash_algorithm":"sha256","receipt_sha256":""}}
 value["integrity"]["receipt_sha256"]=calculate_receipt_sha256(value);return value
class ExtractorTests(unittest.TestCase):
 def setUp(self):self.body=HTML.read_bytes();self.receipt=receipt_for(self.body)
 def extract(self,body=None,receipt=None,subjects=SUBJECTS,families=FAMILIES):
  selected_body=self.body if body is None else body
  selected_receipt=self.receipt if receipt is None else receipt
  return extract_patch_notes(selected_body,selected_receipt,"synthetic.extraction.001",subjects,families)
 def test_fixture_matches_snapshot(self):self.assertEqual(SNAPSHOT.read_bytes(),canonical_extraction_bytes(self.extract()))
 def test_output_is_pending_review(self):self.assertEqual("pending_review",self.extract()["identity"]["status"])
 def test_output_is_deterministic(self):self.assertEqual(self.extract(),self.extract())
 def test_hash_binding_rejected(self):
  altered=self.body.replace(b"changed",b"changed twice")
  with self.assertRaisesRegex(BlizzardPatchNotesExtractorError,"binding_mismatch"):self.extract(altered)
 def test_size_binding_rejected(self):
  receipt=copy.deepcopy(self.receipt);receipt["capture"]["byte_count"]+=1;receipt["integrity"]["receipt_sha256"]=calculate_receipt_sha256(receipt)
  with self.assertRaisesRegex(BlizzardPatchNotesExtractorError,"binding_mismatch"):self.extract(receipt=receipt)
 def test_nonbytes_and_empty_rejected(self):
  for value in ("text",b""):
   with self.assertRaises(BlizzardPatchNotesExtractorError):extract_patch_notes(value,self.receipt,"synthetic.extraction.001",SUBJECTS,FAMILIES)
 def test_non_utf8_rejected(self):
  body=b"\xff";receipt=receipt_for(body)
  with self.assertRaisesRegex(BlizzardPatchNotesExtractorError,"utf8"):self.extract(body,receipt)
 def test_nonpending_receipt_rejected(self):
  receipt=receipt_for(self.body,"duplicate")
  with self.assertRaisesRegex(BlizzardPatchNotesExtractorError,"receipt_status"):self.extract(receipt=receipt)
 def test_unsupported_tag_rejected(self):self.assert_parse_rejected(self.body.replace(b"<ul>",b"<script>"),"tag_unsupported")
 def test_unknown_attribute_rejected(self):self.assert_parse_rejected(self.body.replace(b"data-build=",b"class=\"x\" data-build="),"attribute_unsupported")
 def test_unknown_subject_mapping_rejected(self):
  with self.assertRaisesRegex(BlizzardPatchNotesExtractorError,"mapping_unavailable"):self.extract(subjects={})
 def test_unknown_family_mapping_rejected(self):
  with self.assertRaisesRegex(BlizzardPatchNotesExtractorError,"mapping_unavailable"):self.extract(families={})
 def test_bad_nesting_rejected(self):self.assert_parse_rejected(self.body.replace(b"</h2>",b"</h3>"),"nesting_invalid")
 def test_missing_build_rejected(self):self.assert_parse_rejected(self.body.replace(b" data-build=\"120500\"",b""),"article_invalid")
 def test_invalid_operation_rejected(self):self.assert_parse_rejected(self.body.replace(b'data-operation="change"',b'data-operation="guess"'),"operation_invalid")
 def test_equal_old_new_rejected(self):self.assert_parse_rejected(self.body.replace(b'pct_12',b'pct_10'),"value_semantics_invalid")
 def test_duplicate_family_conflict_rejected(self):
  item=b'<li data-ability="synthetic_ability" data-operation="change" data-old="pct_12" data-new="pct_14">Other synthetic text.</li>'
  self.assert_parse_rejected(self.body.replace(b"</ul>",item+b"</ul>"),"assertion_conflict")
 def test_node_limit_rejected(self):self.assert_parse_rejected(self.body.replace(b"</ul>",b"<ul>"*129+b"</ul>"),"parser_limit")
 def test_output_contains_no_html_or_prose(self):
  text=json.dumps(self.extract());self.assertNotIn("<article",text);self.assertNotIn("Synthetic ability changed",text)
 def test_snapshot_hash_validates(self):self.assertEqual(self.extract(),validate_extraction(json.loads(SNAPSHOT.read_text())))
 def assert_parse_rejected(self,body,reason):
  receipt=receipt_for(body)
  with self.assertRaisesRegex(BlizzardPatchNotesExtractorError,reason):self.extract(body,receipt)
if __name__=="__main__":unittest.main()
