"""Pure construction of unsigned reviewed candidate release bundles."""

from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime,timezone
import hashlib,re
from typing import Any,Mapping

from .candidate_knowledge_review import (canonical_review_decision_bytes,evaluate_candidate_review,validate_candidate_review_decision)
from .knowledge_envelope import canonical_json_bytes,validate_knowledge_envelope
from .static_template_catalog import calculate_catalog_sha256,canonical_catalog_bytes,validate_static_template_catalog

class CandidateReleaseBundleError(ValueError):pass

@dataclass(frozen=True)
class ReleaseBundleContext:
    bundle_id:str
    created_at:datetime
    target_channel:str
    content_version:str

_TOKEN=re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$");_SHA=re.compile(r"^[0-9a-f]{64}$");_VERSION=re.compile(r"^(?:0|[1-9][0-9]*)(?:\.[0-9]+){0,3}$")
_BUNDLE={"schema_version","release_envelope","release_catalog","review_decision","manifest"}
_MANIFEST={"schema_version","identity","compatibility","bindings","integrity"};_IDENTITY={"bundle_id","created_at","status","target_channel","content_version"}
_COMPAT={"wow_product","build_min","build_max","interface_min","interface_max"};_BINDINGS={"generation_id","candidate_commit_sha256","candidate_marker_sha256","review_decision_sha256","release_envelope_sha256","release_catalog_sha256"};_INTEGRITY={"hash_algorithm","manifest_sha256"}

def _fail(reason:str)->None:raise CandidateReleaseBundleError(reason)
def _closed(value:Any,fields:set[str],label:str)->dict[str,Any]:
    if not isinstance(value,dict) or set(value)!=fields:_fail(f"{label}_fields_invalid")
    return value
def _token(value:Any,label:str)->str:
    if not isinstance(value,str) or _TOKEN.fullmatch(value) is None:_fail(f"{label}_invalid")
    return value
def _time(value:Any,label:str)->datetime:
    if not isinstance(value,str) or not value.endswith("Z"):_fail(f"{label}_invalid")
    try:parsed=datetime.fromisoformat(value[:-1]+"+00:00")
    except ValueError as exc:raise CandidateReleaseBundleError(f"{label}_invalid") from exc
    if parsed.utcoffset()!=timezone.utc.utcoffset(parsed):_fail(f"{label}_invalid")
    return parsed
def _integer(value:Any,label:str)->int:
    if isinstance(value,bool) or not isinstance(value,int) or value<1:_fail(f"{label}_invalid")
    return value

def canonical_release_manifest_bytes(document:Mapping[str,Any])->bytes:return canonical_json_bytes(document)
def calculate_release_manifest_sha256(document:Mapping[str,Any])->str:
    value=deepcopy(dict(document));value["integrity"]["manifest_sha256"]="";return hashlib.sha256(canonical_release_manifest_bytes(value)).hexdigest()

def validate_release_manifest(document:Mapping[str,Any])->dict[str,Any]:
    root=_closed(dict(document),_MANIFEST,"manifest")
    if root["schema_version"]!="0.1":_fail("manifest_schema_invalid")
    identity=_closed(root["identity"],_IDENTITY,"identity");_token(identity["bundle_id"],"bundle_id");_time(identity["created_at"],"created_at")
    if identity["status"]!="signature_pending":_fail("manifest_status_invalid")
    if identity["target_channel"] not in {"stable","beta"}:_fail("target_channel_invalid")
    if not isinstance(identity["content_version"],str) or _VERSION.fullmatch(identity["content_version"]) is None:_fail("content_version_invalid")
    compat=_closed(root["compatibility"],_COMPAT,"compatibility")
    if compat["wow_product"]!="retail":_fail("wow_product_invalid")
    for field in _COMPAT-{"wow_product"}:_integer(compat[field],field)
    if compat["build_min"]>compat["build_max"] or compat["interface_min"]>compat["interface_max"]:_fail("compatibility_range_invalid")
    bindings=_closed(root["bindings"],_BINDINGS,"bindings");_token(bindings["generation_id"],"generation_id")
    for field in _BINDINGS-{"generation_id"}:
        if not isinstance(bindings[field],str) or _SHA.fullmatch(bindings[field]) is None:_fail(f"{field}_invalid")
    integrity=_closed(root["integrity"],_INTEGRITY,"integrity")
    if integrity["hash_algorithm"]!="sha256" or not isinstance(integrity["manifest_sha256"],str) or _SHA.fullmatch(integrity["manifest_sha256"]) is None:_fail("manifest_integrity_invalid")
    if calculate_release_manifest_sha256(root)!=integrity["manifest_sha256"]:_fail("manifest_sha256_mismatch")
    return deepcopy(root)

def build_candidate_release_bundle(generation:Mapping[str,Any],review_decision:Mapping[str,Any],context:ReleaseBundleContext)->dict[str,Any]:
    outcome=evaluate_candidate_review(generation,review_decision)
    if outcome.status!="review_eligible_for_publication":_fail(f"review_{outcome.reason or outcome.status}")
    decision=validate_candidate_review_decision(review_decision);envelope=validate_knowledge_envelope(generation["candidate_envelope"]);catalog=validate_static_template_catalog(generation["candidate_catalog"])
    if context.created_at.tzinfo is None or context.created_at.utcoffset()!=timezone.utc.utcoffset(context.created_at):_fail("created_at_invalid")
    _token(context.bundle_id,"bundle_id")
    if context.target_channel not in {"stable","beta"} or context.target_channel!=envelope["identity"]["channel"] or context.target_channel!=catalog["identity"]["channel"]:_fail("target_channel_mismatch")
    if not isinstance(context.content_version,str) or _VERSION.fullmatch(context.content_version) is None or context.content_version!=envelope["identity"]["content_version"] or context.content_version!=catalog["identity"]["content_version"]:_fail("content_version_mismatch")
    if context.created_at<_time(decision["decision"]["decided_at"],"decided_at"):_fail("release_predates_review")
    release_envelope=deepcopy(envelope);release_catalog=deepcopy(catalog);envelope_sha=hashlib.sha256(canonical_json_bytes(release_envelope)).hexdigest()
    matching=[entry for entry in release_catalog["entries"] if entry["envelope_sha256"]==envelope_sha]
    if len(matching)!=1 or matching[0]["lifecycle_state"]!="pending_review":_fail("candidate_entry_mismatch")
    entry=matching[0];entry["lifecycle_state"]="approved";entry["review"]={"decision_id":decision["identity"]["decision_id"],"reviewer_id":decision["decision"]["reviewer_id"],"decided_at":decision["decision"]["decided_at"],"notes":list(decision["decision"]["reason_codes"]),"prior_approval_decision_id":None,"transition_reason":None};entry["source_coverage_complete"]=True;entry["role_policy"]["dynamic_safety_satisfied"]=True
    timestamp=context.created_at.isoformat().replace("+00:00","Z");release_catalog["identity"]["created_at"]=timestamp;release_catalog["integrity"]["catalog_sha256"]="";release_catalog["integrity"]["catalog_sha256"]=calculate_catalog_sha256(release_catalog);release_catalog=validate_static_template_catalog(release_catalog)
    marker_sha=hashlib.sha256(canonical_json_bytes(generation["marker"])).hexdigest();catalog_sha=hashlib.sha256(canonical_catalog_bytes(release_catalog)).hexdigest();decision_sha=decision["integrity"]["decision_sha256"]
    compat=release_envelope["compatibility"]
    manifest={"schema_version":"0.1","identity":{"bundle_id":context.bundle_id,"created_at":timestamp,"status":"signature_pending","target_channel":context.target_channel,"content_version":context.content_version},"compatibility":{"wow_product":compat["wow_product"],"build_min":compat["build_min"],"build_max":compat["build_max"],"interface_min":compat["interface_min"],"interface_max":compat["interface_max"]},"bindings":{"generation_id":generation["commit"]["identity"]["generation_id"],"candidate_commit_sha256":generation["commit"]["integrity"]["commit_sha256"],"candidate_marker_sha256":marker_sha,"review_decision_sha256":decision_sha,"release_envelope_sha256":envelope_sha,"release_catalog_sha256":catalog_sha},"integrity":{"hash_algorithm":"sha256","manifest_sha256":""}}
    manifest["integrity"]["manifest_sha256"]=calculate_release_manifest_sha256(manifest)
    return validate_candidate_release_bundle({"schema_version":"0.1","release_envelope":release_envelope,"release_catalog":release_catalog,"review_decision":decision,"manifest":manifest})

def validate_candidate_release_bundle(document:Mapping[str,Any])->dict[str,Any]:
    root=_closed(dict(document),_BUNDLE,"bundle")
    if root["schema_version"]!="0.1":_fail("bundle_schema_invalid")
    try:envelope=validate_knowledge_envelope(root["release_envelope"]);catalog=validate_static_template_catalog(root["release_catalog"]);decision=validate_candidate_review_decision(root["review_decision"]);manifest=validate_release_manifest(root["manifest"])
    except (TypeError,ValueError) as exc:raise CandidateReleaseBundleError("bundle_member_invalid") from exc
    if envelope["integrity"]["signature"] is not None:_fail("release_envelope_must_remain_unsigned")
    envelope_sha=hashlib.sha256(canonical_json_bytes(envelope)).hexdigest();catalog_sha=hashlib.sha256(canonical_catalog_bytes(catalog)).hexdigest();bindings=manifest["bindings"]
    if bindings["release_envelope_sha256"]!=envelope_sha or bindings["release_catalog_sha256"]!=catalog_sha or bindings["review_decision_sha256"]!=decision["integrity"]["decision_sha256"]:_fail("bundle_binding_mismatch")
    matching=[entry for entry in catalog["entries"] if entry["envelope_sha256"]==envelope_sha]
    if len(matching)!=1 or matching[0]["lifecycle_state"]!="approved" or not matching[0]["source_coverage_complete"] or not matching[0]["role_policy"]["dynamic_safety_satisfied"]:_fail("release_entry_not_approved")
    if matching[0]["review"]["decision_id"]!=decision["identity"]["decision_id"]:_fail("release_review_mismatch")
    if decision["decision"]["outcome"]!="approved":_fail("release_review_not_approved")
    return deepcopy(root)
