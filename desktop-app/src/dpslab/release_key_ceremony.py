"""Pure synthetic evaluator for the attended production-key ceremony."""
from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime,timezone
import hashlib,re
from typing import Any,Mapping
from .knowledge_envelope import canonical_json_bytes

class ReleaseKeyCeremonyError(ValueError):pass
@dataclass(frozen=True)
class CeremonyDryRunOutcome:
    status:str;reason:str|None;evidence:dict[str,Any]
_ROOT={"schema_version","mode","identity","destinations","checkpoints","integrity"};_IDENTITY={"ceremony_id","key_id","algorithm","proposed_valid_from","proposed_valid_until"};_DEST={"local_container","recovery_copy","recovery_record"};_INTEGRITY={"hash_algorithm","plan_sha256"};_OBS=("repository_clean","remote_synchronized","ci_green","operator_attested","destinations_available","media_present","recording_disabled");_STEPS=("readiness","generation","recovery","registry");_TOKEN=re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$");_SHA=re.compile(r"^[0-9a-f]{64}$")
def _fail(reason:str)->None:raise ReleaseKeyCeremonyError(reason)
def _time(value:Any,label:str)->datetime:
    if not isinstance(value,str) or not value.endswith("Z"):_fail(f"{label}_invalid")
    try:parsed=datetime.fromisoformat(value[:-1]+"+00:00")
    except ValueError as exc:raise ReleaseKeyCeremonyError(f"{label}_invalid") from exc
    if parsed.utcoffset()!=timezone.utc.utcoffset(parsed):_fail(f"{label}_invalid")
    return parsed
def calculate_ceremony_plan_sha256(document:Mapping[str,Any])->str:
    value=deepcopy(dict(document));value["integrity"]["plan_sha256"]="";return hashlib.sha256(canonical_json_bytes(value)).hexdigest()
def validate_ceremony_plan(document:Mapping[str,Any])->dict[str,Any]:
    root=dict(document)
    if set(root)!=_ROOT:_fail("plan_fields_invalid")
    if root["schema_version"]!="0.1" or root["mode"]!="synthetic_dry_run":_fail("mode_invalid")
    identity=root["identity"]
    if not isinstance(identity,dict) or set(identity)!=_IDENTITY:_fail("identity_fields_invalid")
    for field in ("ceremony_id","key_id"):
        if not isinstance(identity[field],str) or _TOKEN.fullmatch(identity[field]) is None or not identity[field].startswith("synthetic."):_fail(f"{field}_invalid")
    if identity["algorithm"]!="ed25519":_fail("algorithm_invalid")
    start=_time(identity["proposed_valid_from"],"valid_from");end=_time(identity["proposed_valid_until"],"valid_until")
    if start>=end:_fail("validity_invalid")
    destinations=root["destinations"]
    if not isinstance(destinations,dict) or set(destinations)!=_DEST or len(set(destinations.values()))!=3:_fail("destinations_invalid")
    if any(not isinstance(value,str) or not value.startswith("synthetic://") for value in destinations.values()):_fail("destination_not_synthetic")
    if root["checkpoints"]!=list(_STEPS):_fail("checkpoints_invalid")
    integrity=root["integrity"]
    if not isinstance(integrity,dict) or set(integrity)!=_INTEGRITY or integrity["hash_algorithm"]!="sha256" or not isinstance(integrity["plan_sha256"],str) or _SHA.fullmatch(integrity["plan_sha256"]) is None:_fail("integrity_invalid")
    if calculate_ceremony_plan_sha256(root)!=integrity["plan_sha256"]:_fail("plan_sha256_mismatch")
    return deepcopy(root)
def evaluate_ceremony_dry_run(plan:Mapping[str,Any],observations:Mapping[str,Any],confirmations:Mapping[str,Any],evaluated_at:str)->CeremonyDryRunOutcome:
    valid=validate_ceremony_plan(plan);_time(evaluated_at,"evaluated_at")
    if not isinstance(observations,dict) or tuple(observations)!=_OBS or any(type(observations[key]) is not bool for key in _OBS):_fail("observations_invalid")
    if not isinstance(confirmations,dict) or tuple(confirmations)!=_STEPS or any(type(confirmations[key]) is not bool for key in _STEPS):_fail("confirmations_invalid")
    reason=next((f"observation_{key}_failed" for key in _OBS if not observations[key]),None)
    if reason is None:reason=next((f"checkpoint_{key}_unconfirmed" for key in _STEPS if not confirmations[key]),None)
    status="synthetic_dry_run_ready" if reason is None else "synthetic_dry_run_aborted"
    evidence={"schema_version":"0.1","ceremony_id":valid["identity"]["ceremony_id"],"key_id":valid["identity"]["key_id"],"algorithm":"ed25519","evaluated_at":evaluated_at,"mode":"synthetic_dry_run","plan_sha256":valid["integrity"]["plan_sha256"],"status":status,"reason":reason,"checkpoint_outcomes":{key:confirmations[key] for key in _STEPS}}
    evidence["evidence_sha256"]=hashlib.sha256(canonical_json_bytes(evidence)).hexdigest();return CeremonyDryRunOutcome(status,reason,evidence)
