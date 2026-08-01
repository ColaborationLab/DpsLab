"""Visible, attended launcher for the first production release-key ceremony."""
from __future__ import annotations
import json,os,sys
from dataclasses import dataclass
from datetime import datetime,timedelta,timezone
from pathlib import Path
from typing import Callable
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,NoEncryption,PrivateFormat
from .knowledge_envelope import canonical_json_bytes
from .new_artifact_transaction import NewArtifactTransaction
from .release_key_ceremony_executor import CeremonyConfirmation,CeremonyExecutionPlan,CeremonyExecutionOutcome,execute_attended_ceremony
from .release_key_recovery import decrypt_recovery_bundle,encrypt_recovery_bundle
from .windows_key_protection import DataProtector,WindowsDataProtector
class CeremonyLauncherError(ValueError):pass
@dataclass(frozen=True)
class LauncherConfig:
    ceremony_id:str;key_id:str;expected_operator:str;valid_from:str;valid_until:str;container_path:Path;recovery_path:Path;evidence_path:Path;repository_roots:tuple[Path,...]
@dataclass
class LauncherDependencies:
    identity:Callable[[],str];read_text:Callable[[str],str];read_secret:Callable[[str],str];write:Callable[[str],None];timestamp:Callable[[],str];generate_key:Callable[[],bytes];protector:DataProtector;transaction:object
def calculate_launcher_plan_sha256(config:LauncherConfig)->str:
    import hashlib
    public={"ceremony_id":config.ceremony_id,"key_id":config.key_id,"expected_operator":config.expected_operator,"valid_from":config.valid_from,"valid_until":config.valid_until,"container_path":str(config.container_path.resolve()),"recovery_path":str(config.recovery_path.resolve()),"evidence_path":str(config.evidence_path.resolve()),"repository_roots":[str(p.resolve()) for p in config.repository_roots]}
    return hashlib.sha256(canonical_json_bytes(public)).hexdigest()
def confirmation_phrase(step:str,plan_sha256:str)->str:return f"CONFIRMO {step.upper()} {plan_sha256[:12]}"
def read_masked_secret(prompt:str,read_char:Callable[[],str]|None=None,write:Callable[[str],object]|None=None)->str:
    if read_char is None:
        import msvcrt
        read_char=msvcrt.getwch
    output=write or sys.stdout.write;output(prompt);characters=[]
    while True:
        char=read_char()
        if char in ("\r","\n"):output("\n");return "".join(characters)
        if char=="\x03":raise KeyboardInterrupt
        if char=="\b":
            if characters:characters.pop();output("\b \b")
            continue
        if char in ("\x00","\xe0"):read_char();continue
        if char.isprintable():characters.append(char);output("*")
def run_attended_launcher(config:LauncherConfig,deps:LauncherDependencies)->CeremonyExecutionOutcome:
    actual=deps.identity()
    if actual!=config.expected_operator or "codexsandbox" in actual.lower():raise CeremonyLauncherError("operator_identity_mismatch")
    paths=(config.container_path,config.recovery_path,config.evidence_path)
    if any(not p.is_absolute() or not p.parent.is_dir() or p.exists() for p in paths):raise CeremonyLauncherError("destination_preflight_failed")
    plan_sha=calculate_launcher_plan_sha256(config);deps.write(f"Operador: {actual}");deps.write(f"Clave: {config.key_id}");deps.write(f"Validez: {config.valid_from} -> {config.valid_until}");deps.write(f"Plan SHA-256: {plan_sha}")
    for label,path in (("Contenedor",config.container_path),("Recuperacion",config.recovery_path),("Evidencia",config.evidence_path)):deps.write(f"{label}: {path.resolve()}")
    confirmations=[]
    for step in ("readiness","generation","recovery","registry"):
        expected=confirmation_phrase(step,plan_sha)
        if deps.read_text(f"Escriba exactamente: {expected}\n> ").strip()!=expected:raise CeremonyLauncherError(f"checkpoint_{step}_not_confirmed")
        confirmations.append(CeremonyConfirmation(step,plan_sha,actual,deps.timestamp()))
    password=None
    for attempt in range(1,4):
        first=deps.read_secret(f"Contrasena de recuperacion (intento {attempt}/3): ");second=deps.read_secret("Repita la contrasena: ")
        if first!=second:deps.write("Las contrasenas no coinciden. Intente nuevamente.");first=second="";continue
        candidate=bytearray(first.encode("utf-8"));first=second=""
        if len(candidate)<16:
            deps.write("La contrasena debe tener al menos 16 caracteres. Intente nuevamente.")
            for index in range(len(candidate)):candidate[index]=0
            continue
        password=candidate;break
    if password is None:raise CeremonyLauncherError("passphrase_attempts_exhausted")
    try:
        plan=CeremonyExecutionPlan(config.ceremony_id,config.key_id,actual,config.valid_from,config.valid_until,plan_sha,config.container_path,config.recovery_path,config.evidence_path,config.repository_roots)
        def encrypt(private:bytes)->bytes:return canonical_json_bytes(encrypt_recovery_bundle(private,bytes(password),config.key_id))
        def decrypt(blob:bytes)->bytes:return decrypt_recovery_bundle(json.loads(blob.decode("utf-8")),bytes(password))
        return execute_attended_ceremony(plan,confirmations,deps.generate_key,deps.protector,encrypt,decrypt,deps.transaction,deps.timestamp())
    finally:
        for index in range(len(password)):password[index]=0
def _native_identity()->str:return f"{os.environ.get('USERDOMAIN','')}\\{os.environ.get('USERNAME','')}"
def _generate_ed25519()->bytes:return Ed25519PrivateKey.generate().private_bytes(Encoding.Raw,PrivateFormat.Raw,NoEncryption())
def main()->int:
    now=datetime.now(timezone.utc).replace(microsecond=0);key_id="dpslab.release.ed25519.001";local=Path(os.environ["LOCALAPPDATA"])/"DpsLab"/"signing";recovery=Path(r"F:\DpsLab Release Key Recovery");records=Path(r"D:\DpsLab Release Key Records")
    config=LauncherConfig("dpslab.release.ceremony.001",key_id,r"DANIELPC\dpcs9",now.isoformat().replace("+00:00","Z"),(now+timedelta(days=365)).isoformat().replace("+00:00","Z"),local/f"{key_id}.dpskey",recovery/f"{key_id}.recovery.json",records/f"{key_id}.ceremony.json",(Path(r"D:\Proyectos\DpsLab"),))
    deps=LauncherDependencies(_native_identity,input,read_masked_secret,print,lambda:datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),_generate_ed25519,WindowsDataProtector(),NewArtifactTransaction())
    try:outcome=run_attended_launcher(config,deps)
    except CeremonyLauncherError as exc:print(f"Ceremonia cancelada de forma segura: {exc}");return 2
    print(f"Resultado: {outcome.status}");print(f"Huella publica: {outcome.evidence['public_key_sha256']}");return 0
if __name__=="__main__":raise SystemExit(main())
