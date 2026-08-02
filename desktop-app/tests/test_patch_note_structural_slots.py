import copy,json
from pathlib import Path
import unittest
from dpslab.blizzard_patch_notes_text_topology_probe import calculate_text_topology_sha256
from dpslab.patch_note_structural_slots import PatchNoteStructuralSlotsError,calculate_structural_slots_sha256,canonical_structural_slots_bytes,classify_structural_slots,validate_structural_slots
ROOT=Path(__file__).parents[2];SNAPSHOT=ROOT/"knowledge/snapshots/patch_note_structural_slots_synthetic_0_1.json"
def topology():
 paths=[]
 for tags,total,maximum in [(["article"]+["div"]*5,60,8),(["article"]+["div"]*8,12,1),(["article"]+["div"]*4+["p"],240,30)]:paths.append({"tags":tags,"text_nodes":12,"total_characters":total,"max_characters":maximum})
 v={"schema_version":"0.1","identity":{"report_id":"synthetic.topology.001","probe_revision":"blizzard.text-topology.0.1","status":"text_topology_observed_pending_review"},"source":{"receipt_id":"synthetic.receipt.001","receipt_sha256":"1"*64,"content_sha256":"2"*64,"byte_count":100},"topology":{"paths":paths,"visible_text_nodes":36,"excluded_text_nodes":0},"integrity":{"hash_algorithm":"sha256","report_sha256":""}};v["integrity"]["report_sha256"]=calculate_text_topology_sha256(v);return v
class StructuralSlotsTests(unittest.TestCase):
 def classify(self,value=None):return classify_structural_slots(topology() if value is None else value,"synthetic.slots.001")
 def test_snapshot(self):self.assertEqual(SNAPSHOT.read_bytes(),canonical_structural_slots_bytes(self.classify()))
 def test_valid(self):self.assertEqual(self.classify(),validate_structural_slots(self.classify()))
 def test_deterministic(self):self.assertEqual(self.classify(),self.classify())
 def test_pending(self):self.assertEqual("structural_slots_pending_review",self.classify()["identity"]["status"])
 def test_exact_ids(self):self.assertEqual(["slot.path_01","slot.path_02","slot.path_03"],[x["slot_id"] for x in self.classify()["slots"]])
 def test_metrics_preserved(self):self.assertEqual(240,self.classify()["slots"][2]["total_characters"])
 def test_no_text_or_semantics(self):
  raw=canonical_structural_slots_bytes(self.classify()).lower()
  for x in (b"title",b"date",b"content",b"ability",b"recommendation"):
   with self.subTest(x=x):self.assertNotIn(x,raw)
 def test_missing_path(self):
  v=topology();v["topology"]["paths"].pop();v["topology"]["visible_text_nodes"]=24;v["integrity"]["report_sha256"]=calculate_text_topology_sha256(v)
  with self.assertRaisesRegex(PatchNoteStructuralSlotsError,"topology_paths_not_exact"):self.classify(v)
 def test_extra_path(self):
  v=topology();v["topology"]["paths"].append({"tags":["article","span"],"text_nodes":1,"total_characters":1,"max_characters":1});v["topology"]["visible_text_nodes"]=37;v["integrity"]["report_sha256"]=calculate_text_topology_sha256(v)
  with self.assertRaisesRegex(PatchNoteStructuralSlotsError,"topology_paths_not_exact"):self.classify(v)
 def test_changed_path(self):
  v=topology();v["topology"]["paths"][0]["tags"].append("div");v["integrity"]["report_sha256"]=calculate_text_topology_sha256(v)
  with self.assertRaisesRegex(PatchNoteStructuralSlotsError,"topology_paths_not_exact"):self.classify(v)
 def test_invalid_input_hash(self):
  v=topology();v["integrity"]["report_sha256"]="0"*64
  with self.assertRaises(Exception):self.classify(v)
 def test_closed_root(self):
  v=self.classify();v["meaning"]="forbidden"
  with self.assertRaisesRegex(PatchNoteStructuralSlotsError,"root_invalid"):validate_structural_slots(v)
 def test_closed_slot(self):
  v=self.classify();v["slots"][0]["meaning"]="forbidden"
  with self.assertRaisesRegex(PatchNoteStructuralSlotsError,"slot_invalid"):validate_structural_slots(v)
 def test_slot_id_tamper(self):
  v=self.classify();v["slots"][0]["slot_id"]="title"
  with self.assertRaisesRegex(PatchNoteStructuralSlotsError,"slot_invalid"):validate_structural_slots(v)
 def test_path_tamper(self):
  v=self.classify();v["slots"][0]["tags"].append("div")
  with self.assertRaisesRegex(PatchNoteStructuralSlotsError,"slot_invalid"):validate_structural_slots(v)
 def test_metric_tamper(self):
  v=self.classify();v["slots"][0]["text_nodes"]=0
  with self.assertRaisesRegex(PatchNoteStructuralSlotsError,"slot_metric_invalid"):validate_structural_slots(v)
 def test_hash_tamper(self):
  v=self.classify();v["integrity"]["slots_sha256"]="0"*64
  with self.assertRaisesRegex(PatchNoteStructuralSlotsError,"integrity_invalid"):validate_structural_slots(v)
 def test_hash_projection(self):self.assertEqual(self.classify()["integrity"]["slots_sha256"],calculate_structural_slots_sha256(self.classify()))
 def test_snapshot_canonical(self):self.assertEqual(SNAPSHOT.read_bytes(),canonical_structural_slots_bytes(json.loads(SNAPSHOT.read_text())))
if __name__=="__main__":unittest.main()
