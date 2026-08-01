"""Release signer that exposes signatures, never decrypted key material."""
from __future__ import annotations
import hashlib
from typing import Any,Mapping
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
from .release_signing import sign_release_manifest
from .windows_key_protection import DataProtector,WindowsKeyProtectionError,unprotect_container,validate_protected_key_container

class WindowsReleaseSignerError(ValueError):pass
class WindowsReleaseSigner:
    def __init__(self,container:Mapping[str,Any],protector:DataProtector):self._container=validate_protected_key_container(container);self._protector=protector
    @property
    def key_id(self)->str:return self._container["key_id"]
    def sign(self,payload:bytes)->bytes:
        if not isinstance(payload,bytes) or not payload:raise WindowsReleaseSignerError("payload_invalid")
        secret=unprotect_container(self._container,self._protector)
        try:
            private=Ed25519PrivateKey.from_private_bytes(bytes(secret));public=private.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
            if hashlib.sha256(public).hexdigest()!=self._container["public_key_sha256"]:raise WindowsReleaseSignerError("public_key_fingerprint_mismatch")
            return private.sign(payload)
        finally:
            for index in range(len(secret)):secret[index]=0
def sign_manifest_with_protected_key(manifest:Mapping[str,Any],container:Mapping[str,Any],signed_at:str,protector:DataProtector)->dict[str,Any]:
    signer=WindowsReleaseSigner(container,protector)
    try:return sign_release_manifest(manifest,signer.key_id,signed_at,signer.sign)
    except WindowsKeyProtectionError as exc:raise WindowsReleaseSignerError(str(exc)) from exc
