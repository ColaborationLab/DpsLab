"""Pure human review decisions for exact durable candidate generations."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import re
from typing import Any, Mapping

from .candidate_knowledge_set import canonical_receipt_bytes, validate_candidate_receipt
from .candidate_knowledge_store import validate_candidate_commit
from .catalog_change_proposal import validate_catalog_change_proposal
from .knowledge_envelope import canonical_json_bytes, validate_knowledge_envelope
from .proposal_review import calculate_decision_sha256, validate_proposal_review_decision
from .static_template_catalog import canonical_catalog_bytes, validate_static_template_catalog

class CandidateKnowledgeReviewError(ValueError): pass

@dataclass(frozen=True)
class CandidateReviewContext:
    decision_id: str; reviewer_id: str; authority_reference: str; human_attestation_id: str
    reviewed_at: datetime; wow_build: int; interface: int; outcome: str
    freshness: str; applicability: str; source_coverage: str; role_safety: str
    reason_codes: tuple[str, ...]; limitations_acknowledged: tuple[str, ...]

@dataclass(frozen=True)
class CandidateReviewOutcome:
    status: str; reason: str | None; decision_id: str | None; generation_id: str | None

_TOKEN=re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$"); _SHA=re.compile(r"^[0-9a-f]{64}$")
_ROOT={"schema_version","identity","binding","assessment","decision","integrity"}; _IDENTITY={"decision_id","created_at"}
_BINDING={"generation_id","marker_sha256","commit_sha256","candidate_envelope_sha256","candidate_catalog_sha256","receipt_sha256","source_envelope_sha256","source_catalog_sha256","proposal_sha256","proposal_decision_sha256"}
_ASSESSMENT={"wow_build","interface","role","freshness","applicability","source_coverage","role_safety","no_automation_confirmed"}
_DECISION={"outcome","reviewer_id","authority_reference","human_attestation_id","decided_at","reason_codes","limitations_acknowledged"}; _INTEGRITY={"hash_algorithm","decision_sha256"}
_GENERATION={"marker","commit","candidate_envelope","candidate_catalog","receipt","source_envelope","source_catalog","proposal","proposal_decision"}; _MARKER={"schema_version","generation_id","commit_sha256"}

def _fail(reason:str)->None: raise CandidateKnowledgeReviewError(reason)
def _closed(value:Any,fields:set[str],label:str)->dict[str,Any]:
    if not isinstance(value,dict) or set(value)!=fields:_fail(f"{label}_fields_invalid")
    return value
def _token(value:Any,label:str)->str:
    if not isinstance(value,str) or _TOKEN.fullmatch(value) is None:_fail(f"{label}_invalid")
    return value
def _time(value:Any,label:str)->datetime:
    if not isinstance(value,str) or not value.endswith("Z"):_fail(f"{label}_invalid")
    try:parsed=datetime.fromisoformat(value[:-1]+"+00:00")
    except ValueError as exc:raise CandidateKnowledgeReviewError(f"{label}_invalid") from exc
    if parsed.utcoffset()!=timezone.utc.utcoffset(parsed):_fail(f"{label}_invalid")
    return parsed
def _tokens(value:Any,label:str)->tuple[str,...]:
    if not isinstance(value,list) or not value:_fail(f"{label}_invalid")
    result=tuple(_token(item,label) for item in value)
    if len(result)!=len(set(result)):_fail(f"{label}_duplicate")
    return result

def canonical_review_decision_bytes(document:Mapping[str,Any])->bytes:return canonical_json_bytes(document)
def calculate_review_decision_sha256(document:Mapping[str,Any])->str:
    value=deepcopy(dict(document));value["integrity"]["decision_sha256"]="";return hashlib.sha256(canonical_review_decision_bytes(value)).hexdigest()

def validate_candidate_review_decision(document:Mapping[str,Any])->dict[str,Any]:
    root=_closed(dict(document),_ROOT,"root")
    if root["schema_version"]!="0.1":_fail("schema_version_invalid")
    identity=_closed(root["identity"],_IDENTITY,"identity");_token(identity["decision_id"],"decision_id");created=_time(identity["created_at"],"created_at")
    binding=_closed(root["binding"],_BINDING,"binding");_token(binding["generation_id"],"generation_id")
    for field in _BINDING-{"generation_id"}:
        if not isinstance(binding[field],str) or _SHA.fullmatch(binding[field]) is None:_fail(f"{field}_invalid")
    assessment=_closed(root["assessment"],_ASSESSMENT,"assessment")
    for field in ("wow_build","interface"):
        if isinstance(assessment[field],bool) or not isinstance(assessment[field],int) or assessment[field]<1:_fail(f"{field}_invalid")
    if assessment["role"] not in {"damage","tank","healer"}:_fail("role_invalid")
    allowed={"freshness":{"current","stale","unknown"},"applicability":{"applicable","inapplicable","unknown"},"source_coverage":{"complete","incomplete","unknown"},"role_safety":{"satisfied","unsatisfied","unknown"}}
    for field,values in allowed.items():
        if assessment[field] not in values:_fail(f"{field}_invalid")
    if not isinstance(assessment["no_automation_confirmed"],bool):_fail("no_automation_confirmed_invalid")
    decision=_closed(root["decision"],_DECISION,"decision")
    if decision["outcome"] not in {"approved","rejected"}:_fail("outcome_invalid")
    for field in ("reviewer_id","authority_reference","human_attestation_id"):_token(decision[field],field)
    if _time(decision["decided_at"],"decided_at")!=created:_fail("decision_time_mismatch")
    _tokens(decision["reason_codes"],"reason_code");_tokens(decision["limitations_acknowledged"],"limitation")
    positives=("current","applicable","complete","satisfied",True);actual=tuple(assessment[field] for field in ("freshness","applicability","source_coverage","role_safety","no_automation_confirmed"))
    if decision["outcome"]=="approved" and actual!=positives:_fail("approved_assessment_not_satisfied")
    integrity=_closed(root["integrity"],_INTEGRITY,"integrity")
    if integrity["hash_algorithm"]!="sha256" or not isinstance(integrity["decision_sha256"],str) or _SHA.fullmatch(integrity["decision_sha256"]) is None:_fail("integrity_invalid")
    if calculate_review_decision_sha256(root)!=integrity["decision_sha256"]:_fail("decision_sha256_mismatch")
    return deepcopy(root)

def _validated_generation(value:Mapping[str,Any])->tuple[dict[str,Any],dict[str,Any],dict[str,Any],dict[str,Any],dict[str,Any]]:
    root=_closed(dict(value),_GENERATION,"generation");marker=_closed(root["marker"],_MARKER,"marker")
    if marker["schema_version"]!="0.1":_fail("marker_schema_invalid")
    _token(marker["generation_id"],"generation_id")
    if not isinstance(marker["commit_sha256"],str) or _SHA.fullmatch(marker["commit_sha256"]) is None:_fail("marker_sha_invalid")
    try:
        commit=validate_candidate_commit(root["commit"]);envelope=validate_knowledge_envelope(root["candidate_envelope"]);catalog=validate_static_template_catalog(root["candidate_catalog"]);receipt=validate_candidate_receipt(root["receipt"])
        source_envelope=validate_knowledge_envelope(root["source_envelope"]);source_catalog=validate_static_template_catalog(root["source_catalog"]);proposal=validate_catalog_change_proposal(root["proposal"]);proposal_decision=validate_proposal_review_decision(root["proposal_decision"])
    except (TypeError,ValueError) as exc:raise CandidateKnowledgeReviewError("generation_validation_failed") from exc
    if marker["generation_id"]!=commit["identity"]["generation_id"] or marker["commit_sha256"]!=commit["integrity"]["commit_sha256"]:_fail("marker_commit_mismatch")
    hashes={"candidate_envelope_sha256":hashlib.sha256(canonical_json_bytes(envelope)).hexdigest(),"candidate_catalog_sha256":hashlib.sha256(canonical_catalog_bytes(catalog)).hexdigest(),"receipt_sha256":hashlib.sha256(canonical_receipt_bytes(receipt)).hexdigest()}
    if commit["bindings"]!=hashes:_fail("commit_binding_mismatch")
    if receipt["candidate_bindings"]["candidate_envelope_sha256"]!=hashes["candidate_envelope_sha256"] or receipt["candidate_bindings"]["candidate_catalog_sha256"]!=catalog["integrity"]["catalog_sha256"]:_fail("receipt_candidate_mismatch")
    source_hashes={"source_envelope_sha256":hashlib.sha256(canonical_json_bytes(source_envelope)).hexdigest(),"source_catalog_sha256":source_catalog["integrity"]["catalog_sha256"],"proposal_sha256":proposal["integrity"]["proposal_sha256"],"decision_sha256":calculate_decision_sha256(proposal_decision)}
    if receipt["source_bindings"]!=source_hashes:_fail("source_evidence_mismatch")
    candidates=[entry for entry in catalog["entries"] if entry["envelope_sha256"]==hashes["candidate_envelope_sha256"]]
    if len(candidates)!=1 or candidates[0]["lifecycle_state"]!="pending_review":_fail("candidate_entry_mismatch")
    return marker,commit,envelope,catalog,receipt

def _expected_binding(generation:Mapping[str,Any])->tuple[dict[str,Any],dict[str,Any],dict[str,Any]]:
    marker,commit,envelope,catalog,receipt=_validated_generation(generation)
    binding={"generation_id":commit["identity"]["generation_id"],"marker_sha256":hashlib.sha256(canonical_json_bytes(marker)).hexdigest(),"commit_sha256":commit["integrity"]["commit_sha256"],"candidate_envelope_sha256":hashlib.sha256(canonical_json_bytes(envelope)).hexdigest(),"candidate_catalog_sha256":hashlib.sha256(canonical_catalog_bytes(catalog)).hexdigest(),"receipt_sha256":hashlib.sha256(canonical_receipt_bytes(receipt)).hexdigest(),"source_envelope_sha256":receipt["source_bindings"]["source_envelope_sha256"],"source_catalog_sha256":receipt["source_bindings"]["source_catalog_sha256"],"proposal_sha256":receipt["source_bindings"]["proposal_sha256"],"proposal_decision_sha256":receipt["source_bindings"]["decision_sha256"]}
    return binding,envelope,catalog

def build_candidate_review_decision(generation:Mapping[str,Any],context:CandidateReviewContext)->dict[str,Any]:
    binding,envelope,catalog=_expected_binding(generation)
    if context.reviewed_at.tzinfo is None or context.reviewed_at.utcoffset()!=timezone.utc.utcoffset(context.reviewed_at):_fail("reviewed_at_invalid")
    for field in ("decision_id","reviewer_id","authority_reference","human_attestation_id"):_token(getattr(context,field),field)
    if context.outcome not in {"approved","rejected"}:_fail("outcome_invalid")
    candidate=next(entry for entry in catalog["entries"] if entry["envelope_sha256"]==binding["candidate_envelope_sha256"]);role=envelope["subject"]["role"]
    if candidate["index"]["role"]!=role:_fail("role_mismatch")
    compatibility=envelope["compatibility"];applicable=compatibility["build_min"]<=context.wow_build<=compatibility["build_max"] and compatibility["interface_min"]<=context.interface<=compatibility["interface_max"]
    if context.outcome=="approved" and not applicable:_fail("build_not_applicable")
    committed=_time(generation["commit"]["identity"]["committed_at"],"committed_at")
    if context.reviewed_at<committed:_fail("decision_predates_commit")
    if not set(envelope["evidence"]["limitations"])<=set(context.limitations_acknowledged):_fail("limitations_not_acknowledged")
    required_role_reason={"damage":"damage.contextual_dps","tank":"tank.survival_first","healer":"healer.allies_first"}[role]
    if context.outcome=="approved" and required_role_reason not in context.reason_codes:_fail("role_reason_missing")
    timestamp=context.reviewed_at.isoformat().replace("+00:00","Z")
    decision={"schema_version":"0.1","identity":{"decision_id":context.decision_id,"created_at":timestamp},"binding":binding,"assessment":{"wow_build":context.wow_build,"interface":context.interface,"role":role,"freshness":context.freshness,"applicability":context.applicability,"source_coverage":context.source_coverage,"role_safety":context.role_safety,"no_automation_confirmed":envelope["safety"]["no_automation"] is True},"decision":{"outcome":context.outcome,"reviewer_id":context.reviewer_id,"authority_reference":context.authority_reference,"human_attestation_id":context.human_attestation_id,"decided_at":timestamp,"reason_codes":list(context.reason_codes),"limitations_acknowledged":list(context.limitations_acknowledged)},"integrity":{"hash_algorithm":"sha256","decision_sha256":""}}
    decision["integrity"]["decision_sha256"]=calculate_review_decision_sha256(decision);return validate_candidate_review_decision(decision)

def evaluate_candidate_review(generation:Mapping[str,Any],decision:Mapping[str,Any])->CandidateReviewOutcome:
    binding,envelope,_=_expected_binding(generation);value=validate_candidate_review_decision(decision)
    if value["binding"]!=binding:return CandidateReviewOutcome("review_unavailable","binding_mismatch",None,None)
    committed=_time(generation["commit"]["identity"]["committed_at"],"committed_at");decided=_time(value["decision"]["decided_at"],"decided_at")
    if decided<committed:return CandidateReviewOutcome("review_unavailable","decision_predates_commit",value["identity"]["decision_id"],binding["generation_id"])
    if not set(envelope["evidence"]["limitations"])<=set(value["decision"]["limitations_acknowledged"]):return CandidateReviewOutcome("review_unavailable","limitations_not_acknowledged",value["identity"]["decision_id"],binding["generation_id"])
    assessment=value["assessment"]
    required_role_reason={"damage":"damage.contextual_dps","tank":"tank.survival_first","healer":"healer.allies_first"}[assessment["role"]]
    if value["decision"]["outcome"]=="approved" and required_role_reason not in value["decision"]["reason_codes"]:return CandidateReviewOutcome("review_unavailable","role_reason_missing",value["identity"]["decision_id"],binding["generation_id"])
    compatibility=envelope["compatibility"]
    if value["decision"]["outcome"]=="approved" and not (compatibility["build_min"]<=assessment["wow_build"]<=compatibility["build_max"] and compatibility["interface_min"]<=assessment["interface"]<=compatibility["interface_max"]):return CandidateReviewOutcome("review_unavailable","build_not_applicable",value["identity"]["decision_id"],binding["generation_id"])
    status="review_eligible_for_publication" if value["decision"]["outcome"]=="approved" else "review_rejected"
    return CandidateReviewOutcome(status,None,value["identity"]["decision_id"],binding["generation_id"])
