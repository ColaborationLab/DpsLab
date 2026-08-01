import copy,json
from datetime import datetime,timezone
from pathlib import Path
import unittest
from dpslab.candidate_knowledge_set import (CandidateContext,CandidateKnowledgeSetError,
 build_candidate_knowledge_set,calculate_receipt_sha256,canonical_receipt_bytes,
 validate_candidate_receipt)
from dpslab.knowledge_envelope import calculate_payload_sha256
from dpslab.static_template_catalog import calculate_catalog_sha256
from dpslab.catalog_change_proposal import calculate_proposal_sha256
from dpslab.proposal_review import calculate_decision_sha256

ROOT=Path(__file__).parents[2]
paths={"envelope":"knowledge/fixtures/static_fallback_template_synthetic_0_1.json","catalog":"knowledge/catalogs/static_template_catalog_synthetic_0_1.json","proposal":"knowledge/proposals/catalog_change_proposal_synthetic_0_1.json","decision":"knowledge/reviews/proposal_review_decision_synthetic_0_1.json","candidate":"knowledge/candidates/candidate_knowledge_set_synthetic_0_1.json"}
load=lambda p:json.loads((ROOT/p).read_text())
MAPPING={"guidance.synthetic.damage":{"statement_order":1,"before_text_key":"synthetic.priority.first","after_text_key":"synthetic.priority.updated","update_references":True}}
class CandidateKnowledgeSetTests(unittest.TestCase):
 def setUp(self):
  self.envelope=load(paths["envelope"]);self.catalog=load(paths["catalog"]);self.proposal=load(paths["proposal"]);self.decision=load(paths["decision"]);self.expected=load(paths["candidate"]);self.context=CandidateContext(datetime(2026,8,1,5,30,tzinfo=timezone.utc),"synthetic.retail.damage.002","0.1.1","synthetic.damage.002","knowledge/fixtures/static_fallback_template_synthetic_candidate_0_1.json")
 def build(self,**changes):
  return build_candidate_knowledge_set(changes.get("envelope",self.envelope),changes.get("catalog",self.catalog),changes.get("proposal",self.proposal),changes.get("decision",self.decision),changes.get("mapping",MAPPING),changes.get("context",self.context))
 def test_builder_matches_fixture(self):self.assertEqual(self.expected,self.build())
 def test_receipt_is_valid_and_canonical(self):self.assertEqual(canonical_receipt_bytes(self.expected["receipt"]),canonical_receipt_bytes(validate_candidate_receipt(self.expected["receipt"])))
 def test_receipt_hash_projection(self):
  value=copy.deepcopy(self.expected["receipt"]);value["integrity"]["receipt_sha256"]="f"*64;self.assertEqual(calculate_receipt_sha256(value),calculate_receipt_sha256(self.expected["receipt"]))
 def test_wrong_receipt_hash_rejected(self):
  value=copy.deepcopy(self.expected["receipt"]);value["integrity"]["receipt_sha256"]="f"*64
  with self.assertRaises(CandidateKnowledgeSetError):validate_candidate_receipt(value)
 def test_receipt_root_closed(self):
  value=copy.deepcopy(self.expected["receipt"]);value["extra"]=True
  with self.assertRaises(CandidateKnowledgeSetError):validate_candidate_receipt(value)
 def test_receipt_identity_closed(self):
  value=copy.deepcopy(self.expected["receipt"]);value["identity"]["extra"]=True
  with self.assertRaises(CandidateKnowledgeSetError):validate_candidate_receipt(value)
 def test_only_pending_status_allowed(self):
  value=copy.deepcopy(self.expected["receipt"]);value["identity"]["status"]="published";value["integrity"]["receipt_sha256"]=calculate_receipt_sha256(value)
  with self.assertRaises(CandidateKnowledgeSetError):validate_candidate_receipt(value)
 def test_hash_bindings_required(self):
  value=copy.deepcopy(self.expected["receipt"]);value["candidate_bindings"]["candidate_catalog_sha256"]="bad";value["integrity"]["receipt_sha256"]=calculate_receipt_sha256(value)
  with self.assertRaises(CandidateKnowledgeSetError):validate_candidate_receipt(value)
 def test_single_use_must_remain_pending_durable(self):
  value=copy.deepcopy(self.expected["receipt"]);value["consumption"]["single_use_pending_durable_record"]=False;value["integrity"]["receipt_sha256"]=calculate_receipt_sha256(value)
  with self.assertRaises(CandidateKnowledgeSetError):validate_candidate_receipt(value)
 def test_source_inputs_not_mutated(self):
  values=tuple(copy.deepcopy(x) for x in (self.envelope,self.catalog,self.proposal,self.decision));self.build();self.assertEqual(values,(self.envelope,self.catalog,self.proposal,self.decision))
 def test_candidate_envelope_is_unsigned(self):self.assertIsNone(self.build()["candidate_envelope"]["integrity"]["signature"])
 def test_candidate_catalog_adds_one_entry(self):self.assertEqual(len(self.catalog["entries"])+1,len(self.build()["candidate_catalog"]["entries"]))
 def test_source_entry_is_preserved(self):self.assertEqual(self.catalog["entries"][0],self.build()["candidate_catalog"]["entries"][0])
 def test_candidate_entry_is_pending(self):self.assertEqual("pending_review",self.build()["candidate_catalog"]["entries"][-1]["lifecycle_state"])
 def test_candidate_entry_supersedes_source(self):self.assertEqual(["synthetic.damage.001"],self.build()["candidate_catalog"]["entries"][-1]["supersedes_entry_ids"])
 def test_candidate_source_coverage_is_false(self):self.assertFalse(self.build()["candidate_catalog"]["entries"][-1]["source_coverage_complete"])
 def test_candidate_guidance_is_mapped(self):self.assertEqual("synthetic.priority.updated",self.build()["candidate_envelope"]["guidance"]["statements"][0]["text_key"])
 def test_candidate_provenance_binds_proposal(self):self.assertEqual(self.proposal["integrity"]["proposal_sha256"],self.build()["candidate_envelope"]["evidence"]["source_hashes"]["proposal"])
 def test_receipt_binds_candidate_hashes(self):
  result=self.build();self.assertEqual(result["candidate_catalog"]["integrity"]["catalog_sha256"],result["receipt"]["candidate_bindings"]["candidate_catalog_sha256"])
 def test_rejected_decision_fails(self):
  value=copy.deepcopy(self.decision);value["decision"]["outcome"]="rejected";value["integrity"]["decision_sha256"]=calculate_decision_sha256(value)
  with self.assertRaises(CandidateKnowledgeSetError):self.build(decision=value)
 def test_catalog_binding_mismatch_fails(self):
  value=copy.deepcopy(self.proposal);value["binding"]["catalog_sha256"]="f"*64;value["integrity"]["proposal_sha256"]=calculate_proposal_sha256(value)
  with self.assertRaises(CandidateKnowledgeSetError):self.build(proposal=value)
 def test_empty_mapping_fails(self):
  with self.assertRaises(CandidateKnowledgeSetError):self.build(mapping={})
 def test_unknown_physical_field_fails(self):
  with self.assertRaises(CandidateKnowledgeSetError):self.build(mapping={"other":{"statement_order":1,"before_text_key":"synthetic.priority.first","after_text_key":"synthetic.priority.updated","update_references":True}})
 def test_physical_before_mismatch_fails(self):
  mapping={"guidance.synthetic.damage":{"statement_order":1,"before_text_key":"synthetic.other","after_text_key":"synthetic.priority.updated","update_references":True}}
  with self.assertRaisesRegex(CandidateKnowledgeSetError,"before"):self.build(mapping=mapping)
 def test_statement_order_out_of_range_fails(self):
  mapping={"guidance.synthetic.damage":{"statement_order":99,"before_text_key":"synthetic.priority.first","after_text_key":"synthetic.priority.updated","update_references":True}}
  with self.assertRaises(CandidateKnowledgeSetError):self.build(mapping=mapping)
 def test_mapping_rule_is_closed(self):
  mapping=copy.deepcopy(MAPPING);mapping["guidance.synthetic.damage"]["extra"]=True
  with self.assertRaises(CandidateKnowledgeSetError):self.build(mapping=mapping)
 def test_stale_reference_is_rejected_when_not_updated(self):
  mapping=copy.deepcopy(MAPPING);mapping["guidance.synthetic.damage"]["update_references"]=False
  with self.assertRaisesRegex(CandidateKnowledgeSetError,"stale_reference"):self.build(mapping=mapping)
 def test_alternative_references_are_updated(self):
  self.assertEqual(["synthetic.priority.updated"],self.build()["candidate_envelope"]["guidance"]["statements"][1]["alternatives"])
 def test_naive_application_time_fails(self):
  context=CandidateContext(datetime(2026,8,1),"synthetic.retail.damage.002","0.1.1","synthetic.damage.002",self.context.envelope_path)
  with self.assertRaises(CandidateKnowledgeSetError):self.build(context=context)
 def test_invalid_version_fails(self):
  context=CandidateContext(self.context.applied_at,self.context.package_id,"next",self.context.entry_id,self.context.envelope_path)
  with self.assertRaises(CandidateKnowledgeSetError):self.build(context=context)
 def test_path_escape_fails(self):
  context=CandidateContext(self.context.applied_at,self.context.package_id,self.context.content_version,self.context.entry_id,"../outside.json")
  with self.assertRaises(CandidateKnowledgeSetError):self.build(context=context)
 def test_candidate_payload_hash_is_valid(self):self.assertEqual(calculate_payload_sha256(self.build()["candidate_envelope"]),self.build()["candidate_envelope"]["integrity"]["payload_sha256"])
 def test_candidate_catalog_hash_is_valid(self):self.assertEqual(calculate_catalog_sha256(self.build()["candidate_catalog"]),self.build()["candidate_catalog"]["integrity"]["catalog_sha256"])
 def test_candidate_fixture_has_no_real_claims(self):
  text=(ROOT/paths["candidate"]).read_text().lower()
  for forbidden in ("http://","https://","battle.net","blizzard","wowhead","dpcs90"):
   self.assertNotIn(forbidden,text)

if __name__=="__main__":unittest.main()
