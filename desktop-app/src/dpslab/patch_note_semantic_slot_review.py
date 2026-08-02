"""Fail-closed human semantic review of neutral patch-note slots."""
from copy import deepcopy
from datetime import datetime
import hashlib,json,re
from .patch_note_structural_slots import validate_structural_slots
class PatchNoteSemanticSlotReviewError(ValueError):pass
_SHA=re.compile(r"^[0-9a-f]{64}$")
_SLOTS={"slot.path_01","slot.path_02","slot.path_03"}
_ROLES={"article_title","publication_label","article_body","non_content_metadata","unknown","rejected"}
_REASONS={"direct_visual_confirmation","ambiguous_visual_structure","not_content_bearing","reviewer_rejected"}
_APPROVED={"article_title","publication_label","article_body"}
def _fail(reason):raise PatchNoteSemanticSlotReviewError(reason)
def canonical_semantic_review_bytes(d):return (json.dumps(d,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n").encode()
def calculate_semantic_review_sha256(d):v=deepcopy(dict(d));v["integrity"]["review_sha256"]="";return hashlib.sha256(canonical_semantic_review_bytes(v)).hexdigest()
def _timestamp(value):
 if not isinstance(value,str) or not value.endswith("Z"):_fail("timestamp_invalid")
 try:datetime.fromisoformat(value[:-1]+"+00:00")
 except ValueError:_fail("timestamp_invalid")
def validate_semantic_slot_review(d):
 v=dict(d)
 if set(v)!={"schema_version","identity","source","reviewer","decisions","integrity"} or v.get("schema_version")!="0.1":_fail("root_invalid")
 i,s,r,ds,g=v["identity"],v["source"],v["reviewer"],v["decisions"],v["integrity"]
 if set(i)!={"review_id","status"} or not isinstance(i.get("review_id"),str) or i.get("status") not in {"semantic_slot_review_approved","semantic_slot_review_pending"}:_fail("identity_invalid")
 if set(s)!={"receipt_id","receipt_sha256","slot_report_id","slot_report_sha256"}:_fail("source_invalid")
 if any(not isinstance(s.get(k),str) for k in s) or any(_SHA.fullmatch(s[k]) is None for k in ("receipt_sha256","slot_report_sha256")):_fail("source_invalid")
 if set(r)!={"reviewer_id","observed_at"} or not isinstance(r.get("reviewer_id"),str) or not r["reviewer_id"]:_fail("reviewer_invalid")
 _timestamp(r.get("observed_at"))
 if not isinstance(ds,list) or len(ds)!=3 or {x.get("slot_id") for x in ds}!=_SLOTS:_fail("decisions_invalid")
 roles=[]
 for x in ds:
  if set(x)!={"slot_id","role","reason_code"} or x.get("role") not in _ROLES or x.get("reason_code") not in _REASONS:_fail("decision_invalid")
  roles.append(x["role"])
 approved=set(roles)==_APPROVED and len(set(roles))==3
 expected="semantic_slot_review_approved" if approved else "semantic_slot_review_pending"
 if i["status"]!=expected:_fail("status_invalid")
 if set(g)!={"hash_algorithm","review_sha256"} or g.get("hash_algorithm")!="sha256" or not isinstance(g.get("review_sha256"),str) or _SHA.fullmatch(g["review_sha256"]) is None or calculate_semantic_review_sha256(v)!=g["review_sha256"]:_fail("integrity_invalid")
 return deepcopy(v)
def create_semantic_slot_review(slots,*,review_id,reviewer_id,observed_at,receipt_id,receipt_sha256,decisions):
 source=validate_structural_slots(slots)
 roles=[x.get("role") for x in decisions]
 status="semantic_slot_review_approved" if set(roles)==_APPROVED and len(roles)==3 and len(set(roles))==3 else "semantic_slot_review_pending"
 v={"schema_version":"0.1","identity":{"review_id":review_id,"status":status},"source":{"receipt_id":receipt_id,"receipt_sha256":receipt_sha256,"slot_report_id":source["identity"]["classification_id"],"slot_report_sha256":source["integrity"]["slots_sha256"]},"reviewer":{"reviewer_id":reviewer_id,"observed_at":observed_at},"decisions":deepcopy(decisions),"integrity":{"hash_algorithm":"sha256","review_sha256":""}}
 v["integrity"]["review_sha256"]=calculate_semantic_review_sha256(v);return validate_semantic_slot_review(v)
