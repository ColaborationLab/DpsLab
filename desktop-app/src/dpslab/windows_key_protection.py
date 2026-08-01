"""Closed metadata boundary for Windows user-scoped protected key material."""
from __future__ import annotations
import base64,ctypes,hashlib,os,re
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
from typing import Any,Mapping,Protocol

class WindowsKeyProtectionError(ValueError):pass
class DataProtector(Protocol):
    def protect(self,plaintext:bytes)->bytes:...
    def unprotect(self,ciphertext:bytes)->bytes:...

class _DataBlob(ctypes.Structure):
    _fields_=[("cbData",ctypes.c_ulong),("pbData",ctypes.POINTER(ctypes.c_ubyte))]

class WindowsDataProtector:
    """Minimal DPAPI wrapper: current-user scope and no UI prompts."""
    flags=0x01
    description="DpsLab release key 0.1"
    def __init__(self,crypt32:Any=None,kernel32:Any=None):
        if os.name!="nt" and crypt32 is None:raise WindowsKeyProtectionError("windows_required")
        self._crypt32=crypt32 or ctypes.WinDLL("crypt32",use_last_error=True);self._kernel32=kernel32 or ctypes.WinDLL("kernel32",use_last_error=True)
    @staticmethod
    def _input(value:bytes)->tuple[_DataBlob,Any]:
        buffer=(ctypes.c_ubyte*len(value)).from_buffer_copy(value);return _DataBlob(len(value),ctypes.cast(buffer,ctypes.POINTER(ctypes.c_ubyte))),buffer
    def _output(self,blob:_DataBlob)->bytes:
        try:return ctypes.string_at(blob.pbData,blob.cbData)
        finally:self._kernel32.LocalFree(blob.pbData)
    def protect(self,plaintext:bytes)->bytes:
        if not isinstance(plaintext,bytes) or not plaintext:_fail("plaintext_invalid")
        source,keepalive=self._input(plaintext);output=_DataBlob()
        if not self._crypt32.CryptProtectData(ctypes.byref(source),self.description,None,None,None,self.flags,ctypes.byref(output)):_fail(f"dpapi_protect_failed:{ctypes.get_last_error()}")
        return self._output(output)
    def unprotect(self,ciphertext:bytes)->bytes:
        if not isinstance(ciphertext,bytes) or not ciphertext:_fail("ciphertext_invalid")
        source,keepalive=self._input(ciphertext);output=_DataBlob()
        if not self._crypt32.CryptUnprotectData(ctypes.byref(source),None,None,None,None,self.flags,ctypes.byref(output)):_fail(f"dpapi_unprotect_failed:{ctypes.get_last_error()}")
        return self._output(output)

_FIELDS={"schema_version","key_id","algorithm","public_key_sha256","created_at","protection","ciphertext_base64"};_PROTECTION={"provider","scope","ui_forbidden"};_TOKEN=re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$");_SHA=re.compile(r"^[0-9a-f]{64}$")
def _fail(reason:str)->None:raise WindowsKeyProtectionError(reason)
def _time(value:Any)->None:
    if not isinstance(value,str) or not value.endswith("Z"):_fail("created_at_invalid")
    try:parsed=datetime.fromisoformat(value[:-1]+"+00:00")
    except ValueError as exc:raise WindowsKeyProtectionError("created_at_invalid") from exc
    if parsed.utcoffset()!=timezone.utc.utcoffset(parsed):_fail("created_at_invalid")
def _ciphertext(value:Any)->bytes:
    if not isinstance(value,str):_fail("ciphertext_invalid")
    try:raw=base64.b64decode(value,validate=True)
    except (ValueError,base64.binascii.Error) as exc:raise WindowsKeyProtectionError("ciphertext_invalid") from exc
    if not raw:_fail("ciphertext_invalid")
    return raw
def validate_protected_key_container(document:Mapping[str,Any])->dict[str,Any]:
    root=dict(document)
    if set(root)!=_FIELDS:_fail("container_fields_invalid")
    if root["schema_version"]!="0.1":_fail("schema_invalid")
    if not isinstance(root["key_id"],str) or _TOKEN.fullmatch(root["key_id"]) is None:_fail("key_id_invalid")
    if root["algorithm"]!="ed25519":_fail("algorithm_invalid")
    if not isinstance(root["public_key_sha256"],str) or _SHA.fullmatch(root["public_key_sha256"]) is None:_fail("fingerprint_invalid")
    _time(root["created_at"]);protection=root["protection"]
    if not isinstance(protection,dict) or set(protection)!=_PROTECTION:_fail("protection_fields_invalid")
    if protection!={"provider":"windows_dpapi","scope":"current_user","ui_forbidden":True}:_fail("protection_policy_invalid")
    _ciphertext(root["ciphertext_base64"]);return deepcopy(root)
def build_protected_key_container(private_key:bytes,key_id:str,public_key:bytes,created_at:str,protector:DataProtector)->dict[str,Any]:
    if not isinstance(private_key,bytes) or len(private_key)!=32:_fail("private_key_invalid")
    if not isinstance(public_key,bytes) or len(public_key)!=32:_fail("public_key_invalid")
    ciphertext=protector.protect(private_key)
    if not isinstance(ciphertext,bytes) or not ciphertext:_fail("protector_output_invalid")
    document={"schema_version":"0.1","key_id":key_id,"algorithm":"ed25519","public_key_sha256":hashlib.sha256(public_key).hexdigest(),"created_at":created_at,"protection":{"provider":"windows_dpapi","scope":"current_user","ui_forbidden":True},"ciphertext_base64":base64.b64encode(ciphertext).decode("ascii")}
    return validate_protected_key_container(document)
def protected_key_path(local_app_data:Path,key_id:str)->Path:
    if not isinstance(local_app_data,Path) or not local_app_data.is_absolute():_fail("local_app_data_invalid")
    if not isinstance(key_id,str) or _TOKEN.fullmatch(key_id) is None:_fail("key_id_invalid")
    root=(local_app_data/"DpsLab"/"signing").resolve();candidate=(root/f"{key_id}.dpskey").resolve()
    if candidate.parent!=root:_fail("container_path_invalid")
    return candidate
def unprotect_container(document:Mapping[str,Any],protector:DataProtector)->bytearray:
    valid=validate_protected_key_container(document);plaintext=protector.unprotect(_ciphertext(valid["ciphertext_base64"]))
    if not isinstance(plaintext,bytes) or len(plaintext)!=32:_fail("unprotected_key_invalid")
    return bytearray(plaintext)
