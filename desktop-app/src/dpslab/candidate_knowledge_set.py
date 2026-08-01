"""Pure construction of an unpublished candidate knowledge set."""

from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib, json, re
from typing import Any, Mapping

from .catalog_change_proposal import validate_catalog_change_proposal
from .knowledge_envelope import calculate_payload_sha256, canonical_json_bytes, validate_knowledge_envelope
from .proposal_review import calculate_decision_sha256, evaluate_proposal_review
from .static_template_catalog import calculate_catalog_sha256, canonical_catalog_bytes, validate_static_template_catalog

class CandidateKnowledgeSetError(ValueError): pass

@dataclass(frozen=True)
class CandidateContext:
    applied_at: datetime
    package_id: str
    content_version: str
    entry_id: str
    envelope_path: str

_TOKEN=re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$"); _VERSION=re.compile(r"^(?:0|[1-9][0-9]*)(?:\.[0-9]+){0,3}$"); _SHA=re.compile(r"^[0-9a-f]{64}$")
_RECEIPT={"schema_version","identity","source_bindings","candidate_bindings","consumption","integrity"}
_IDENTITY={"receipt_id","applied_at","status"}; _SOURCE={"source_envelope_sha256","source_catalog_sha256","proposal_sha256","decision_sha256"}; _CANDIDATE={"candidate_envelope_sha256","candidate_catalog_sha256"}; _CONSUMPTION={"decision_id","proposal_id","single_use_pending_durable_record"}; _INTEGRITY={"hash_algorithm","receipt_sha256"}

def _fail(reason:str)->None: raise CandidateKnowledgeSetError(reason)
def _closed(value:Any,fields:set[str],label:str)->dict[str,Any]:
    if not isinstance(value,dict) or set(value)!=fields: _fail(f"{label}_fields_invalid")
    return value
def _token(value:Any,label:str)->str:
    if not isinstance(value,str) or _TOKEN.fullmatch(value) is None: _fail(f"{label}_invalid")
    return value
def _time(value:Any,label:str)->datetime:
    if not isinstance(value,str) or not value.endswith("Z"): _fail(f"{label}_invalid")
    try:return datetime.fromisoformat(value[:-1]+"+00:00")
    except ValueError as exc:raise CandidateKnowledgeSetError(f"{label}_invalid") from exc

def canonical_receipt_bytes(document:Mapping[str,Any])->bytes:return canonical_json_bytes(document)
def calculate_receipt_sha256(document:Mapping[str,Any])->str:
    value=deepcopy(dict(document)); value["integrity"]["receipt_sha256"]=""; return hashlib.sha256(canonical_receipt_bytes(value)).hexdigest()
def validate_candidate_receipt(document:Mapping[str,Any])->dict[str,Any]:
    root=_closed(dict(document),_RECEIPT,"root")
    if root["schema_version"]!="0.1":_fail("schema_version_invalid")
    identity=_closed(root["identity"],_IDENTITY,"identity");_token(identity["receipt_id"],"receipt_id");_time(identity["applied_at"],"applied_at")
    if identity["status"]!="candidate_pending_review":_fail("status_invalid")
    for section,fields in (("source_bindings",_SOURCE),("candidate_bindings",_CANDIDATE)):
        value=_closed(root[section],fields,section)
        for item in fields:
            if not isinstance(value[item],str) or _SHA.fullmatch(value[item]) is None:_fail(f"{item}_invalid")
    consumption=_closed(root["consumption"],_CONSUMPTION,"consumption");_token(consumption["decision_id"],"decision_id");_token(consumption["proposal_id"],"proposal_id")
    if consumption["single_use_pending_durable_record"] is not True:_fail("single_use_state_invalid")
    integrity=_closed(root["integrity"],_INTEGRITY,"integrity")
    if integrity["hash_algorithm"]!="sha256" or not isinstance(integrity["receipt_sha256"],str) or _SHA.fullmatch(integrity["receipt_sha256"]) is None:_fail("integrity_invalid")
    if calculate_receipt_sha256(root)!=integrity["receipt_sha256"]:_fail("receipt_sha256_mismatch")
    return deepcopy(root)

def build_candidate_knowledge_set(source_envelope:Mapping[str,Any],source_catalog:Mapping[str,Any],proposal:Mapping[str,Any],decision:Mapping[str,Any],physical_mapping:Mapping[str,Mapping[str,Any]],context:CandidateContext)->dict[str,Any]:
    envelope=validate_knowledge_envelope(source_envelope); catalog=validate_static_template_catalog(source_catalog); proposal_value=validate_catalog_change_proposal(proposal)
    outcome=evaluate_proposal_review(proposal_value,decision)
    if outcome.status!="decision_eligible":_fail(f"review_{outcome.reason or outcome.status}")
    if proposal_value["binding"]["catalog_sha256"]!=catalog["integrity"]["catalog_sha256"]:_fail("catalog_binding_mismatch")
    source_envelope_bytes=canonical_json_bytes(envelope); source_envelope_sha=hashlib.sha256(source_envelope_bytes).hexdigest()
    matching=[entry for entry in catalog["entries"] if entry["envelope_sha256"]==source_envelope_sha and entry["index"]["class_id"]==proposal_value["subject"]["class_id"] and entry["index"]["specialization_id"]==proposal_value["subject"]["specialization_id"] and entry["index"]["role"]==proposal_value["subject"]["role"]]
    if len(matching)!=1:_fail("source_entry_mismatch")
    if not isinstance(physical_mapping,Mapping) or not physical_mapping:_fail("physical_mapping_invalid")
    normalized={}
    for field,raw in physical_mapping.items():
        _token(field,"mapping_field"); rule=_closed(dict(raw),{"statement_order","before_text_key","after_text_key","update_references"},"mapping_rule")
        if isinstance(rule["statement_order"],bool) or not isinstance(rule["statement_order"],int) or rule["statement_order"]<1:_fail("statement_order_invalid")
        _token(rule["before_text_key"],"before_text_key");_token(rule["after_text_key"],"after_text_key")
        if not isinstance(rule["update_references"],bool):_fail("update_references_invalid")
        normalized[field]=rule
    candidate_envelope=deepcopy(envelope)
    for operation in proposal_value["operations"]:
        if operation["action"]!="replace" or operation["catalog_field"] not in normalized:_fail("operation_not_mapped")
        rule=normalized[operation["catalog_field"]]; statements=candidate_envelope["guidance"]["statements"]
        if rule["statement_order"]>len(statements):_fail("statement_missing")
        statement=statements[rule["statement_order"]-1]
        if statement["text_key"]!=rule["before_text_key"]:_fail("physical_before_mismatch")
        statement["text_key"]=rule["after_text_key"]
        if rule["update_references"]:
            for existing in statements:
                existing["alternatives"]=[rule["after_text_key"] if value==rule["before_text_key"] else value for value in existing["alternatives"]]
        elif any(rule["before_text_key"] in existing["alternatives"] for existing in statements):
            _fail("stale_reference")
    if context.applied_at.tzinfo is None or context.applied_at.utcoffset()!=timezone.utc.utcoffset(context.applied_at):_fail("applied_at_invalid")
    for value,label in ((context.package_id,"package_id"),(context.entry_id,"entry_id")):_token(value,label)
    if _VERSION.fullmatch(context.content_version) is None:_fail("content_version_invalid")
    if not context.envelope_path.startswith("knowledge/fixtures/") or not context.envelope_path.endswith(".json") or ".." in context.envelope_path or "\\" in context.envelope_path:_fail("envelope_path_invalid")
    timestamp=context.applied_at.isoformat().replace("+00:00","Z")
    candidate_envelope["identity"].update({"package_id":context.package_id,"content_version":context.content_version,"created_at":timestamp})
    candidate_envelope["evidence"]["source_ids"]=sorted(set(candidate_envelope["evidence"]["source_ids"]+[proposal_value["identity"]["proposal_id"],decision["identity"]["decision_id"]]))
    candidate_envelope["evidence"]["source_hashes"]={"proposal":proposal_value["integrity"]["proposal_sha256"],"review_decision":calculate_decision_sha256(decision)}
    candidate_envelope["evidence"]["limitations"]=sorted(set(candidate_envelope["evidence"]["limitations"]+["candidate_pending_review"]))
    candidate_envelope["integrity"].update({"payload_sha256":"","signature":None,"signature_algorithm":"placeholder-none"});candidate_envelope["integrity"]["payload_sha256"]=calculate_payload_sha256(candidate_envelope);candidate_envelope=validate_knowledge_envelope(candidate_envelope)
    candidate_envelope_sha=hashlib.sha256(canonical_json_bytes(candidate_envelope)).hexdigest()
    candidate_catalog=deepcopy(catalog);candidate_catalog["identity"].update({"content_version":context.content_version,"created_at":timestamp})
    source_entry=matching[0]; new_entry=deepcopy(source_entry);new_entry.update({"entry_id":context.entry_id,"envelope_path":context.envelope_path,"envelope_sha256":candidate_envelope_sha,"lifecycle_state":"pending_review","review":{"decision_id":None,"reviewer_id":None,"decided_at":None,"notes":["candidate_pending_review"],"prior_approval_decision_id":None,"transition_reason":None},"supersedes_entry_ids":[source_entry["entry_id"]],"invalidation_reasons":[],"source_coverage_complete":False});new_entry["role_policy"]["dynamic_safety_satisfied"]=False
    candidate_catalog["entries"].append(new_entry);candidate_catalog["integrity"]["catalog_sha256"]="";candidate_catalog["integrity"]["catalog_sha256"]=calculate_catalog_sha256(candidate_catalog);candidate_catalog=validate_static_template_catalog(candidate_catalog)
    receipt={"schema_version":"0.1","identity":{"receipt_id":f"receipt.{decision['identity']['decision_id']}","applied_at":timestamp,"status":"candidate_pending_review"},"source_bindings":{"source_envelope_sha256":source_envelope_sha,"source_catalog_sha256":catalog["integrity"]["catalog_sha256"],"proposal_sha256":proposal_value["integrity"]["proposal_sha256"],"decision_sha256":calculate_decision_sha256(decision)},"candidate_bindings":{"candidate_envelope_sha256":candidate_envelope_sha,"candidate_catalog_sha256":candidate_catalog["integrity"]["catalog_sha256"]},"consumption":{"decision_id":decision["identity"]["decision_id"],"proposal_id":proposal_value["identity"]["proposal_id"],"single_use_pending_durable_record":True},"integrity":{"hash_algorithm":"sha256","receipt_sha256":""}};receipt["integrity"]["receipt_sha256"]=calculate_receipt_sha256(receipt);receipt=validate_candidate_receipt(receipt)
    return {"schema_version":"0.1","candidate_envelope":candidate_envelope,"candidate_catalog":candidate_catalog,"receipt":receipt}
