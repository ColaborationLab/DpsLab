import json,unittest
from pathlib import Path
from dpslab.patch_note_semantic_review_ceremony import *
ROOT=Path(__file__).resolve().parents[2]
SLOTS=json.loads((ROOT/"knowledge/snapshots/patch_note_structural_slots_synthetic_0_1.json").read_text())
ROLES=iter(["article_title","publication_label","article_body"])
class CeremonyTests(unittest.TestCase):
 def setUp(self):
  self.buffers=[];self.seen=[];self.roles=iter(["article_title","publication_label","article_body"]);self.binding=True
 def verify(self):return self.binding
 def content(self,slot):
  b=bytearray(("synthetic "+slot).encode());self.buffers.append(b);return b
 def decide(self,slot,view):
  self.seen.append((slot,bytes(view)));return {"role":next(self.roles),"reason_code":"direct_visual_confirmation"}
 def ceremony(self,**overrides):
  kwargs=dict(review_id="synthetic.ceremony.001",reviewer_id="synthetic-reviewer",observed_at="2026-08-05T05:00:00Z",receipt_id="synthetic.receipt.001",receipt_sha256="a"*64,verify_binding=self.verify,provide_content=self.content,request_decision=self.decide);kwargs.update(overrides);return run_semantic_review_ceremony(SLOTS,**kwargs)
 def test_completed(self):self.assertEqual(self.ceremony().status,"ceremony_completed")
 def test_three_slots_in_order(self):self.ceremony();self.assertEqual([x[0] for x in self.seen],["slot.path_01","slot.path_02","slot.path_03"])
 def test_all_buffers_zeroized(self):self.ceremony();self.assertTrue(all(not any(x) for x in self.buffers))
 def test_readonly_view(self):
  def decision(slot,view):self.assertTrue(view.readonly);return self.decide(slot,view)
  self.ceremony(request_decision=decision)
 def test_initial_binding_rejection(self):self.binding=False;self.assertEqual(self.ceremony().status,"ceremony_binding_rejected");self.assertFalse(self.buffers)
 def test_drift_before_second_slot(self):
  calls=0
  def verify():
   nonlocal calls;calls+=1;return calls<3
  out=self.ceremony(verify_binding=verify);self.assertEqual(out.status,"ceremony_source_drifted");self.assertEqual(out.reviewed_slots,1)
 def test_drift_after_last_slot(self):
  calls=0
  def verify():
   nonlocal calls;calls+=1;return calls<5
  self.assertEqual(self.ceremony(verify_binding=verify).status,"ceremony_source_drifted")
 def test_cancel_zeroizes(self):
  out=self.ceremony(request_decision=lambda s,v:None);self.assertEqual(out.status,"ceremony_cancelled");self.assertTrue(all(not any(x) for x in self.buffers))
 def test_display_error_zeroizes(self):
  def bad(s,v):raise RuntimeError("display failed")
  with self.assertRaises(RuntimeError):self.ceremony(request_decision=bad)
  self.assertTrue(all(not any(x) for x in self.buffers))
 def test_requires_bytearray(self):
  with self.assertRaisesRegex(SemanticReviewCeremonyError,"owned_bytearray"):self.ceremony(provide_content=lambda s:b"immutable")
 def test_empty_rejected_and_zeroized(self):
  b=bytearray()
  with self.assertRaisesRegex(SemanticReviewCeremonyError,"content_size_invalid"):self.ceremony(provide_content=lambda s:b)
 def test_oversize_rejected_and_zeroized(self):
  b=bytearray(b"1234")
  with self.assertRaisesRegex(SemanticReviewCeremonyError,"content_size_invalid"):self.ceremony(provide_content=lambda s:b,max_slot_bytes=3)
  self.assertFalse(any(b))
 def test_invalid_limit(self):
  with self.assertRaisesRegex(SemanticReviewCeremonyError,"max_slot_bytes_invalid"):self.ceremony(max_slot_bytes=0)
 def test_unknown_is_pending(self):
  roles=iter(["unknown","publication_label","article_body"])
  out=self.ceremony(request_decision=lambda s,v:{"role":next(roles),"reason_code":"ambiguous_visual_structure"});self.assertEqual(out.review["identity"]["status"],"semantic_slot_review_pending")
 def test_no_content_in_review(self):
  raw=json.dumps(self.ceremony().review);self.assertNotIn("synthetic slot.path",raw)
 def test_invalid_decision_fails_after_zeroize(self):
  with self.assertRaises(Exception):self.ceremony(request_decision=lambda s,v:{"role":"ability","reason_code":"direct_visual_confirmation"})
  self.assertTrue(all(not any(x) for x in self.buffers))
