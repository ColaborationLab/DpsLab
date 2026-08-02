import copy,hashlib,json
from pathlib import Path
import unittest
from dpslab.blizzard_patch_notes_text_topology_probe import BlizzardPatchNotesTextTopologyProbeError,calculate_text_topology_sha256,canonical_text_topology_bytes,probe_text_topology,validate_text_topology
from dpslab.official_source_receipt import calculate_receipt_sha256
ROOT=Path(__file__).parents[2];HTML=ROOT/"knowledge/fixtures/blizzard_patch_notes_text_topology_synthetic_0_1.html";SNAPSHOT=ROOT/"knowledge/snapshots/blizzard_patch_notes_text_topology_synthetic_0_1.json"
def receipt_for(body,status="captured_pending_review"):
 v={"schema_version":"0.1","identity":{"receipt_id":"synthetic.text.receipt.001","captured_at":"2026-08-02T01:30:00Z"},"source":{"source_id":"blizzard.wow.content_update_notes","final_host":"worldofwarcraft.blizzard.com","media_type":"text/html"},"capture":{"transport_status":"response_quarantined_pending_capture_validation","capture_status":status,"complete":True,"byte_count":len(body),"content_sha256":hashlib.sha256(body).hexdigest(),"etag":'"text-1"',"last_modified":None,"reused_previous":status!="captured_pending_review"},"integrity":{"hash_algorithm":"sha256","receipt_sha256":""}};v["integrity"]["receipt_sha256"]=calculate_receipt_sha256(v);return v
class TextTopologyTests(unittest.TestCase):
 def setUp(self):self.body=HTML.read_bytes();self.receipt=receipt_for(self.body)
 def probe(self,body=None,receipt=None):return probe_text_topology(self.body if body is None else body,self.receipt if receipt is None else receipt,"synthetic.text.report.001")
 def test_fixture_snapshot(self):self.assertEqual(SNAPSHOT.read_bytes(),canonical_text_topology_bytes(self.probe()))
 def test_valid_deterministic(self):self.assertEqual(self.probe(),validate_text_topology(self.probe()));self.assertEqual(self.probe(),self.probe())
 def test_pending(self):self.assertEqual("text_topology_observed_pending_review",self.probe()["identity"]["status"])
 def test_exact_metrics(self):self.assertEqual((4,2),(self.probe()["topology"]["visible_text_nodes"],self.probe()["topology"]["excluded_text_nodes"]))
 def test_text_is_erased(self):
  raw=canonical_text_topology_bytes(self.probe()).lower()
  for x in (b"invented",b"forbidden",b"outside text",b"<article"):
   with self.subTest(x=x):self.assertNotIn(x,raw)
 def test_paths_include_heading_and_list(self):
  paths=[x["tags"] for x in self.probe()["topology"]["paths"]];self.assertIn(["article","h2"],paths);self.assertIn(["article","div","ul","li","strong"],paths)
 def test_outside_article_ignored(self):self.assertEqual(4,self.probe()["topology"]["visible_text_nodes"])
 def test_excluded_subtrees_count_only(self):self.assertEqual(2,self.probe()["topology"]["excluded_text_nodes"])
 def test_receipt_binding(self):
  with self.assertRaisesRegex(BlizzardPatchNotesTextTopologyProbeError,"receipt_binding_mismatch"):self.probe(self.body+b"x")
 def test_receipt_status(self):
  with self.assertRaisesRegex(BlizzardPatchNotesTextTopologyProbeError,"receipt_status_invalid"):self.probe(receipt=receipt_for(self.body,"duplicate"))
 def test_empty_visible_rejected(self):
  b=b"<article><script>x</script></article>"
  with self.assertRaisesRegex(BlizzardPatchNotesTextTopologyProbeError,"visible_article_text_unavailable"):self.probe(b,receipt_for(b))
 def test_malformed_rejected(self):
  b=b"<article><p>x</article></p>"
  with self.assertRaisesRegex(BlizzardPatchNotesTextTopologyProbeError,"nesting_invalid"):self.probe(b,receipt_for(b))
 def test_nonbytes_empty_utf8(self):
  for b in ("x",b""):
   with self.assertRaisesRegex(BlizzardPatchNotesTextTopologyProbeError,"html_bytes_invalid"):self.probe(b)
  b=b"\xff"
  with self.assertRaisesRegex(BlizzardPatchNotesTextTopologyProbeError,"html_utf8_invalid"):self.probe(b,receipt_for(b))
 def test_nested_article_uses_nearest(self):
  b=b"<article><article><p>abc</p></article></article>";self.assertEqual(["article","p"],probe_text_topology(b,receipt_for(b),"synthetic.text.report.002")["topology"]["paths"][0]["tags"])
 def test_whitespace_ignored(self):
  b=b"<article>   <p>x</p>  </article>";self.assertEqual(1,probe_text_topology(b,receipt_for(b),"synthetic.text.report.002")["topology"]["visible_text_nodes"])
 def test_closed_report(self):
  v=self.probe();v["topology"]["text"]=[]
  with self.assertRaisesRegex(BlizzardPatchNotesTextTopologyProbeError,"topology_invalid"):validate_text_topology(v)
 def test_tamper_rejected(self):
  v=self.probe();v["topology"]["visible_text_nodes"]+=1
  with self.assertRaises(BlizzardPatchNotesTextTopologyProbeError):validate_text_topology(v)
 def test_hash_projection(self):self.assertEqual(self.probe()["integrity"]["report_sha256"],calculate_text_topology_sha256(self.probe()))
 def test_snapshot_canonical(self):self.assertEqual(SNAPSHOT.read_bytes(),canonical_text_topology_bytes(json.loads(SNAPSHOT.read_text())))
if __name__=="__main__":unittest.main()
