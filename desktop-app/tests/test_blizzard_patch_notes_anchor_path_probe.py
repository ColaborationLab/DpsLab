import copy,hashlib,json
from pathlib import Path
import unittest
from dpslab.blizzard_patch_notes_anchor_path_probe import BlizzardPatchNotesAnchorPathProbeError,calculate_anchor_path_sha256,canonical_anchor_path_bytes,probe_anchor_paths,validate_anchor_path_report
from dpslab.official_source_receipt import calculate_receipt_sha256
ROOT=Path(__file__).parents[2];HTML=ROOT/"knowledge/fixtures/blizzard_patch_notes_anchor_path_synthetic_0_1.html";SNAPSHOT=ROOT/"knowledge/snapshots/blizzard_patch_notes_anchor_path_synthetic_0_1.json"
def receipt_for(body,status="captured_pending_review"):
 value={"schema_version":"0.1","identity":{"receipt_id":"synthetic.path.receipt.001","captured_at":"2026-08-02T01:00:00Z"},"source":{"source_id":"blizzard.wow.content_update_notes","final_host":"worldofwarcraft.blizzard.com","media_type":"text/html"},"capture":{"transport_status":"response_quarantined_pending_capture_validation","capture_status":status,"complete":True,"byte_count":len(body),"content_sha256":hashlib.sha256(body).hexdigest(),"etag":'"path-1"',"last_modified":None,"reused_previous":status!="captured_pending_review"},"integrity":{"hash_algorithm":"sha256","receipt_sha256":""}}
 value["integrity"]["receipt_sha256"]=calculate_receipt_sha256(value);return value
class AnchorPathProbeTests(unittest.TestCase):
 def setUp(self):self.body=HTML.read_bytes();self.receipt=receipt_for(self.body)
 def probe(self,body=None,receipt=None):return probe_anchor_paths(self.body if body is None else body,self.receipt if receipt is None else receipt,"synthetic.path.report.001")
 def test_fixture_matches_snapshot(self):self.assertEqual(SNAPSHOT.read_bytes(),canonical_anchor_path_bytes(self.probe()))
 def test_report_validates(self):self.assertEqual(self.probe(),validate_anchor_path_report(self.probe()))
 def test_deterministic(self):self.assertEqual(self.probe(),self.probe())
 def test_pending_status(self):self.assertEqual("anchor_path_observed_pending_review",self.probe()["identity"]["status"])
 def test_counts_anchored_and_unanchored(self):self.assertEqual((3,2,1),(lambda p:(p["carrier_count"],p["anchored_count"],p["unanchored_count"]))(self.probe()["paths"]))
 def test_exact_nearest_article_paths(self):self.assertEqual([["article","div","section","div"],["article","section","div","div"]],[x["tags"] for x in self.probe()["paths"]["signatures"]])
 def test_values_are_never_retained(self):
  raw=canonical_anchor_path_bytes(self.probe())
  for value in (b"secret-one",b"secret-two",b"secret-three",b"data-props",b"<article"):
   with self.subTest(value=value):self.assertNotIn(value,raw)
 def test_receipt_binding(self):
  with self.assertRaisesRegex(BlizzardPatchNotesAnchorPathProbeError,"receipt_binding_mismatch"):self.probe(self.body+b"x")
 def test_receipt_status(self):
  with self.assertRaisesRegex(BlizzardPatchNotesAnchorPathProbeError,"receipt_status_invalid"):self.probe(receipt=receipt_for(self.body,"duplicate"))
 def test_empty_carrier_rejected(self):
  body=b"<article><div></div></article>"
  with self.assertRaisesRegex(BlizzardPatchNotesAnchorPathProbeError,"anchor_carrier_unavailable"):self.probe(body,receipt_for(body))
 def test_non_div_carrier_ignored(self):
  body=b'<article><span data-props="secret"></span></article>'
  with self.assertRaisesRegex(BlizzardPatchNotesAnchorPathProbeError,"anchor_carrier_unavailable"):self.probe(body,receipt_for(body))
 def test_malformed_nesting_rejected(self):
  body=b'<article><div data-props="x"></article></div>'
  with self.assertRaisesRegex(BlizzardPatchNotesAnchorPathProbeError,"nesting_invalid"):self.probe(body,receipt_for(body))
 def test_duplicate_attribute_rejected(self):
  body=b'<article><div data-props="x" data-props="y"></div></article>'
  with self.assertRaisesRegex(BlizzardPatchNotesAnchorPathProbeError,"attribute_duplicate"):self.probe(body,receipt_for(body))
 def test_nonbytes_empty_nonutf8(self):
  for body,reason in (("x","html_bytes_invalid"),(b"","html_bytes_invalid")):
   with self.subTest(body=body),self.assertRaisesRegex(BlizzardPatchNotesAnchorPathProbeError,reason):self.probe(body)
  body=b"\xff"
  with self.assertRaisesRegex(BlizzardPatchNotesAnchorPathProbeError,"html_utf8_invalid"):self.probe(body,receipt_for(body))
 def test_nearest_nested_article_wins(self):
  body=b'<article><section><article><div data-props="x"></div></article></section></article>'
  self.assertEqual(["article","div"],probe_anchor_paths(body,receipt_for(body),"synthetic.path.report.002")["paths"]["signatures"][0]["tags"])
 def test_node_limit(self):
  body=b"<br>"*4097+b'<div data-props="x"></div>'
  with self.assertRaisesRegex(BlizzardPatchNotesAnchorPathProbeError,"probe_limit_exceeded"):self.probe(body,receipt_for(body))
 def test_closed_report(self):
  report=self.probe();report["paths"]["values"]=[]
  with self.assertRaisesRegex(BlizzardPatchNotesAnchorPathProbeError,"paths_invalid"):validate_anchor_path_report(report)
 def test_count_tamper_rejected(self):
  report=self.probe();report["paths"]["anchored_count"]+=1
  with self.assertRaises(BlizzardPatchNotesAnchorPathProbeError):validate_anchor_path_report(report)
 def test_hash_tamper_rejected(self):
  report=self.probe();report["integrity"]["report_sha256"]="0"*64
  with self.assertRaisesRegex(BlizzardPatchNotesAnchorPathProbeError,"report_sha256_mismatch"):validate_anchor_path_report(report)
 def test_hash_projection_stable(self):self.assertEqual(self.probe()["integrity"]["report_sha256"],calculate_anchor_path_sha256(self.probe()))
 def test_snapshot_canonical(self):self.assertEqual(SNAPSHOT.read_bytes(),canonical_anchor_path_bytes(json.loads(SNAPSHOT.read_text())))
if __name__=="__main__":unittest.main()
