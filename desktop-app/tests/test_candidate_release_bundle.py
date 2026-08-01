import copy,json
from datetime import datetime,timezone
from pathlib import Path
import unittest

from dpslab.candidate_release_bundle import (CandidateReleaseBundleError,ReleaseBundleContext,
 build_candidate_release_bundle,calculate_release_manifest_sha256,canonical_release_manifest_bytes,
 validate_candidate_release_bundle,validate_release_manifest)
from dpslab.candidate_knowledge_review import calculate_review_decision_sha256
from tests.test_candidate_knowledge_review import generation

ROOT=Path(__file__).parents[2]
load=lambda p:json.loads((ROOT/p).read_text(encoding="utf-8"))
REVIEW="knowledge/reviews/candidate_knowledge_review_decision_synthetic_0_1.json";FIXTURE="knowledge/releases/candidate_knowledge_release_bundle_synthetic_0_1.json"

class CandidateReleaseBundleTests(unittest.TestCase):
 def setUp(self):self.generation=generation();self.review=load(REVIEW);self.fixture=load(FIXTURE);self.context=ReleaseBundleContext("release.synthetic.001",datetime(2026,8,1,7,0,tzinfo=timezone.utc),"stable","0.1.1")
 def build(self,**changes):return build_candidate_release_bundle(changes.get("generation",self.generation),changes.get("review",self.review),changes.get("context",self.context))
 def test_builder_matches_fixture(self):self.assertEqual(self.fixture,self.build())
 def test_fixture_validates_canonically(self):self.assertEqual(self.fixture,validate_candidate_release_bundle(self.fixture))
 def test_manifest_validates_canonically(self):self.assertEqual(canonical_release_manifest_bytes(self.fixture["manifest"]),canonical_release_manifest_bytes(validate_release_manifest(self.fixture["manifest"])))
 def test_manifest_hash_projection(self):
  value=copy.deepcopy(self.fixture["manifest"]);value["integrity"]["manifest_sha256"]="f"*64;self.assertEqual(calculate_release_manifest_sha256(value),calculate_release_manifest_sha256(self.fixture["manifest"]))
 def test_reviewed_entry_is_promoted(self):self.assertEqual("approved",self.fixture["release_catalog"]["entries"][-1]["lifecycle_state"])
 def test_source_entry_is_preserved(self):self.assertEqual(self.generation["candidate_catalog"]["entries"][0],self.fixture["release_catalog"]["entries"][0])
 def test_source_is_not_deprecated(self):self.assertEqual("pending_review",self.fixture["release_catalog"]["entries"][0]["lifecycle_state"])
 def test_release_entry_coverage_and_safety(self):
  entry=self.fixture["release_catalog"]["entries"][-1];self.assertTrue(entry["source_coverage_complete"]);self.assertTrue(entry["role_policy"]["dynamic_safety_satisfied"])
 def test_review_identity_is_copied(self):self.assertEqual(self.review["identity"]["decision_id"],self.fixture["release_catalog"]["entries"][-1]["review"]["decision_id"])
 def test_bundle_remains_signature_pending(self):self.assertEqual("signature_pending",self.fixture["manifest"]["identity"]["status"])
 def test_envelope_remains_unsigned(self):self.assertIsNone(self.fixture["release_envelope"]["integrity"]["signature"])
 def test_inputs_are_not_mutated(self):
  before=(copy.deepcopy(self.generation),copy.deepcopy(self.review));self.build();self.assertEqual(before,(self.generation,self.review))
 def test_rejected_review_cannot_build(self):
  value=copy.deepcopy(self.review);value["decision"]["outcome"]="rejected";value["integrity"]["decision_sha256"]=calculate_review_decision_sha256(value)
  with self.assertRaises(CandidateReleaseBundleError):self.build(review=value)
 def test_target_channel_must_match(self):
  with self.assertRaisesRegex(CandidateReleaseBundleError,"target_channel_mismatch"):self.build(context=ReleaseBundleContext(self.context.bundle_id,self.context.created_at,"beta",self.context.content_version))
 def test_content_version_must_match(self):
  with self.assertRaisesRegex(CandidateReleaseBundleError,"content_version_mismatch"):self.build(context=ReleaseBundleContext(self.context.bundle_id,self.context.created_at,"stable","0.1.2"))
 def test_naive_created_at_fails(self):
  with self.assertRaisesRegex(CandidateReleaseBundleError,"created_at_invalid"):self.build(context=ReleaseBundleContext(self.context.bundle_id,datetime(2026,8,1,7),"stable","0.1.1"))
 def test_release_cannot_predate_review(self):
  with self.assertRaisesRegex(CandidateReleaseBundleError,"release_predates_review"):self.build(context=ReleaseBundleContext(self.context.bundle_id,datetime(2026,8,1,6,tzinfo=timezone.utc),"stable","0.1.1"))
 def test_bundle_root_is_closed(self):
  value=copy.deepcopy(self.fixture);value["extra"]=True
  with self.assertRaisesRegex(CandidateReleaseBundleError,"bundle_fields_invalid"):validate_candidate_release_bundle(value)
 def test_manifest_root_is_closed(self):
  value=copy.deepcopy(self.fixture["manifest"]);value["extra"]=True
  with self.assertRaisesRegex(CandidateReleaseBundleError,"manifest_fields_invalid"):validate_release_manifest(value)
 def test_fixture_contains_no_live_source(self):
  text=(ROOT/FIXTURE).read_text().lower()
  for forbidden in ("http://","https://","battle.net","blizzard","wowhead","dpcs90"):self.assertNotIn(forbidden,text)

def _negative(name,mutate):
 def test(self):
  value=copy.deepcopy(self.fixture);mutate(value)
  with self.assertRaises(CandidateReleaseBundleError):validate_candidate_release_bundle(value)
 test.__name__=f"test_rejects_{name}";return test

_CASES={
 "published_status":lambda x:x["manifest"]["identity"].__setitem__("status","published"),
 "development_channel":lambda x:x["manifest"]["identity"].__setitem__("target_channel","dev"),
 "invalid_version":lambda x:x["manifest"]["identity"].__setitem__("content_version","next"),
 "boolean_build":lambda x:x["manifest"]["compatibility"].__setitem__("build_min",True),
 "reversed_build_range":lambda x:x["manifest"]["compatibility"].__setitem__("build_min",999999),
 "bad_commit_hash":lambda x:x["manifest"]["bindings"].__setitem__("candidate_commit_sha256","bad"),
 "bad_manifest_hash":lambda x:x["manifest"]["integrity"].__setitem__("manifest_sha256","f"*64),
 "catalog_binding_mismatch":lambda x:x["manifest"]["bindings"].__setitem__("release_catalog_sha256","f"*64),
 "review_binding_mismatch":lambda x:x["manifest"]["bindings"].__setitem__("review_decision_sha256","f"*64),
 "unsigned_state_removed":lambda x:x["release_envelope"]["integrity"].__setitem__("signature","synthetic"),
 "coverage_removed":lambda x:x["release_catalog"]["entries"][-1].__setitem__("source_coverage_complete",False),
 "approval_removed":lambda x:x["release_catalog"]["entries"][-1].__setitem__("lifecycle_state","pending_review"),
}
for _name,_mutate in _CASES.items():setattr(CandidateReleaseBundleTests,f"test_rejects_{_name}",_negative(_name,_mutate))

if __name__=="__main__":unittest.main()
