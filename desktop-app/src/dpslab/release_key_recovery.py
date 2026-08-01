"""Passphrase-encrypted recovery bundles for Ed25519 release keys."""
from __future__ import annotations
import base64,hashlib,os,re
from copy import deepcopy
from typing import Any,Mapping
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
from .knowledge_envelope import canonical_json_bytes
class ReleaseKeyRecoveryError(ValueError):pass
_ROOT={"schema_version","key_id","public_key_sha256","kdf","cipher","integrity"};_KDF={"name","salt_base64","length","n","r","p"};_CIPHER={"name","nonce_base64","ciphertext_base64"};_INTEGRITY={"hash_algorithm","bundle_sha256"};_TOKEN=re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$");_SHA=re.compile(r"^[0-9a-f]{64}$")
def _fail(reason:str)->None:raise ReleaseKeyRecoveryError(reason)
def _decode(value:Any,size:int|None,label:str)->bytes:
    if not isinstance(value,str):_fail(f"{label}_invalid")
    try:raw=base64.b64decode(value,validate=True)
    except Exception as exc:raise ReleaseKeyRecoveryError(f"{label}_invalid") from exc
    if (size is not None and len(raw)!=size) or not raw:_fail(f"{label}_invalid")
    return raw
def calculate_recovery_bundle_sha256(document:Mapping[str,Any])->str:
    value=deepcopy(dict(document));value["integrity"]["bundle_sha256"]="";return hashlib.sha256(canonical_json_bytes(value)).hexdigest()
def validate_recovery_bundle(document:Mapping[str,Any])->dict[str,Any]:
    root=dict(document)
    if set(root)!=_ROOT or root["schema_version"]!="0.1":_fail("bundle_fields_invalid")
    if not isinstance(root["key_id"],str) or _TOKEN.fullmatch(root["key_id"]) is None:_fail("key_id_invalid")
    if not isinstance(root["public_key_sha256"],str) or _SHA.fullmatch(root["public_key_sha256"]) is None:_fail("fingerprint_invalid")
    k=root["kdf"]
    if not isinstance(k,dict) or set(k)!=_KDF or k!={"name":"scrypt","salt_base64":k.get("salt_base64"),"length":32,"n":32768,"r":8,"p":1}:_fail("kdf_invalid")
    _decode(k["salt_base64"],16,"salt");c=root["cipher"]
    if not isinstance(c,dict) or set(c)!=_CIPHER or c["name"]!="aes-256-gcm":_fail("cipher_invalid")
    _decode(c["nonce_base64"],12,"nonce");_decode(c["ciphertext_base64"],None,"ciphertext");i=root["integrity"]
    if not isinstance(i,dict) or set(i)!=_INTEGRITY or i["hash_algorithm"]!="sha256" or not isinstance(i["bundle_sha256"],str) or _SHA.fullmatch(i["bundle_sha256"]) is None:_fail("integrity_invalid")
    if calculate_recovery_bundle_sha256(root)!=i["bundle_sha256"]:_fail("bundle_sha256_mismatch")
    return deepcopy(root)
def _derive(passphrase:bytes,salt:bytes)->bytes:
    if not isinstance(passphrase,bytes) or len(passphrase)<16:_fail("passphrase_invalid")
    return Scrypt(salt=salt,length=32,n=32768,r=8,p=1).derive(passphrase)
def encrypt_recovery_bundle(private_key:bytes,passphrase:bytes,key_id:str)->dict[str,Any]:
    if not isinstance(private_key,bytes) or len(private_key)!=32:_fail("private_key_invalid")
    private=Ed25519PrivateKey.from_private_bytes(private_key);public=private.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw);fingerprint=hashlib.sha256(public).hexdigest();salt=os.urandom(16);nonce=os.urandom(12);key=_derive(passphrase,salt);aad=canonical_json_bytes({"schema_version":"0.1","key_id":key_id,"public_key_sha256":fingerprint});ciphertext=AESGCM(key).encrypt(nonce,private_key,aad);bundle={"schema_version":"0.1","key_id":key_id,"public_key_sha256":fingerprint,"kdf":{"name":"scrypt","salt_base64":base64.b64encode(salt).decode(),"length":32,"n":32768,"r":8,"p":1},"cipher":{"name":"aes-256-gcm","nonce_base64":base64.b64encode(nonce).decode(),"ciphertext_base64":base64.b64encode(ciphertext).decode()},"integrity":{"hash_algorithm":"sha256","bundle_sha256":""}};bundle["integrity"]["bundle_sha256"]=calculate_recovery_bundle_sha256(bundle);return validate_recovery_bundle(bundle)
def decrypt_recovery_bundle(document:Mapping[str,Any],passphrase:bytes)->bytes:
    bundle=validate_recovery_bundle(document);salt=_decode(bundle["kdf"]["salt_base64"],16,"salt");nonce=_decode(bundle["cipher"]["nonce_base64"],12,"nonce");ciphertext=_decode(bundle["cipher"]["ciphertext_base64"],None,"ciphertext");aad=canonical_json_bytes({"schema_version":"0.1","key_id":bundle["key_id"],"public_key_sha256":bundle["public_key_sha256"]})
    try:private=AESGCM(_derive(passphrase,salt)).decrypt(nonce,ciphertext,aad)
    except InvalidTag as exc:raise ReleaseKeyRecoveryError("recovery_authentication_failed") from exc
    if len(private)!=32:_fail("recovered_key_invalid")
    public=Ed25519PrivateKey.from_private_bytes(private).public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
    if hashlib.sha256(public).hexdigest()!=bundle["public_key_sha256"]:_fail("recovery_fingerprint_mismatch")
    return private
