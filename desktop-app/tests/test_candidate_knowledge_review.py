import copy,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
import unittest

from dpslab.candidate_knowledge_review import (CandidateKnowledgeReviewError,CandidateReviewContext,
 build_candidate_review_decision,calculate_review_decision_sha256,canonical_review_decision_bytes,
 evaluate_candidate_review,validate_candidate_review_decision)
from dpslab.candidate_knowledge_set import canonical_receipt_bytes
from dpslab.candidate_knowledge_store import calculate_commit_sha256
from dpslab.knowledge_envelope import canonical_json_bytes
from dpslab.static_template_catalog import canonical_catalog_bytes

ROOT=Path(__file__).parents[2]
PATHS={"candidate":"knowledge/candidates/candidate_knowledge_set_synthetic_0_1.json","fixture":"knowledge/reviews/candidate_knowledge_review_decision_synthetic_0_1.json","source_envelope":"knowledge/fixtures/static_fallback_template_synthetic_0_1.json","source_catalog":"knowledge/catalogs/static_template_catalog_synthetic_0_1.json","proposal":"knowledge/proposals/catalog_change_proposal_synthetic_0_1.json","proposal_decision":"knowledge/reviews/proposal_review_decision_synthetic_0_1.json"}
def load(name):return json.loads((ROOT/PATHS[name]).read_text(encoding="utf-8"))

def generation():
 x=load("candidate");e=x["candidate_envelope"];c=x["candidate_catalog"];r=x["receipt"]
 commit={"schema_version":"0.1","identity":{"generation_id":"candidate.synthetic.001","committed_at":"2026-08-01T06:00:00Z","status":"candidate_pending_review"},"bindings":{"candidate_envelope_sha256":hashlib.sha256(canonical_json_bytes(e)).hexdigest(),"candidate_catalog_sha256":hashlib.sha256(canonical_catalog_bytes(c)).hexdigest(),"receipt_sha256":hashlib.sha256(canonical_receipt_bytes(r)).hexdigest()},"consumption":{"decision_id":r["consumption"]["decision_id"],"proposal_id":r["consumption"]["proposal_id"],"durably_recorded":True},"integrity":{"hash_algorithm":"sha256","commit_sha256":""}}
 commit["integrity"]["commit_sha256"]=calculate_commit_sha256(commit);marker={"schema_version":"0.1","generation_id":"candidate.synthetic.001","commit_sha256":commit["integrity"]["commit_sha256"]}
 return {"marker":marker,"commit":commit,"candidate_envelope":e,"candidate_catalog":c,"receipt":r,"source_envelope":load("source_envelope"),"source_catalog":load("source_catalog"),"proposal":load("proposal"),"proposal_decision":load("proposal_decision")}

class CandidateKnowledgeReviewTests(unittest.TestCase):
 def setUp(self):
  self.generation=generation();self.fixture=load("fixture");self.limitations=tuple(self.generation["candidate_envelope"]["evidence"]["limitations"])
 def context(self,**changes):
  values={"decision_id":"candidate.review.synthetic.001","reviewer_id":"daniel","authority_reference":"n0.gov.synthetic","human_attestation_id":"human.attestation.synthetic.001","reviewed_at":datetime(2026,8,1,6,30,tzinfo=timezone.utc),"wow_build":120500,"interface":120500,"outcome":"approved","freshness":"current","applicability":"applicable","source_coverage":"complete","role_safety":"satisfied","reason_codes":("candidate.review.human_approved","damage.contextual_dps"),"limitations_acknowledged":self.limitations};values.update(changes);return CandidateReviewContext(**values)
 def build(self,**changes):return build_candidate_review_decision(changes.get("generation",self.generation),changes.get("context",self.context()))
 def rehash(self,value):value["integrity"]["decision_sha256"]=calculate_review_decision_sha256(value);return value
 def test_builder_matches_fixture(self):self.assertEqual(self.fixture,self.build())
 def test_fixture_is_canonical_and_valid(self):self.assertEqual(canonical_review_decision_bytes(self.fixture),canonical_review_decision_bytes(validate_candidate_review_decision(self.fixture)))
 def test_approved_review_is_eligible(self):self.assertEqual("review_eligible_for_publication",evaluate_candidate_review(self.generation,self.fixture).status)
 def test_approval_does_not_mutate_generation(self):
  before=copy.deepcopy(self.generation);self.build();self.assertEqual(before,self.generation)
 def test_exact_marker_is_bound(self):self.assertEqual(hashlib.sha256(canonical_json_bytes(self.generation["marker"])).hexdigest(),self.fixture["binding"]["marker_sha256"])
 def test_exact_commit_is_bound(self):self.assertEqual(self.generation["commit"]["integrity"]["commit_sha256"],self.fixture["binding"]["commit_sha256"])
 def test_source_evidence_is_bound(self):self.assertEqual(self.generation["receipt"]["source_bindings"]["proposal_sha256"],self.fixture["binding"]["proposal_sha256"])
 def test_candidate_remains_pending(self):self.assertEqual("pending_review",self.generation["candidate_catalog"]["entries"][-1]["lifecycle_state"])
 def test_candidate_remains_unsigned(self):self.assertIsNone(self.generation["candidate_envelope"]["integrity"]["signature"])
 def test_decision_root_is_closed(self):
  value=copy.deepcopy(self.fixture);value["extra"]=True
  with self.assertRaisesRegex(CandidateKnowledgeReviewError,"root_fields_invalid"):validate_candidate_review_decision(value)
 def test_decision_hash_is_enforced(self):
  value=copy.deepcopy(self.fixture);value["integrity"]["decision_sha256"]="f"*64
  with self.assertRaisesRegex(CandidateKnowledgeReviewError,"decision_sha256_mismatch"):validate_candidate_review_decision(value)
 def test_hash_projection_omits_only_hash(self):
  value=copy.deepcopy(self.fixture);value["integrity"]["decision_sha256"]="f"*64;self.assertEqual(calculate_review_decision_sha256(self.fixture),calculate_review_decision_sha256(value))
 def test_marker_mismatch_fails_closed(self):
  value=copy.deepcopy(self.generation);value["marker"]["commit_sha256"]="f"*64
  with self.assertRaisesRegex(CandidateKnowledgeReviewError,"marker_commit_mismatch"):self.build(generation=value)
 def test_commit_binding_mismatch_fails_closed(self):
  value=copy.deepcopy(self.generation);value["commit"]["bindings"]["receipt_sha256"]="f"*64;value["commit"]["integrity"]["commit_sha256"]=calculate_commit_sha256(value["commit"]);value["marker"]["commit_sha256"]=value["commit"]["integrity"]["commit_sha256"]
  with self.assertRaisesRegex(CandidateKnowledgeReviewError,"commit_binding_mismatch"):self.build(generation=value)
 def test_source_evidence_mismatch_fails_closed(self):
  value=copy.deepcopy(self.generation);value["source_envelope"]["identity"]["package_id"]="synthetic.changed"
  with self.assertRaises(CandidateKnowledgeReviewError):self.build(generation=value)
 def test_generation_root_is_closed(self):
  value=copy.deepcopy(self.generation);value["extra"]=True
  with self.assertRaisesRegex(CandidateKnowledgeReviewError,"generation_fields_invalid"):self.build(generation=value)
 def test_naive_review_time_fails(self):
  with self.assertRaisesRegex(CandidateKnowledgeReviewError,"reviewed_at_invalid"):self.build(context=self.context(reviewed_at=datetime(2026,8,1,6,30)))
 def test_review_before_commit_fails(self):
  with self.assertRaisesRegex(CandidateKnowledgeReviewError,"decision_predates_commit"):self.build(context=self.context(reviewed_at=datetime(2026,8,1,5,59,tzinfo=timezone.utc)))
 def test_build_outside_range_cannot_be_approved(self):
  with self.assertRaisesRegex(CandidateKnowledgeReviewError,"build_not_applicable"):self.build(context=self.context(wow_build=130000))
 def test_stale_cannot_be_approved(self):
  with self.assertRaisesRegex(CandidateKnowledgeReviewError,"approved_assessment_not_satisfied"):self.build(context=self.context(freshness="stale"))
 def test_unknown_applicability_cannot_be_approved(self):
  with self.assertRaisesRegex(CandidateKnowledgeReviewError,"approved_assessment_not_satisfied"):self.build(context=self.context(applicability="unknown"))
 def test_incomplete_coverage_cannot_be_approved(self):
  with self.assertRaisesRegex(CandidateKnowledgeReviewError,"approved_assessment_not_satisfied"):self.build(context=self.context(source_coverage="incomplete"))
 def test_unsatisfied_role_safety_cannot_be_approved(self):
  with self.assertRaisesRegex(CandidateKnowledgeReviewError,"approved_assessment_not_satisfied"):self.build(context=self.context(role_safety="unsatisfied"))
 def test_required_limitation_must_be_acknowledged(self):
  with self.assertRaisesRegex(CandidateKnowledgeReviewError,"limitations_not_acknowledged"):self.build(context=self.context(limitations_acknowledged=("synthetic_fixture_only",)))
 def test_damage_role_reason_is_required(self):
  with self.assertRaisesRegex(CandidateKnowledgeReviewError,"role_reason_missing"):self.build(context=self.context(reason_codes=("candidate.review.human_approved",)))
 def test_human_attestation_is_required(self):
  with self.assertRaisesRegex(CandidateKnowledgeReviewError,"human_attestation_id_invalid"):self.build(context=self.context(human_attestation_id=""))
 def test_binding_mismatch_is_unavailable(self):
  value=copy.deepcopy(self.fixture);value["binding"]["marker_sha256"]="f"*64;self.rehash(value);outcome=evaluate_candidate_review(self.generation,value);self.assertEqual(("review_unavailable","binding_mismatch"),(outcome.status,outcome.reason))
 def test_rejection_is_immutable_outcome(self):
  decision=self.build(context=self.context(outcome="rejected",freshness="stale",applicability="inapplicable",source_coverage="incomplete",role_safety="unsatisfied",wow_build=130000,reason_codes=("candidate.review.rejected",)))
  self.assertEqual("review_rejected",evaluate_candidate_review(self.generation,decision).status)
 def test_invalid_assessment_token_fails(self):
  value=copy.deepcopy(self.fixture);value["assessment"]["freshness"]="recent";self.rehash(value)
  with self.assertRaisesRegex(CandidateKnowledgeReviewError,"freshness_invalid"):validate_candidate_review_decision(value)
 def test_boolean_build_is_rejected(self):
  value=copy.deepcopy(self.fixture);value["assessment"]["wow_build"]=True;self.rehash(value)
  with self.assertRaisesRegex(CandidateKnowledgeReviewError,"wow_build_invalid"):validate_candidate_review_decision(value)
 def test_fixture_contains_no_live_sources(self):
  text=(ROOT/PATHS["fixture"]).read_text().lower()
  for forbidden in ("http://","https://","battle.net","blizzard","wowhead","dpcs90"):self.assertNotIn(forbidden,text)

if __name__=="__main__":unittest.main()
