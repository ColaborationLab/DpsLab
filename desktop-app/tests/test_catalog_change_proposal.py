import copy, json
from datetime import datetime, timezone, timedelta
from pathlib import Path
import unittest

from dpslab.catalog_change_proposal import (CatalogProposalError, ProposalContext,
 calculate_proposal_sha256, canonical_proposal_bytes, build_catalog_change_proposal,
 validate_catalog_change_proposal)

ROOT=Path(__file__).parents[2]
PROPOSAL=ROOT/"knowledge/proposals/catalog_change_proposal_synthetic_0_1.json"
EVIDENCE=ROOT/"knowledge/snapshots/patch_evidence_synthetic_0_1.json"
CATALOG=ROOT/"knowledge/catalogs/static_template_catalog_synthetic_0_1.json"
MAPPING={"synthetic.role.damage":"guidance.synthetic.damage","synthetic.role.safety":"guidance.synthetic.safety"}
def rehash(v): v["integrity"]["proposal_sha256"]=calculate_proposal_sha256(v); return v

class CatalogChangeProposalTests(unittest.TestCase):
 def setUp(self):
  self.proposal=json.loads(PROPOSAL.read_text()); self.evidence=json.loads(EVIDENCE.read_text()); self.catalog=json.loads(CATALOG.read_text()); start=datetime(2026,7,31,16,tzinfo=timezone.utc); self.context=ProposalContext("damage",1,71,("synthetic_single_target",),start,start+timedelta(days=1))
 def mutate(self,path,value):
  item=copy.deepcopy(self.proposal); target=item
  for part in path[:-1]: target=target[part]
  target[path[-1]]=value; return rehash(item)
 def test_fixture_canonical_valid(self): self.assertEqual(PROPOSAL.read_bytes(),canonical_proposal_bytes(validate_catalog_change_proposal(self.proposal)))
 def test_hash_projection(self):
  item=copy.deepcopy(self.proposal); item["integrity"]["proposal_sha256"]="f"*64; self.assertEqual(calculate_proposal_sha256(item),calculate_proposal_sha256(self.proposal))
 def test_wrong_hash_rejected(self):
  item=copy.deepcopy(self.proposal); item["integrity"]["proposal_sha256"]="f"*64
  with self.assertRaises(CatalogProposalError): validate_catalog_change_proposal(item)
 def test_root_closed(self):
  item=copy.deepcopy(self.proposal); item["extra"]=True
  with self.assertRaises(CatalogProposalError): validate_catalog_change_proposal(item)
 def test_identity_closed(self):
  item=copy.deepcopy(self.proposal); item["identity"]["extra"]=True
  with self.assertRaises(CatalogProposalError): validate_catalog_change_proposal(item)
 def test_binding_closed(self):
  item=copy.deepcopy(self.proposal); item["binding"]["extra"]=True
  with self.assertRaises(CatalogProposalError): validate_catalog_change_proposal(item)
 def test_operation_closed(self):
  item=copy.deepcopy(self.proposal); item["operations"][0]["extra"]=True
  with self.assertRaises(CatalogProposalError): validate_catalog_change_proposal(item)
 def test_schema_rejected(self):
  with self.assertRaises(CatalogProposalError): validate_catalog_change_proposal(self.mutate(["schema_version"],"0.2"))
 def test_only_pending_review_allowed(self):
  with self.assertRaises(CatalogProposalError): validate_catalog_change_proposal(self.mutate(["identity","status"],"approved"))
 def test_expiry_must_advance(self):
  with self.assertRaises(CatalogProposalError): validate_catalog_change_proposal(self.mutate(["identity","expires_at"],"2026-07-31T16:00:00Z"))
 def test_hash_bindings_rejected(self):
  for field in ("catalog_sha256","evidence_sha256"):
   with self.assertRaises(CatalogProposalError): validate_catalog_change_proposal(self.mutate(["binding",field],"bad"))
 def test_binding_ranges_rejected(self):
  with self.assertRaises(CatalogProposalError): validate_catalog_change_proposal(self.mutate(["binding","build_min"],120501))
 def test_subject_role_rejected(self):
  with self.assertRaises(CatalogProposalError): validate_catalog_change_proposal(self.mutate(["subject","role"],"support"))
 def test_subject_ids_rejected(self):
  with self.assertRaises(CatalogProposalError): validate_catalog_change_proposal(self.mutate(["subject","class_id"],True))
 def test_empty_contexts_rejected(self):
  with self.assertRaises(CatalogProposalError): validate_catalog_change_proposal(self.mutate(["subject","content_contexts"],[]))
 def test_empty_operations_rejected(self):
  with self.assertRaises(CatalogProposalError): validate_catalog_change_proposal(self.mutate(["operations"],[]))
 def test_duplicate_operation_id_rejected(self):
  item=copy.deepcopy(self.proposal); item["operations"].append(copy.deepcopy(item["operations"][0]))
  with self.assertRaises(CatalogProposalError): validate_catalog_change_proposal(rehash(item))
 def test_conflicting_target_rejected(self):
  item=copy.deepcopy(self.proposal); other=copy.deepcopy(item["operations"][0]); other["operation_id"]="other"; item["operations"].append(other)
  with self.assertRaises(CatalogProposalError): validate_catalog_change_proposal(rehash(item))
 def test_action_rejected(self):
  with self.assertRaises(CatalogProposalError): validate_catalog_change_proposal(self.mutate(["operations",0,"action"],"approve"))
 def test_action_value_matrix_rejected(self):
  for action,before,after in (("add","old","new"),("replace","same","same"),("remove",None,None),("invalidate","old",None)):
   item=copy.deepcopy(self.proposal); op=item["operations"][0]; op.update({"action":action,"before_token":before,"after_token":after})
   with self.assertRaises(CatalogProposalError): validate_catalog_change_proposal(rehash(item))
 def test_limitations_required(self):
  with self.assertRaises(CatalogProposalError): validate_catalog_change_proposal(self.mutate(["operations",0,"limitations"],[]))
 def test_review_cannot_embed_approval(self):
  item=copy.deepcopy(self.proposal); item["review"]["decision_id"]="decision"
  with self.assertRaises(CatalogProposalError): validate_catalog_change_proposal(rehash(item))
 def test_builder_matches_fixture(self): self.assertEqual(self.proposal,build_catalog_change_proposal(self.evidence,self.catalog,MAPPING,self.context))
 def test_builder_binds_catalog_hash(self): self.assertEqual(self.catalog["integrity"]["catalog_sha256"],build_catalog_change_proposal(self.evidence,self.catalog,MAPPING,self.context)["binding"]["catalog_sha256"])
 def test_historical_evidence_rejected(self):
  item=copy.deepcopy(self.evidence); item["identity"]["lifecycle"]="historical"; from dpslab.patch_evidence import calculate_evidence_sha256; item["integrity"]["evidence_sha256"]=calculate_evidence_sha256(item)
  with self.assertRaisesRegex(CatalogProposalError,"historical"): build_catalog_change_proposal(item,self.catalog,MAPPING,self.context)
 def test_unknown_family_rejected(self):
  with self.assertRaises(CatalogProposalError): build_catalog_change_proposal(self.evidence,self.catalog,{"other":"field.other"},self.context)
 def test_empty_mapping_rejected(self):
  with self.assertRaises(CatalogProposalError): build_catalog_change_proposal(self.evidence,self.catalog,{},self.context)
 def test_invalid_context_time_rejected(self):
  context=ProposalContext("damage",1,71,("synthetic",),datetime(2026,7,31),datetime(2026,8,1))
  with self.assertRaises(CatalogProposalError): build_catalog_change_proposal(self.evidence,self.catalog,MAPPING,context)
 def test_invalid_context_subject_rejected(self):
  context=ProposalContext("damage",0,71,("synthetic",),self.context.created_at,self.context.expires_at)
  with self.assertRaises(CatalogProposalError): build_catalog_change_proposal(self.evidence,self.catalog,MAPPING,context)
 def test_context_must_match_catalog_entry(self):
  context=ProposalContext("damage",2,71,("synthetic_single_target",),self.context.created_at,self.context.expires_at)
  with self.assertRaisesRegex(CatalogProposalError,"catalog_subject"): build_catalog_change_proposal(self.evidence,self.catalog,MAPPING,context)
 def test_stale_or_future_evidence_rejected(self):
  for start in (datetime(2026,7,30,tzinfo=timezone.utc),datetime(2026,8,10,tzinfo=timezone.utc)):
   context=ProposalContext("damage",1,71,("synthetic_single_target",),start,start+timedelta(days=1))
   with self.assertRaisesRegex(CatalogProposalError,"stale"): build_catalog_change_proposal(self.evidence,self.catalog,MAPPING,context)
 def test_invalid_age_policy_rejected(self):
  context=ProposalContext("damage",1,71,("synthetic_single_target",),self.context.created_at,self.context.expires_at,0)
  with self.assertRaises(CatalogProposalError): build_catalog_change_proposal(self.evidence,self.catalog,MAPPING,context)
 def test_tank_damage_requires_safety(self):
  context=ProposalContext("tank",1,71,("synthetic",),self.context.created_at,self.context.expires_at)
  with self.assertRaisesRegex(CatalogProposalError,"safety"): build_catalog_change_proposal(self.evidence,self.catalog,MAPPING,context)
 def test_healer_damage_requires_safety(self):
  context=ProposalContext("healer",1,71,("synthetic",),self.context.created_at,self.context.expires_at)
  with self.assertRaisesRegex(CatalogProposalError,"safety"): build_catalog_change_proposal(self.evidence,self.catalog,MAPPING,context)
 def test_invalidation_becomes_separate_operation(self):
  item=copy.deepcopy(self.evidence); item["assertions"][0]["invalidation_families"]=["synthetic.role.safety"]; from dpslab.patch_evidence import calculate_evidence_sha256; item["integrity"]["evidence_sha256"]=calculate_evidence_sha256(item)
  self.assertEqual(2,len(build_catalog_change_proposal(item,self.catalog,MAPPING,self.context)["operations"]))
 def test_empty_assertions_rejected(self):
  item=copy.deepcopy(self.evidence); item["assertions"]=[]; from dpslab.patch_evidence import calculate_evidence_sha256; item["integrity"]["evidence_sha256"]=calculate_evidence_sha256(item)
  with self.assertRaises(CatalogProposalError): build_catalog_change_proposal(item,self.catalog,MAPPING,self.context)
 def test_fixture_contains_no_real_claims(self):
  text=PROPOSAL.read_text().lower()
  for forbidden in ("http://","https://","battle.net","blizzard","wowhead","best in slot"):
   self.assertNotIn(forbidden,text)

if __name__=="__main__": unittest.main()
