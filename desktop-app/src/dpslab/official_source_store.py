"""Atomic bounded storage for metadata-only official-source receipts."""
from __future__ import annotations
from copy import deepcopy
import hashlib,json,os,re,tempfile
from pathlib import Path
from typing import Any,Mapping,Sequence
from .official_source_change import OfficialSourceChangeError,append_receipt_history
from .official_source_receipt import OfficialSourceReceiptError,validate_capture_receipt
class OfficialSourceStoreError(ValueError):pass
_ROOT={"schema_version","source_id","receipts","integrity"};_INTEGRITY={"hash_algorithm","ledger_sha256"};_TOKEN=re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$");_SHA=re.compile(r"^[0-9a-f]{64}$")
def canonical_ledger_bytes(document:Mapping[str,Any])->bytes:return (json.dumps(document,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n").encode("utf-8")
def calculate_ledger_sha256(document:Mapping[str,Any])->str:
 value=deepcopy(dict(document));value["integrity"]["ledger_sha256"]="";return hashlib.sha256(canonical_ledger_bytes(value)).hexdigest()
def _root(root:Path)->Path:
 value=Path(root)
 if not value.is_absolute() or not value.exists() or not value.is_dir() or value.is_symlink():raise OfficialSourceStoreError("store_root_invalid")
 return value
def _path(root:Path,source_id:str)->Path:
 if not isinstance(source_id,str) or _TOKEN.fullmatch(source_id) is None:raise OfficialSourceStoreError("source_id_invalid")
 return _root(root)/f"{source_id}.receipts.json"
def build_receipt_ledger(source_id:str,receipts:Sequence[Mapping[str,Any]])->dict[str,Any]:
 if not isinstance(source_id,str) or _TOKEN.fullmatch(source_id) is None:raise OfficialSourceStoreError("source_id_invalid")
 history:tuple[dict[str,Any],...]=()
 for receipt in receipts:
  value=validate_capture_receipt(receipt)
  if value["source"]["source_id"]!=source_id:raise OfficialSourceStoreError("source_id_mismatch")
  history=append_receipt_history(history,value)
 ledger={"schema_version":"0.1","source_id":source_id,"receipts":list(history),"integrity":{"hash_algorithm":"sha256","ledger_sha256":""}}
 ledger["integrity"]["ledger_sha256"]=calculate_ledger_sha256(ledger);return ledger
def validate_receipt_ledger(document:Mapping[str,Any])->dict[str,Any]:
 value=dict(document)
 if set(value)!=_ROOT or value.get("schema_version")!="0.1" or not isinstance(value.get("receipts"),list):raise OfficialSourceStoreError("ledger_fields_invalid")
 integrity=value.get("integrity")
 if not isinstance(integrity,dict) or set(integrity)!=_INTEGRITY or integrity.get("hash_algorithm")!="sha256" or not isinstance(integrity.get("ledger_sha256"),str) or _SHA.fullmatch(integrity["ledger_sha256"]) is None:raise OfficialSourceStoreError("ledger_integrity_invalid")
 try:rebuilt=build_receipt_ledger(value.get("source_id"),value["receipts"])
 except (OfficialSourceReceiptError,OfficialSourceChangeError) as exc:raise OfficialSourceStoreError("ledger_receipts_invalid") from exc
 if rebuilt["integrity"]["ledger_sha256"]!=integrity["ledger_sha256"]:raise OfficialSourceStoreError("ledger_sha256_mismatch")
 return deepcopy(value)
def load_receipt_ledger(root:Path,source_id:str)->dict[str,Any]:
 path=_path(root,source_id)
 if not path.exists():return build_receipt_ledger(source_id,())
 if path.is_symlink() or not path.is_file():raise OfficialSourceStoreError("ledger_path_invalid")
 try:value=json.loads(path.read_text(encoding="utf-8"))
 except (OSError,UnicodeError,json.JSONDecodeError) as exc:raise OfficialSourceStoreError("ledger_read_invalid") from exc
 return validate_receipt_ledger(value)
def append_receipt_atomic(root:Path,receipt:Mapping[str,Any])->dict[str,Any]:
 value=validate_capture_receipt(receipt);source_id=value["source"]["source_id"];path=_path(root,source_id);current=load_receipt_ledger(root,source_id);ledger=build_receipt_ledger(source_id,(*current["receipts"],value));payload=canonical_ledger_bytes(ledger);temporary:Path|None=None
 try:
  with tempfile.NamedTemporaryFile(mode="wb",prefix=f".{source_id}.",suffix=".tmp",dir=path.parent,delete=False) as stream:
   temporary=Path(stream.name);stream.write(payload);stream.flush();os.fsync(stream.fileno())
  os.replace(temporary,path);temporary=None
 except OSError as exc:raise OfficialSourceStoreError("ledger_write_failed") from exc
 finally:
  if temporary is not None:
   try:temporary.unlink(missing_ok=True)
   except OSError:pass
 return ledger
