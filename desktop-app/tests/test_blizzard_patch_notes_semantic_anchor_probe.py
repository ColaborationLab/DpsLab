import copy,hashlib,json
from pathlib import Path
import unittest
from dpslab.blizzard_patch_notes_semantic_anchor_probe import BlizzardPatchNotesSemanticAnchorProbeError,calculate_semantic_shape_sha256,canonical_semantic_shape_bytes,probe_semantic_anchor_shape,validate_semantic_shape
from dpslab.official_source_receipt import calculate_receipt_sha256
ROOT=Path(__file__).parents[2];HTML=ROOT/"knowledge/fixtures/blizzard_patch_notes_semantic_anchor_synthetic_0_1.html";SNAPSHOT=ROOT/"knowledge/snapshots/blizzard_patch_notes_semantic_shape_synthetic_0_1.json"
def receipt_for(body,status="captured_pending_review"):
 value={"schema_version":"0.1","identity":{"receipt_id":"synthetic.semantic.receipt.001","captured_at":"2026-08-02T00:30:00Z"},"source":{"source_id":"blizzard.wow.content_update_notes","final_host":"worldofwarcraft.blizzard.com","media_type":"text/html"},"capture":{"transport_status":"response_quarantined_pending_capture_validation","capture_status":status,"complete":True,"byte_count":len(body),"content_sha256":hashlib.sha256(body).hexdigest(),"etag":'"semantic-1"',"last_modified":None,"reused_previous":status!="captured_pending_review"},"integrity":{"hash_algorithm":"sha256","receipt_sha256":""}}
 value["integrity"]["receipt_sha256"]=calculate_receipt_sha256(value);return value
def carrier(payload):return '<article>'+'<div>'*7+f'<div data-props="{payload}"></div>'+'</div>'*7+'</article>'
def anchor(payload):return f'<html><body>{carrier(payload)}</body></html>'.encode()
class SemanticAnchorProbeTests(unittest.TestCase):
 def setUp(self):self.body=HTML.read_bytes();self.receipt=receipt_for(self.body)
 def probe(self,body=None,receipt=None):return probe_semantic_anchor_shape(self.body if body is None else body,self.receipt if receipt is None else receipt,"synthetic.semantic.report.001")
 def test_fixture_matches_snapshot(self):self.assertEqual(SNAPSHOT.read_bytes(),canonical_semantic_shape_bytes(self.probe()))
 def test_report_validates(self):self.assertEqual(self.probe(),validate_semantic_shape(self.probe()))
 def test_report_is_deterministic(self):self.assertEqual(self.probe(),self.probe())
 def test_status_and_anchor_count(self):self.assertEqual(("semantic_shape_observed_pending_review",2),(self.probe()["identity"]["status"],self.probe()["shape"]["anchor_count"]))
 def test_values_and_html_are_erased(self):
  encoded=canonical_semantic_shape_bytes(self.probe()).lower()
  for forbidden in (b"alpha",b"synthetic\"",b"data-props",b"<article",b":true",b":false"):
   with self.subTest(forbidden=forbidden):self.assertNotIn(forbidden,encoded)
 def test_paths_and_types_are_aggregated(self):
  paths={item["path"]:item for item in self.probe()["shape"]["paths"]};self.assertEqual("array",paths["syntheticRoot.syntheticItems"]["json_type"]);self.assertEqual(2,paths["syntheticRoot.syntheticEnabled"]["occurrences"]);self.assertEqual(1,paths["syntheticRoot.syntheticItems"]["max_array_length"])
 def test_receipt_hash_binding(self):
  with self.assertRaisesRegex(BlizzardPatchNotesSemanticAnchorProbeError,"receipt_binding_mismatch"):self.probe(self.body+b"x")
 def test_receipt_size_binding(self):
  receipt=copy.deepcopy(self.receipt);receipt["capture"]["byte_count"]+=1;receipt["integrity"]["receipt_sha256"]=calculate_receipt_sha256(receipt)
  with self.assertRaisesRegex(BlizzardPatchNotesSemanticAnchorProbeError,"receipt_binding_mismatch"):self.probe(receipt=receipt)
 def test_receipt_must_be_pending(self):
  with self.assertRaisesRegex(BlizzardPatchNotesSemanticAnchorProbeError,"receipt_status_invalid"):self.probe(receipt=receipt_for(self.body,"duplicate"))
 def test_empty_match_rejected(self):
  body=b"<html><body><article></article></body></html>"
  with self.assertRaisesRegex(BlizzardPatchNotesSemanticAnchorProbeError,"semantic_anchor_unavailable"):self.probe(body,receipt_for(body))
 def test_direct_child_path_rejected(self):
  body=b'<article><section><div data-props="{&quot;x&quot;:1}"></div></section></article>'
  with self.assertRaisesRegex(BlizzardPatchNotesSemanticAnchorProbeError,"anchor_path_not_allowed"):self.probe(body,receipt_for(body))
 def test_invalid_json_rejected(self):
  body=anchor("not-json")
  with self.assertRaisesRegex(BlizzardPatchNotesSemanticAnchorProbeError,"anchor_json_invalid"):self.probe(body,receipt_for(body))
 def test_duplicate_json_key_rejected(self):
  body=anchor("{&quot;x&quot;:1,&quot;x&quot;:2}")
  with self.assertRaisesRegex(BlizzardPatchNotesSemanticAnchorProbeError,"json_key_duplicate"):self.probe(body,receipt_for(body))
 def test_nonobject_root_rejected(self):
  body=anchor("[1,2]")
  with self.assertRaisesRegex(BlizzardPatchNotesSemanticAnchorProbeError,"anchor_root_invalid"):self.probe(body,receipt_for(body))
 def test_conflicting_types_rejected(self):
  body=(carrier("{&quot;x&quot;:1}")+carrier("{&quot;x&quot;:&quot;a&quot;}")).encode()
  with self.assertRaisesRegex(BlizzardPatchNotesSemanticAnchorProbeError,"json_type_conflict"):self.probe(body,receipt_for(body))
 def test_nonfinite_number_rejected(self):
  body=anchor("{&quot;x&quot;:NaN}")
  with self.assertRaisesRegex(BlizzardPatchNotesSemanticAnchorProbeError,"json_number_invalid"):self.probe(body,receipt_for(body))
 def test_invalid_key_rejected(self):
  body=anchor("{&quot;bad key&quot;:1}")
  with self.assertRaisesRegex(BlizzardPatchNotesSemanticAnchorProbeError,"json_key_invalid"):self.probe(body,receipt_for(body))
 def test_array_limit_rejected(self):
  body=anchor("{&quot;x&quot;:["+",".join("0" for _ in range(257))+"]}")
  with self.assertRaisesRegex(BlizzardPatchNotesSemanticAnchorProbeError,"array_length_limit_exceeded"):self.probe(body,receipt_for(body))
 def test_depth_limit_rejected(self):
  value="0"
  for index in range(18):value='{"x":'+value+'}'
  body=anchor(value.replace('"','&quot;'))
  with self.assertRaisesRegex(BlizzardPatchNotesSemanticAnchorProbeError,"json_limit_exceeded"):self.probe(body,receipt_for(body))
 def test_html_nesting_rejected(self):
  body=('<article>'+'<div>'*7+'<div data-props="{&quot;x&quot;:1}"></article>'+'</div>'*8).encode()
  with self.assertRaisesRegex(BlizzardPatchNotesSemanticAnchorProbeError,"html_nesting_invalid"):self.probe(body,receipt_for(body))
 def test_shorter_and_longer_paths_rejected(self):
  for count in (7,9):
   body=('<article>'+'<div>'*(count-1)+'<div data-props="{&quot;x&quot;:1}"></div>'+'</div>'*(count-1)+'</article>').encode()
   with self.subTest(count=count),self.assertRaisesRegex(BlizzardPatchNotesSemanticAnchorProbeError,"anchor_path_not_allowed"):self.probe(body,receipt_for(body))
 def test_mixed_exact_and_invalid_paths_fail_closed(self):
  body=(carrier("{&quot;x&quot;:1}")+'<article><div data-props="{&quot;x&quot;:1}"></div></article>').encode()
  with self.assertRaisesRegex(BlizzardPatchNotesSemanticAnchorProbeError,"anchor_path_not_allowed"):self.probe(body,receipt_for(body))
 def test_closed_report_rejects_extra_field(self):
  report=self.probe();report["shape"]["values"]=[]
  with self.assertRaisesRegex(BlizzardPatchNotesSemanticAnchorProbeError,"shape_invalid"):validate_semantic_shape(report)
 def test_hash_tampering_rejected(self):
  report=self.probe();report["shape"]["anchor_count"]+=1
  with self.assertRaisesRegex(BlizzardPatchNotesSemanticAnchorProbeError,"report_sha256_mismatch"):validate_semantic_shape(report)
 def test_hash_projection_stable(self):self.assertEqual(self.probe()["integrity"]["report_sha256"],calculate_semantic_shape_sha256(self.probe()))
 def test_snapshot_is_canonical(self):self.assertEqual(SNAPSHOT.read_bytes(),canonical_semantic_shape_bytes(json.loads(SNAPSHOT.read_text())))
if __name__=="__main__":unittest.main()
