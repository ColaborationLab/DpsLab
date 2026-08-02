import copy,hashlib,json
from pathlib import Path
import unittest
from dpslab.blizzard_patch_notes_layout_probe import BlizzardPatchNotesLayoutProbeError,calculate_layout_report_sha256,canonical_layout_report_bytes,probe_patch_notes_layout,validate_layout_report
from dpslab.official_source_receipt import calculate_receipt_sha256
ROOT=Path(__file__).parents[2];HTML=ROOT/"knowledge/fixtures/blizzard_patch_notes_layout_synthetic_0_1.html";SNAPSHOT=ROOT/"knowledge/snapshots/blizzard_patch_notes_layout_synthetic_0_1.json"
def receipt_for(body,status="captured_pending_review"):
 value={"schema_version":"0.1","identity":{"receipt_id":"synthetic.layout.receipt.001","captured_at":"2026-08-01T23:30:00Z"},"source":{"source_id":"blizzard.wow.content_update_notes","final_host":"worldofwarcraft.blizzard.com","media_type":"text/html"},"capture":{"transport_status":"response_quarantined_pending_capture_validation","capture_status":status,"complete":True,"byte_count":len(body),"content_sha256":hashlib.sha256(body).hexdigest(),"etag":'"layout-1"',"last_modified":None,"reused_previous":status!="captured_pending_review"},"integrity":{"hash_algorithm":"sha256","receipt_sha256":""}}
 value["integrity"]["receipt_sha256"]=calculate_receipt_sha256(value);return value
class LayoutProbeTests(unittest.TestCase):
 def setUp(self):self.body=HTML.read_bytes();self.receipt=receipt_for(self.body)
 def probe(self,body=None,receipt=None):return probe_patch_notes_layout(self.body if body is None else body,self.receipt if receipt is None else receipt,"synthetic.layout.report.001")
 def test_fixture_matches_snapshot(self):self.assertEqual(SNAPSHOT.read_bytes(),canonical_layout_report_bytes(self.probe()))
 def test_report_validates(self):self.assertEqual(self.probe(),validate_layout_report(self.probe()))
 def test_report_is_deterministic(self):self.assertEqual(self.probe(),self.probe())
 def test_status_is_pending_review(self):self.assertEqual("layout_observed_pending_review",self.probe()["identity"]["status"])
 def test_receipt_hash_binding(self):
  with self.assertRaisesRegex(BlizzardPatchNotesLayoutProbeError,"receipt_binding_mismatch"):self.probe(self.body+b"x")
 def test_receipt_size_binding(self):
  receipt=copy.deepcopy(self.receipt);receipt["capture"]["byte_count"]+=1;receipt["integrity"]["receipt_sha256"]=calculate_receipt_sha256(receipt)
  with self.assertRaisesRegex(BlizzardPatchNotesLayoutProbeError,"receipt_binding_mismatch"):self.probe(receipt=receipt)
 def test_receipt_must_be_pending(self):
  with self.assertRaisesRegex(BlizzardPatchNotesLayoutProbeError,"receipt_status_invalid"):self.probe(receipt=receipt_for(self.body,"duplicate"))
 def test_nonbytes_empty_and_nonutf8_rejected(self):
  for value,reason in (("html","html_bytes_invalid"),(b"","html_bytes_invalid"),(b"\xff","receipt_binding_mismatch")):
   with self.subTest(value=value),self.assertRaisesRegex(BlizzardPatchNotesLayoutProbeError,reason):self.probe(value)
 def test_nonutf8_bound_body_rejected(self):
  body=b"\xff"
  with self.assertRaisesRegex(BlizzardPatchNotesLayoutProbeError,"html_utf8_invalid"):self.probe(body,receipt_for(body))
 def test_text_and_values_are_erased(self):
  encoded=canonical_layout_report_bytes(self.probe()).lower()
  for forbidden in (b"synthetic heading",b"synthetic item",b"display:block",b"application/ld+json",b"data-view=",b"<html"):
   with self.subTest(forbidden=forbidden):self.assertNotIn(forbidden,encoded)
 def test_only_attribute_names_remain(self):self.assertIn({"tag":"body","name":"data-view","count":1},self.probe()["layout"]["attribute_names"])
 def test_hazards_are_boolean_only(self):self.assertEqual({"comments":True,"declarations":True,"scripts":True,"styles":True,"embedded_json":True},self.probe()["layout"]["hazards"])
 def test_tag_and_edge_counts_are_exact(self):
  report=self.probe();self.assertEqual(10,report["layout"]["node_count"]);self.assertIn({"parent":"article","child":"h2","count":1},report["layout"]["edges"])
 def test_malformed_nesting_rejected(self):
  body=b"<main><section></main></section>"
  with self.assertRaisesRegex(BlizzardPatchNotesLayoutProbeError,"nesting_invalid"):self.probe(body,receipt_for(body))
 def test_duplicate_attribute_rejected(self):
  body=b'<main id="a" id="b"></main>'
  with self.assertRaisesRegex(BlizzardPatchNotesLayoutProbeError,"attribute_duplicate"):self.probe(body,receipt_for(body))
 def test_node_limit_rejected(self):
  body=(b"<div></div>"*4097)
  with self.assertRaisesRegex(BlizzardPatchNotesLayoutProbeError,"probe_limit_exceeded"):self.probe(body,receipt_for(body))
 def test_depth_limit_rejected(self):
  body=b"<div>"*65+b"</div>"*65
  with self.assertRaisesRegex(BlizzardPatchNotesLayoutProbeError,"probe_limit_exceeded"):self.probe(body,receipt_for(body))
 def test_attribute_limit_rejected(self):
  body=("<div "+" ".join(f'a{i}="x"' for i in range(33))+"></div>").encode()
  with self.assertRaisesRegex(BlizzardPatchNotesLayoutProbeError,"probe_limit_exceeded"):self.probe(body,receipt_for(body))
 def test_closed_report_rejects_extra_field(self):
  report=self.probe();report["layout"]["text"]="forbidden"
  with self.assertRaisesRegex(BlizzardPatchNotesLayoutProbeError,"layout_invalid"):validate_layout_report(report)
 def test_hash_tampering_rejected(self):
  report=self.probe();report["layout"]["node_count"]+=1
  with self.assertRaises(BlizzardPatchNotesLayoutProbeError):validate_layout_report(report)
 def test_hash_projection_is_stable(self):self.assertEqual(self.probe()["integrity"]["report_sha256"],calculate_layout_report_sha256(self.probe()))
 def test_snapshot_is_canonical(self):self.assertEqual(SNAPSHOT.read_bytes(),canonical_layout_report_bytes(json.loads(SNAPSHOT.read_text())))
if __name__=="__main__":unittest.main()
