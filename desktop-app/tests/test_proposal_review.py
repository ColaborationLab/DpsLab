import copy,json
from pathlib import Path
import unittest
from dpslab.proposal_review import (ProposalReviewError,calculate_decision_sha256,
 canonical_decision_bytes,evaluate_proposal_review,validate_proposal_review_decision)

ROOT=Path(__file__).parents[2]; DECISION=ROOT/"knowledge/reviews/proposal_review_decision_synthetic_0_1.json"; PROPOSAL=ROOT/"knowledge/proposals/catalog_change_proposal_synthetic_0_1.json"
def rehash(v): v["integrity"]["decision_sha256"]=calculate_decision_sha256(v); return v
class ProposalReviewTests(unittest.TestCase):
 def setUp(self): self.decision=json.loads(DECISION.read_text()); self.proposal=json.loads(PROPOSAL.read_text())
 def mutate(self,path,value):
  item=copy.deepcopy(self.decision); target=item
  for part in path[:-1]: target=target[part]
  target[path[-1]]=value; return rehash(item)
 def test_fixture_canonical_valid(self): self.assertEqual(DECISION.read_bytes(),canonical_decision_bytes(validate_proposal_review_decision(self.decision)))
 def test_hash_projection(self):
  item=copy.deepcopy(self.decision); item["integrity"]["decision_sha256"]="f"*64; self.assertEqual(calculate_decision_sha256(item),calculate_decision_sha256(self.decision))
 def test_wrong_hash_rejected(self):
  item=copy.deepcopy(self.decision); item["integrity"]["decision_sha256"]="f"*64
  with self.assertRaises(ProposalReviewError): validate_proposal_review_decision(item)
 def test_root_closed(self):
  item=copy.deepcopy(self.decision); item["extra"]=True
  with self.assertRaises(ProposalReviewError): validate_proposal_review_decision(item)
 def test_identity_closed(self):
  item=copy.deepcopy(self.decision); item["identity"]["extra"]=True
  with self.assertRaises(ProposalReviewError): validate_proposal_review_decision(item)
 def test_binding_closed(self):
  item=copy.deepcopy(self.decision); item["binding"]["extra"]=True
  with self.assertRaises(ProposalReviewError): validate_proposal_review_decision(item)
 def test_decision_closed(self):
  item=copy.deepcopy(self.decision); item["decision"]["extra"]=True
  with self.assertRaises(ProposalReviewError): validate_proposal_review_decision(item)
 def test_schema_rejected(self):
  with self.assertRaises(ProposalReviewError): validate_proposal_review_decision(self.mutate(["schema_version"],"0.2"))
 def test_bad_decision_id_rejected(self):
  with self.assertRaises(ProposalReviewError): validate_proposal_review_decision(self.mutate(["identity","decision_id"],"Bad ID"))
 def test_bad_time_rejected(self):
  with self.assertRaises(ProposalReviewError): validate_proposal_review_decision(self.mutate(["identity","created_at"],"not-time"))
 def test_binding_hashes_rejected(self):
  for field in ("proposal_sha256","catalog_sha256","evidence_sha256"):
   with self.assertRaises(ProposalReviewError): validate_proposal_review_decision(self.mutate(["binding",field],"bad"))
 def test_outcome_rejected(self):
  with self.assertRaises(ProposalReviewError): validate_proposal_review_decision(self.mutate(["decision","outcome"],"published"))
 def test_reviewer_required(self):
  with self.assertRaises(ProposalReviewError): validate_proposal_review_decision(self.mutate(["decision","reviewer_id"],""))
 def test_authority_required(self):
  with self.assertRaises(ProposalReviewError): validate_proposal_review_decision(self.mutate(["decision","authority_reference"],""))
 def test_created_and_decided_must_match(self):
  with self.assertRaises(ProposalReviewError): validate_proposal_review_decision(self.mutate(["decision","decided_at"],"2026-07-31T16:31:00Z"))
 def test_reasons_required(self):
  with self.assertRaises(ProposalReviewError): validate_proposal_review_decision(self.mutate(["decision","reason_codes"],[]))
 def test_duplicate_reasons_rejected(self):
  with self.assertRaises(ProposalReviewError): validate_proposal_review_decision(self.mutate(["decision","reason_codes"],["same","same"]))
 def test_limitations_required(self):
  with self.assertRaises(ProposalReviewError): validate_proposal_review_decision(self.mutate(["decision","limitations_acknowledged"],[]))
 def test_approval_is_eligible(self): self.assertEqual("decision_eligible",evaluate_proposal_review(self.proposal,self.decision).status)
 def test_rejection_is_distinct(self): self.assertEqual("decision_rejected",evaluate_proposal_review(self.proposal,self.mutate(["decision","outcome"],"rejected")).status)
 def test_proposal_id_mismatch(self): self.assertEqual("binding_mismatch",evaluate_proposal_review(self.proposal,self.mutate(["binding","proposal_id"],"proposal.other")).reason)
 def test_proposal_hash_mismatch(self): self.assertEqual("binding_mismatch",evaluate_proposal_review(self.proposal,self.mutate(["binding","proposal_sha256"],"f"*64)).reason)
 def test_catalog_hash_mismatch(self): self.assertEqual("binding_mismatch",evaluate_proposal_review(self.proposal,self.mutate(["binding","catalog_sha256"],"f"*64)).reason)
 def test_evidence_hash_mismatch(self): self.assertEqual("binding_mismatch",evaluate_proposal_review(self.proposal,self.mutate(["binding","evidence_sha256"],"f"*64)).reason)
 def test_all_proposal_limitations_must_be_acknowledged(self):
  item=self.mutate(["decision","limitations_acknowledged"],["requires_human_review"])
  self.assertEqual("limitations_mismatch",evaluate_proposal_review(self.proposal,item).reason)
 def test_consumed_decision_replay_rejected(self): self.assertEqual("replay_detected",evaluate_proposal_review(self.proposal,self.decision,frozenset({"synthetic.decision.1"})).reason)
 def test_consumed_proposal_replay_rejected(self): self.assertEqual("replay_detected",evaluate_proposal_review(self.proposal,self.decision,frozenset(),frozenset({self.proposal["integrity"]["proposal_sha256"]})).reason)
 def test_decision_before_creation_rejected(self):
  item=self.mutate(["identity","created_at"],"2026-07-31T15:59:00Z"); item["decision"]["decided_at"]="2026-07-31T15:59:00Z"; rehash(item)
  self.assertEqual("outside_validity_window",evaluate_proposal_review(self.proposal,item).reason)
 def test_decision_after_expiry_rejected(self):
  item=self.mutate(["identity","created_at"],"2026-08-01T16:01:00Z"); item["decision"]["decided_at"]="2026-08-01T16:01:00Z"; rehash(item)
  self.assertEqual("outside_validity_window",evaluate_proposal_review(self.proposal,item).reason)
 def test_boundary_times_are_allowed(self):
  for instant in ("2026-07-31T16:00:00Z","2026-08-01T16:00:00Z"):
   item=copy.deepcopy(self.decision); item["identity"]["created_at"]=instant; item["decision"]["decided_at"]=instant; rehash(item); self.assertEqual("decision_eligible",evaluate_proposal_review(self.proposal,item).status)
 def test_inputs_are_not_mutated(self):
  p=copy.deepcopy(self.proposal); d=copy.deepcopy(self.decision); evaluate_proposal_review(self.proposal,self.decision); self.assertEqual((p,d),(self.proposal,self.decision))
 def test_fixture_has_no_real_identity_or_network(self):
  text=DECISION.read_text().lower()
  for forbidden in ("http://","https://","battle.net","blizzard","daniel","dpcs90"):
   self.assertNotIn(forbidden,text)

if __name__=="__main__": unittest.main()
