"""Pure validation of human review decisions bound to exact proposals."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
import hashlib, json, re
from typing import Any, Mapping

from .catalog_change_proposal import validate_catalog_change_proposal


class ProposalReviewError(ValueError): pass

@dataclass(frozen=True)
class ReviewOutcome:
    status: str
    reason: str | None
    decision_id: str | None
    proposal_id: str | None

_TOKEN=re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$"); _SHA=re.compile(r"^[0-9a-f]{64}$")
_ROOT={"schema_version","identity","binding","decision","integrity"}
_IDENTITY={"decision_id","created_at"}
_BINDING={"proposal_id","proposal_sha256","catalog_sha256","evidence_sha256"}
_DECISION={"outcome","reviewer_id","authority_reference","decided_at","reason_codes","limitations_acknowledged"}
_INTEGRITY={"hash_algorithm","decision_sha256"}

def _fail(reason:str)->None: raise ProposalReviewError(reason)
def _closed(value:Any,fields:set[str],label:str)->dict[str,Any]:
    if not isinstance(value,dict) or set(value)!=fields: _fail(f"{label}_fields_invalid")
    return value
def _token(value:Any,label:str)->str:
    if not isinstance(value,str) or _TOKEN.fullmatch(value) is None: _fail(f"{label}_invalid")
    return value
def _time(value:Any,label:str)->datetime:
    if not isinstance(value,str) or not value.endswith("Z"): _fail(f"{label}_invalid")
    try: return datetime.fromisoformat(value[:-1]+"+00:00")
    except ValueError as exc: raise ProposalReviewError(f"{label}_invalid") from exc
def _tokens(value:Any,label:str)->tuple[str,...]:
    if not isinstance(value,list) or not value: _fail(f"{label}_invalid")
    result=tuple(_token(x,label) for x in value)
    if len(result)!=len(set(result)): _fail(f"{label}_duplicate")
    return result

def canonical_decision_bytes(document:Mapping[str,Any])->bytes:
    return (json.dumps(document,sort_keys=True,ensure_ascii=False,separators=(",", ":"))+"\n").encode("utf-8")
def calculate_decision_sha256(document:Mapping[str,Any])->str:
    projection=deepcopy(dict(document)); projection["integrity"]["decision_sha256"]=""
    return hashlib.sha256(canonical_decision_bytes(projection)).hexdigest()

def validate_proposal_review_decision(document:Mapping[str,Any])->dict[str,Any]:
    root=_closed(dict(document),_ROOT,"root")
    if root["schema_version"]!="0.1": _fail("schema_version_invalid")
    identity=_closed(root["identity"],_IDENTITY,"identity"); _token(identity["decision_id"],"decision_id"); created=_time(identity["created_at"],"created_at")
    binding=_closed(root["binding"],_BINDING,"binding"); _token(binding["proposal_id"],"proposal_id")
    for field in ("proposal_sha256","catalog_sha256","evidence_sha256"):
        if not isinstance(binding[field],str) or _SHA.fullmatch(binding[field]) is None: _fail(f"{field}_invalid")
    decision=_closed(root["decision"],_DECISION,"decision")
    if decision["outcome"] not in {"approved","rejected"}: _fail("outcome_invalid")
    for field in ("reviewer_id","authority_reference"): _token(decision[field],field)
    decided=_time(decision["decided_at"],"decided_at")
    if decided!=created: _fail("decision_time_mismatch")
    _tokens(decision["reason_codes"],"reason_code"); _tokens(decision["limitations_acknowledged"],"limitation")
    integrity=_closed(root["integrity"],_INTEGRITY,"integrity")
    if integrity["hash_algorithm"]!="sha256" or not isinstance(integrity["decision_sha256"],str) or _SHA.fullmatch(integrity["decision_sha256"]) is None: _fail("integrity_invalid")
    if calculate_decision_sha256(root)!=integrity["decision_sha256"]: _fail("decision_sha256_mismatch")
    return deepcopy(root)

def evaluate_proposal_review(proposal:Mapping[str,Any],decision:Mapping[str,Any],consumed_decision_ids:frozenset[str]=frozenset(),consumed_proposal_hashes:frozenset[str]=frozenset())->ReviewOutcome:
    proposal_value=validate_catalog_change_proposal(proposal); decision_value=validate_proposal_review_decision(decision)
    identity=proposal_value["identity"]; binding=decision_value["binding"]; review=decision_value["decision"]
    expected=(identity["proposal_id"],proposal_value["integrity"]["proposal_sha256"],proposal_value["binding"]["catalog_sha256"],proposal_value["binding"]["evidence_sha256"])
    actual=(binding["proposal_id"],binding["proposal_sha256"],binding["catalog_sha256"],binding["evidence_sha256"])
    if actual!=expected: return ReviewOutcome("decision_unavailable","binding_mismatch",None,None)
    required_limitations={value for operation in proposal_value["operations"] for value in operation["limitations"]}
    acknowledged=set(review["limitations_acknowledged"])
    if not required_limitations<=acknowledged:
        return ReviewOutcome("decision_unavailable","limitations_mismatch",decision_value["identity"]["decision_id"],binding["proposal_id"])
    decision_id=decision_value["identity"]["decision_id"]; proposal_hash=binding["proposal_sha256"]
    if decision_id in consumed_decision_ids or proposal_hash in consumed_proposal_hashes: return ReviewOutcome("decision_unavailable","replay_detected",decision_id,binding["proposal_id"])
    decided=_time(review["decided_at"],"decided_at")
    if not (_time(identity["created_at"],"proposal_created_at")<=decided<=_time(identity["expires_at"],"proposal_expires_at")): return ReviewOutcome("decision_unavailable","outside_validity_window",decision_id,binding["proposal_id"])
    status="decision_eligible" if review["outcome"]=="approved" else "decision_rejected"
    return ReviewOutcome(status,None,decision_id,binding["proposal_id"])
