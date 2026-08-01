"""Pure construction of review-only catalog change proposals."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Any, Mapping

from .patch_evidence import validate_patch_evidence
from .static_template_catalog import calculate_catalog_sha256, validate_static_template_catalog


class CatalogProposalError(ValueError):
    pass


@dataclass(frozen=True)
class ProposalContext:
    role: str
    class_id: int
    specialization_id: int
    content_contexts: tuple[str, ...]
    created_at: datetime
    expires_at: datetime
    max_evidence_age_seconds: int = 604800


_TOKEN = re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$")
_SHA = re.compile(r"^[0-9a-f]{64}$")
_ROOT = {"schema_version", "identity", "binding", "subject", "operations", "review", "integrity"}
_IDENTITY = {"proposal_id", "created_at", "expires_at", "status"}
_BINDING = {"catalog_id", "catalog_content_version", "catalog_sha256", "evidence_id", "evidence_sha256", "source_revision", "build_min", "build_max", "interface_min", "interface_max"}
_SUBJECT = {"role", "class_id", "specialization_id", "content_contexts"}
_OPERATION = {"operation_id", "parameter_family_id", "catalog_field", "action", "subject_tokens", "before_token", "after_token", "citation_token", "source_assertion_id", "limitations"}
_REVIEW = {"state", "decision_id", "reviewer_id", "decided_at"}
_INTEGRITY = {"hash_algorithm", "proposal_sha256"}


def _fail(reason: str) -> None: raise CatalogProposalError(reason)
def _closed(value: Any, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields: _fail(f"{label}_fields_invalid")
    return value
def _token(value: Any, label: str) -> str:
    if not isinstance(value, str) or _TOKEN.fullmatch(value) is None: _fail(f"{label}_invalid")
    return value
def _time(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"): _fail(f"{label}_invalid")
    try: parsed=datetime.fromisoformat(value[:-1]+"+00:00")
    except ValueError as exc: raise CatalogProposalError(f"{label}_invalid") from exc
    return parsed


def canonical_proposal_bytes(document: Mapping[str, Any]) -> bytes:
    return (json.dumps(document, sort_keys=True, ensure_ascii=False, separators=(",", ":"))+"\n").encode("utf-8")


def calculate_proposal_sha256(document: Mapping[str, Any]) -> str:
    projection=deepcopy(dict(document)); projection["integrity"]["proposal_sha256"]=""
    return hashlib.sha256(canonical_proposal_bytes(projection)).hexdigest()


def validate_catalog_change_proposal(document: Mapping[str, Any]) -> dict[str, Any]:
    root=_closed(dict(document),_ROOT,"root")
    if root["schema_version"]!="0.1": _fail("schema_version_invalid")
    identity=_closed(root["identity"],_IDENTITY,"identity")
    _token(identity["proposal_id"],"proposal_id"); created=_time(identity["created_at"],"created_at"); expires=_time(identity["expires_at"],"expires_at")
    if expires<=created: _fail("expiry_invalid")
    if identity["status"]!="pending_review": _fail("status_invalid")
    binding=_closed(root["binding"],_BINDING,"binding")
    for field in ("catalog_id","catalog_content_version","evidence_id","source_revision"): _token(binding[field],field)
    for field in ("catalog_sha256","evidence_sha256"):
        if not isinstance(binding[field],str) or _SHA.fullmatch(binding[field]) is None: _fail(f"{field}_invalid")
    for field in ("build_min","build_max","interface_min","interface_max"):
        if isinstance(binding[field],bool) or not isinstance(binding[field],int) or binding[field]<0: _fail(f"{field}_invalid")
    if binding["build_min"]>binding["build_max"] or binding["interface_min"]>binding["interface_max"]: _fail("range_invalid")
    subject=_closed(root["subject"],_SUBJECT,"subject")
    if subject["role"] not in {"damage","tank","healer"}: _fail("role_invalid")
    for field in ("class_id","specialization_id"):
        if isinstance(subject[field],bool) or not isinstance(subject[field],int) or subject[field]<1: _fail(f"{field}_invalid")
    if not isinstance(subject["content_contexts"],list) or not subject["content_contexts"]: _fail("content_contexts_invalid")
    for value in subject["content_contexts"]: _token(value,"content_context")
    if not isinstance(root["operations"],list) or not root["operations"]: _fail("operations_invalid")
    ids:set[str]=set(); targets:set[tuple[str,str]]=set()
    for raw in root["operations"]:
        op=_closed(raw,_OPERATION,"operation"); op_id=_token(op["operation_id"],"operation_id"); family=_token(op["parameter_family_id"],"parameter_family_id"); field=_token(op["catalog_field"],"catalog_field")
        if op_id in ids: _fail("operation_id_duplicate")
        ids.add(op_id)
        if (family,field) in targets: _fail("operation_conflict")
        targets.add((family,field))
        if op["action"] not in {"add","replace","remove","invalidate"}: _fail("action_invalid")
        if not isinstance(op["subject_tokens"],list) or not op["subject_tokens"]: _fail("subject_tokens_invalid")
        for value in op["subject_tokens"]: _token(value,"subject_token")
        for name in ("before_token","after_token"):
            if op[name] is not None: _token(op[name],name)
        if op["action"]=="add" and (op["before_token"] is not None or op["after_token"] is None): _fail("operation_values_invalid")
        if op["action"]=="replace" and (op["before_token"] is None or op["after_token"] is None or op["before_token"]==op["after_token"]): _fail("operation_values_invalid")
        if op["action"]=="remove" and (op["before_token"] is None or op["after_token"] is not None): _fail("operation_values_invalid")
        if op["action"]=="invalidate" and (op["before_token"] is not None or op["after_token"] is not None): _fail("operation_values_invalid")
        _token(op["citation_token"],"citation_token"); _token(op["source_assertion_id"],"source_assertion_id")
        if not isinstance(op["limitations"],list) or not op["limitations"]: _fail("limitations_invalid")
        for value in op["limitations"]: _token(value,"limitation")
    review=_closed(root["review"],_REVIEW,"review")
    if review!={"state":"pending_review","decision_id":None,"reviewer_id":None,"decided_at":None}: _fail("review_invalid")
    integrity=_closed(root["integrity"],_INTEGRITY,"integrity")
    if integrity["hash_algorithm"]!="sha256" or not isinstance(integrity["proposal_sha256"],str) or _SHA.fullmatch(integrity["proposal_sha256"]) is None: _fail("integrity_invalid")
    if calculate_proposal_sha256(root)!=integrity["proposal_sha256"]: _fail("proposal_sha256_mismatch")
    return deepcopy(root)


def build_catalog_change_proposal(evidence: Mapping[str, Any], catalog: Mapping[str, Any], family_to_field: Mapping[str,str], context: ProposalContext) -> dict[str,Any]:
    evidence_value=validate_patch_evidence(evidence); catalog_value=validate_static_template_catalog(catalog)
    if evidence_value["identity"]["lifecycle"]!="current": _fail("historical_evidence")
    if not isinstance(family_to_field,Mapping) or not family_to_field: _fail("mapping_invalid")
    mapping={_token(k,"mapping_family"):_token(v,"mapping_field") for k,v in family_to_field.items()}
    if context.role not in {"damage","tank","healer"}: _fail("context_role_invalid")
    if context.created_at.tzinfo is None or context.created_at.utcoffset()!=timezone.utc.utcoffset(context.created_at) or context.expires_at<=context.created_at: _fail("context_time_invalid")
    if context.class_id<1 or context.specialization_id<1 or not context.content_contexts or len(context.content_contexts)!=len(set(context.content_contexts)): _fail("context_subject_invalid")
    if isinstance(context.max_evidence_age_seconds,bool) or not isinstance(context.max_evidence_age_seconds,int) or context.max_evidence_age_seconds<1: _fail("evidence_age_policy_invalid")
    assertions=evidence_value["assertions"]
    families={item["parameter_family_id"] for item in assertions}
    if any(item["certainty"]!="exact" for item in assertions): _fail("ambiguous_evidence")
    referenced=families|{family for item in assertions for family in item["invalidation_families"]}
    if not referenced<=set(mapping): _fail("unknown_family")
    if context.role in {"tank","healer"} and "synthetic.role.damage" in families and "synthetic.role.safety" not in families: _fail("safety_evidence_missing")
    evidence_created=_time(evidence_value["identity"]["created_at"],"evidence_created_at")
    age=(context.created_at-evidence_created).total_seconds()
    if age<0 or age>context.max_evidence_age_seconds: _fail("evidence_stale")
    source=evidence_value["source"]
    matching_entries=[entry for entry in catalog_value["entries"] if entry["index"]["role"]==context.role and entry["index"]["class_id"]==context.class_id and entry["index"]["specialization_id"]==context.specialization_id and set(context.content_contexts)<=set(entry["index"]["content_contexts"]) and entry["index"]["build_min"]<=source["build_min"]<=source["build_max"]<=entry["index"]["build_max"] and entry["index"]["interface_min"]<=source["interface_min"]<=source["interface_max"]<=entry["index"]["interface_max"]]
    if len(matching_entries)!=1: _fail("catalog_subject_mismatch")
    action_map={"add":"add","change":"replace","remove":"remove","invalidate":"invalidate"}
    operations=[]
    for item in assertions:
        operations.append({"operation_id":f"proposal.{item['assertion_id']}","parameter_family_id":item["parameter_family_id"],"catalog_field":mapping[item["parameter_family_id"]],"action":action_map[item["operation"]],"subject_tokens":sorted(item["subject_tokens"]),"before_token":item["old_token"],"after_token":item["new_token"],"citation_token":item["citation_token"],"source_assertion_id":item["assertion_id"],"limitations":["requires_human_review","synthetic_fixture_only"]})
        for family in item["invalidation_families"]:
            operations.append({"operation_id":f"proposal.{item['assertion_id']}.invalidate.{family}","parameter_family_id":family,"catalog_field":mapping[family],"action":"invalidate","subject_tokens":sorted(item["subject_tokens"]),"before_token":None,"after_token":None,"citation_token":item["citation_token"],"source_assertion_id":item["assertion_id"],"limitations":["requires_human_review","synthetic_fixture_only"]})
    if not operations: _fail("no_operations")
    proposal={"schema_version":"0.1","identity":{"proposal_id":f"proposal.{evidence_value['identity']['evidence_id']}","created_at":context.created_at.isoformat().replace("+00:00","Z"),"expires_at":context.expires_at.isoformat().replace("+00:00","Z"),"status":"pending_review"},"binding":{"catalog_id":catalog_value["identity"]["catalog_id"],"catalog_content_version":catalog_value["identity"]["content_version"],"catalog_sha256":calculate_catalog_sha256(catalog_value),"evidence_id":evidence_value["identity"]["evidence_id"],"evidence_sha256":evidence_value["integrity"]["evidence_sha256"],"source_revision":source["source_revision"],"build_min":source["build_min"],"build_max":source["build_max"],"interface_min":source["interface_min"],"interface_max":source["interface_max"]},"subject":{"role":context.role,"class_id":context.class_id,"specialization_id":context.specialization_id,"content_contexts":sorted(context.content_contexts)},"operations":sorted(operations,key=lambda x:x["operation_id"]),"review":{"state":"pending_review","decision_id":None,"reviewer_id":None,"decided_at":None},"integrity":{"hash_algorithm":"sha256","proposal_sha256":""}}
    proposal["integrity"]["proposal_sha256"]=calculate_proposal_sha256(proposal)
    return validate_catalog_change_proposal(proposal)
