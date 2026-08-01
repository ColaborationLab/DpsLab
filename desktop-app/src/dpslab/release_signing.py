"""Detached Ed25519 signing boundary for candidate release manifests."""
from __future__ import annotations
import base64,hashlib,re
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime,timezone
from typing import Any,Callable,Mapping
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from .candidate_release_bundle import canonical_release_manifest_bytes,validate_release_manifest
from .knowledge_envelope import canonical_json_bytes

class ReleaseSigningError(ValueError):pass
@dataclass(frozen=True)
class SignatureVerificationOutcome:
    status:str;key_id:str;manifest_sha256:str

_TOKEN=re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$");_SHA=re.compile(r"^[0-9a-f]{64}$")
_REGISTRY={"schema_version","identity","keys","integrity"};_IDENTITY={"registry_id","content_version","created_at"};_KEY={"key_id","algorithm","public_key_base64","valid_from","valid_until","status","rotated_from_key_id","revoked_at","revocation_reason"};_INTEGRITY={"hash_algorithm","registry_sha256"};_SIGNATURE={"schema_version","manifest_sha256","key_id","algorithm","signed_at","signature_base64","status"}
def _fail(reason:str)->None:raise ReleaseSigningError(reason)
def _closed(value:Any,fields:set[str],label:str)->dict[str,Any]:
    if not isinstance(value,dict) or set(value)!=fields:_fail(f"{label}_fields_invalid")
    return value
def _token(value:Any,label:str)->str:
    if not isinstance(value,str) or _TOKEN.fullmatch(value) is None:_fail(f"{label}_invalid")
    return value
def _time(value:Any,label:str)->datetime:
    if not isinstance(value,str) or not value.endswith("Z"):_fail(f"{label}_invalid")
    try:parsed=datetime.fromisoformat(value[:-1]+"+00:00")
    except ValueError as exc:raise ReleaseSigningError(f"{label}_invalid") from exc
    if parsed.utcoffset()!=timezone.utc.utcoffset(parsed):_fail(f"{label}_invalid")
    return parsed
def _decoded(value:Any,size:int,label:str)->bytes:
    if not isinstance(value,str):_fail(f"{label}_invalid")
    try:raw=base64.b64decode(value,validate=True)
    except (ValueError,base64.binascii.Error) as exc:raise ReleaseSigningError(f"{label}_invalid") from exc
    if len(raw)!=size:_fail(f"{label}_invalid")
    return raw
def calculate_trust_registry_sha256(document:Mapping[str,Any])->str:
    value=deepcopy(dict(document));value["integrity"]["registry_sha256"]="";return hashlib.sha256(canonical_json_bytes(value)).hexdigest()
def validate_release_trust_registry(document:Mapping[str,Any])->dict[str,Any]:
    root=_closed(dict(document),_REGISTRY,"registry")
    if root["schema_version"]!="0.1":_fail("registry_schema_invalid")
    identity=_closed(root["identity"],_IDENTITY,"identity");_token(identity["registry_id"],"registry_id");_token(identity["content_version"],"content_version");_time(identity["created_at"],"created_at")
    if not isinstance(root["keys"],list) or not root["keys"]:_fail("keys_invalid")
    seen:set[str]=set();prior:dict[str,dict[str,Any]]={}
    for raw in root["keys"]:
        key=_closed(raw,_KEY,"key");key_id=_token(key["key_id"],"key_id")
        if key_id in seen:_fail("key_id_duplicate")
        if key["algorithm"]!="ed25519":_fail("key_algorithm_invalid")
        _decoded(key["public_key_base64"],32,"public_key");start=_time(key["valid_from"],"valid_from");end=_time(key["valid_until"],"valid_until")
        if start>=end:_fail("key_validity_invalid")
        parent=key["rotated_from_key_id"]
        if parent is not None:
            if not isinstance(parent,str) or parent not in seen:_fail("rotation_parent_invalid")
            parent_key=prior[parent]
            if start<=_time(parent_key["valid_from"],"valid_from") or end<=_time(parent_key["valid_until"],"valid_until"):_fail("rotation_validity_not_advancing")
        if key["status"]=="trusted":
            if key["revoked_at"] is not None or key["revocation_reason"] is not None:_fail("trusted_key_revocation_invalid")
        elif key["status"]=="revoked":
            revoked=_time(key["revoked_at"],"revoked_at")
            if revoked<start or revoked>end or not isinstance(key["revocation_reason"],str) or not key["revocation_reason"].strip():_fail("revocation_invalid")
        else:_fail("key_status_invalid")
        seen.add(key_id);prior[key_id]=key
    integrity=_closed(root["integrity"],_INTEGRITY,"integrity")
    if integrity["hash_algorithm"]!="sha256" or not isinstance(integrity["registry_sha256"],str) or _SHA.fullmatch(integrity["registry_sha256"]) is None:_fail("registry_integrity_invalid")
    if calculate_trust_registry_sha256(root)!=integrity["registry_sha256"]:_fail("registry_sha256_mismatch")
    return deepcopy(root)
def sign_release_manifest(manifest:Mapping[str,Any],key_id:str,signed_at:str,signer:Callable[[bytes],bytes])->dict[str,Any]:
    valid=validate_release_manifest(manifest);_token(key_id,"key_id");_time(signed_at,"signed_at");payload=canonical_release_manifest_bytes(valid);signature=signer(payload)
    if not isinstance(signature,bytes) or len(signature)!=64:_fail("signature_invalid")
    return {"schema_version":"0.1","manifest_sha256":valid["integrity"]["manifest_sha256"],"key_id":key_id,"algorithm":"ed25519","signed_at":signed_at,"signature_base64":base64.b64encode(signature).decode("ascii"),"status":"signed_candidate"}
def verify_release_signature(manifest:Mapping[str,Any],signature:Mapping[str,Any],registry:Mapping[str,Any],observed_at:str)->SignatureVerificationOutcome:
    valid=validate_release_manifest(manifest);record=_closed(dict(signature),_SIGNATURE,"signature")
    if record["schema_version"]!="0.1" or record["algorithm"]!="ed25519" or record["status"]!="signed_candidate":_fail("signature_metadata_invalid")
    key_id=_token(record["key_id"],"key_id");signed=_time(record["signed_at"],"signed_at");observed=_time(observed_at,"observed_at")
    if signed>observed or signed<_time(valid["identity"]["created_at"],"manifest_created_at"):_fail("signature_time_invalid")
    manifest_sha=valid["integrity"]["manifest_sha256"]
    if record["manifest_sha256"]!=manifest_sha:_fail("manifest_sha256_mismatch")
    signature_bytes=_decoded(record["signature_base64"],64,"signature");registry_valid=validate_release_trust_registry(registry);matches=[key for key in registry_valid["keys"] if key["key_id"]==key_id]
    if len(matches)!=1 or matches[0]["status"]!="trusted":_fail("trusted_key_not_found")
    key=matches[0]
    if not (_time(key["valid_from"],"valid_from")<=signed<=_time(key["valid_until"],"valid_until")):_fail("signature_outside_key_validity")
    try:Ed25519PublicKey.from_public_bytes(_decoded(key["public_key_base64"],32,"public_key")).verify(signature_bytes,canonical_release_manifest_bytes(valid))
    except InvalidSignature as exc:raise ReleaseSigningError("signature_verification_failed") from exc
    return SignatureVerificationOutcome("signature_valid_release_eligible",key_id,manifest_sha)
