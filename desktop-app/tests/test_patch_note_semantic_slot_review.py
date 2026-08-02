import json,unittest
from copy import deepcopy
from pathlib import Path
from dpslab.patch_note_semantic_slot_review import *
ROOT=Path(__file__).resolve().parents[2]
SLOTS=json.loads((ROOT/"knowledge/snapshots/patch_note_structural_slots_synthetic_0_1.json").read_text())
DECISIONS=[
 {"slot_id":"slot.path_01","role":"article_title","reason_code":"direct_visual_confirmation"},
 {"slot_id":"slot.path_02","role":"publication_label","reason_code":"direct_visual_confirmation"},
 {"slot_id":"slot.path_03","role":"article_body","reason_code":"direct_visual_confirmation"}]
def build(decisions=DECISIONS):return create_semantic_slot_review(SLOTS,review_id="synthetic.semantic-review.001",reviewer_id="synthetic-reviewer",observed_at="2026-08-02T04:00:00Z",receipt_id="synthetic.receipt.001",receipt_sha256="a"*64,decisions=decisions)
class SemanticSlotReviewTests(unittest.TestCase):
 def test_valid_approved(self):self.assertEqual(build()["identity"]["status"],"semantic_slot_review_approved")
 def test_exact_roles(self):self.assertEqual({x["role"] for x in build()["decisions"]},{"article_title","publication_label","article_body"})
 def test_unknown_pending(self):
  d=deepcopy(DECISIONS);d[0]["role"]="unknown";d[0]["reason_code"]="ambiguous_visual_structure";self.assertEqual(build(d)["identity"]["status"],"semantic_slot_review_pending")
 def test_rejected_pending(self):
  d=deepcopy(DECISIONS);d[0]["role"]="rejected";d[0]["reason_code"]="reviewer_rejected";self.assertEqual(build(d)["identity"]["status"],"semantic_slot_review_pending")
 def test_duplicate_pending(self):
  d=deepcopy(DECISIONS);d[1]["role"]="article_title";self.assertEqual(build(d)["identity"]["status"],"semantic_slot_review_pending")
 def test_non_content_pending(self):
  d=deepcopy(DECISIONS);d[1]["role"]="non_content_metadata";d[1]["reason_code"]="not_content_bearing";self.assertEqual(build(d)["identity"]["status"],"semantic_slot_review_pending")
 def test_missing_slot(self):
  with self.assertRaises(PatchNoteSemanticSlotReviewError):build(DECISIONS[:2])
 def test_duplicate_slot(self):
  d=deepcopy(DECISIONS);d[2]["slot_id"]=d[0]["slot_id"]
  with self.assertRaises(PatchNoteSemanticSlotReviewError):build(d)
 def test_unknown_role(self):
  d=deepcopy(DECISIONS);d[0]["role"]="ability"
  with self.assertRaises(PatchNoteSemanticSlotReviewError):build(d)
 def test_unknown_reason(self):
  d=deepcopy(DECISIONS);d[0]["reason_code"]="inferred_from_length"
  with self.assertRaises(PatchNoteSemanticSlotReviewError):build(d)
 def test_invalid_receipt_hash(self):
  with self.assertRaises(PatchNoteSemanticSlotReviewError):create_semantic_slot_review(SLOTS,review_id="x",reviewer_id="r",observed_at="2026-08-02T04:00:00Z",receipt_id="r",receipt_sha256="bad",decisions=DECISIONS)
 def test_invalid_timestamp(self):
  with self.assertRaises(PatchNoteSemanticSlotReviewError):create_semantic_slot_review(SLOTS,review_id="x",reviewer_id="r",observed_at="today",receipt_id="r",receipt_sha256="a"*64,decisions=DECISIONS)
 def test_altered_slot_report(self):
  s=deepcopy(SLOTS);s["slots"][0]["text_nodes"]+=1
  with self.assertRaises(Exception):create_semantic_slot_review(s,review_id="x",reviewer_id="r",observed_at="2026-08-02T04:00:00Z",receipt_id="r",receipt_sha256="a"*64,decisions=DECISIONS)
 def test_status_tamper(self):
  v=build();v["identity"]["status"]="semantic_slot_review_pending";v["integrity"]["review_sha256"]=calculate_semantic_review_sha256(v)
  with self.assertRaises(PatchNoteSemanticSlotReviewError):validate_semantic_slot_review(v)
 def test_hash_tamper(self):
  v=build();v["reviewer"]["reviewer_id"]="other"
  with self.assertRaises(PatchNoteSemanticSlotReviewError):validate_semantic_slot_review(v)
 def test_closed_root(self):
  v=build();v["text"]="forbidden";v["integrity"]["review_sha256"]=calculate_semantic_review_sha256(v)
  with self.assertRaises(PatchNoteSemanticSlotReviewError):validate_semantic_slot_review(v)
 def test_no_content_or_facts(self):
  raw=json.dumps(build());self.assertNotIn("html",raw);self.assertNotIn("ability",raw);self.assertNotIn("recommend",raw)
 def test_deterministic(self):self.assertEqual(build(),build())
 def test_snapshot(self):
  expected=json.loads((ROOT/"knowledge/snapshots/patch_note_semantic_slot_review_synthetic_0_1.json").read_text());self.assertEqual(build(),expected)
