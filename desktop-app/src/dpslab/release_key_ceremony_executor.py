"""Attended ceremony orchestration with injected secret and storage boundaries."""
from __future__ import annotations
import base64,hashlib,re
from dataclasses import dataclass
from datetime import datetime,timezone
from pathlib import Path
from typing import Any,Callable,Mapping,Protocol,Sequence
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
from .knowledge_envelope import canonical_json_bytes
from .windows_key_protection import DataProtector,build_protected_key_container
class CeremonyExecutorError(ValueError):pass
class ArtifactTransaction(Protocol):
    def commit_new(self,artifacts:Mapping[Path,bytes])->None:...
@dataclass(frozen=True)
class CeremonyConfirmation:checkpoint:str;plan_sha256:str;operator_id:str;confirmed_at:str
@dataclass(frozen=True)
class CeremonyExecutionPlan:
    ceremony_id:str;key_id:str;operator_id:str;valid_from:str;valid_until:str;plan_sha256:str;container_path:Path;recovery_path:Path;evidence_path:Path;repository_roots:tuple[Path,...]
@dataclass(frozen=True)
class CeremonyExecutionOutcome:status:str;evidence:dict[str,Any]
_STEPS=("readiness","generation","recovery","registry");_TOKEN=re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$");_SHA=re.compile(r"^[0-9a-f]{64}$")
def _fail(reason:str)->None:raise CeremonyExecutorError(reason)
def _time(value:Any,label:str)->datetime:
    if not isinstance(value,str) or not value.endswith("Z"):_fail(f"{label}_invalid")
    try:parsed=datetime.fromisoformat(value[:-1]+"+00:00")
    except ValueError as exc:raise CeremonyExecutorError(f"{label}_invalid") from exc
    if parsed.utcoffset()!=timezone.utc.utcoffset(parsed):_fail(f"{label}_invalid")
    return parsed
def _validate_plan(plan:CeremonyExecutionPlan)->None:
    for value,label in ((plan.ceremony_id,"ceremony_id"),(plan.key_id,"key_id")):
        if not isinstance(value,str) or _TOKEN.fullmatch(value) is None:_fail(f"{label}_invalid")
    if not plan.key_id.startswith("dpslab.release.ed25519."):_fail("key_id_invalid")
    if not isinstance(plan.operator_id,str) or "\\" not in plan.operator_id or "codexsandbox" in plan.operator_id.lower():_fail("operator_invalid")
    if not isinstance(plan.plan_sha256,str) or _SHA.fullmatch(plan.plan_sha256) is None:_fail("plan_sha256_invalid")
    if _time(plan.valid_from,"valid_from")>=_time(plan.valid_until,"valid_until"):_fail("validity_invalid")
    paths=(plan.container_path,plan.recovery_path,plan.evidence_path)
    if any(not isinstance(path,Path) or not path.is_absolute() for path in paths) or len({path.resolve() for path in paths})!=3:_fail("destinations_invalid")
    roots=tuple(root.resolve() for root in plan.repository_roots)
    for path in paths:
        resolved=path.resolve()
        if path.exists():_fail("destination_exists")
        if any(resolved==root or root in resolved.parents for root in roots):_fail("destination_in_repository")
def _validate_confirmations(plan:CeremonyExecutionPlan,confirmations:Sequence[CeremonyConfirmation])->None:
    if not isinstance(confirmations,(list,tuple)) or tuple(item.checkpoint for item in confirmations)!=_STEPS:_fail("confirmation_order_invalid")
    prior=None
    for item in confirmations:
        if item.plan_sha256!=plan.plan_sha256 or item.operator_id!=plan.operator_id:_fail("confirmation_binding_invalid")
        current=_time(item.confirmed_at,"confirmed_at")
        if prior is not None and current<=prior:_fail("confirmation_time_invalid")
        prior=current
def execute_attended_ceremony(plan:CeremonyExecutionPlan,confirmations:Sequence[CeremonyConfirmation],generate_private_key:Callable[[],bytes],protector:DataProtector,encrypt_recovery:Callable[[bytes],bytes],decrypt_recovery:Callable[[bytes],bytes],transaction:ArtifactTransaction,executed_at:str)->CeremonyExecutionOutcome:
    _validate_plan(plan);_validate_confirmations(plan,confirmations);_time(executed_at,"executed_at");raw=generate_private_key()
    if not isinstance(raw,bytes) or len(raw)!=32:_fail("generated_key_invalid")
    secret=bytearray(raw);recovered=bytearray()
    try:
        private=Ed25519PrivateKey.from_private_bytes(bytes(secret));public=private.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw);fingerprint=hashlib.sha256(public).hexdigest();container=build_protected_key_container(bytes(secret),plan.key_id,public,plan.valid_from,protector);container_bytes=canonical_json_bytes(container);recovery=encrypt_recovery(bytes(secret))
        if not isinstance(recovery,bytes) or not recovery:_fail("recovery_ciphertext_invalid")
        restored=decrypt_recovery(recovery)
        if not isinstance(restored,bytes) or len(restored)!=32:_fail("recovery_verification_invalid")
        recovered=bytearray(restored);restored_public=Ed25519PrivateKey.from_private_bytes(bytes(recovered)).public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
        if hashlib.sha256(restored_public).hexdigest()!=fingerprint:_fail("recovery_fingerprint_mismatch")
        evidence={"schema_version":"0.1","ceremony_id":plan.ceremony_id,"key_id":plan.key_id,"operator_id":plan.operator_id,"algorithm":"ed25519","executed_at":executed_at,"valid_from":plan.valid_from,"valid_until":plan.valid_until,"plan_sha256":plan.plan_sha256,"public_key_base64":base64.b64encode(public).decode("ascii"),"public_key_sha256":fingerprint,"container_sha256":hashlib.sha256(container_bytes).hexdigest(),"recovery_sha256":hashlib.sha256(recovery).hexdigest(),"status":"key_material_created_pending_registry_review"};evidence["evidence_sha256"]=hashlib.sha256(canonical_json_bytes(evidence)).hexdigest();transaction.commit_new({plan.container_path:container_bytes,plan.recovery_path:recovery,plan.evidence_path:canonical_json_bytes(evidence)});return CeremonyExecutionOutcome(evidence["status"],evidence)
    finally:
        for index in range(len(secret)):secret[index]=0
        for index in range(len(recovered)):recovered[index]=0
