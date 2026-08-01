"""Pure change detection for canonical metadata-only capture receipts."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Any,Mapping,Sequence
from .official_source_receipt import validate_capture_receipt

class OfficialSourceChangeError(ValueError): pass
@dataclass(frozen=True)
class ReceiptChange:
 status:str
 source_id:str
 previous_receipt_id:str|None
 current_receipt_id:str
 previous_content_sha256:str|None
 current_content_sha256:str
 historical_only:bool=True
def _time(value:Mapping[str,Any])->datetime:
 return datetime.fromisoformat(value["identity"]["captured_at"][:-1]+"+00:00")
def _compatible(left:Mapping[str,Any],right:Mapping[str,Any])->bool:
 return all(left["source"][key]==right["source"][key] for key in ("source_id","final_host","media_type"))
def classify_receipt_change(previous:Mapping[str,Any]|None,current:Mapping[str,Any])->ReceiptChange:
 now=validate_capture_receipt(current);current_id=now["identity"]["receipt_id"];digest=now["capture"]["content_sha256"]
 if previous is None:return ReceiptChange("first_seen_pending_review",now["source"]["source_id"],None,current_id,None,digest)
 old=validate_capture_receipt(previous)
 if not _compatible(old,now):raise OfficialSourceChangeError("source_identity_mismatch")
 if old["identity"]["receipt_id"]==current_id:raise OfficialSourceChangeError("receipt_id_duplicate")
 if _time(now)<=_time(old):raise OfficialSourceChangeError("capture_time_not_strictly_increasing")
 old_digest=old["capture"]["content_sha256"]
 status="unchanged" if old_digest==digest else "changed_pending_review"
 return ReceiptChange(status,now["source"]["source_id"],old["identity"]["receipt_id"],current_id,old_digest,digest)
def append_receipt_history(history:Sequence[Mapping[str,Any]],current:Mapping[str,Any],*,max_receipts:int=32)->tuple[dict[str,Any],...]:
 if isinstance(max_receipts,bool) or not isinstance(max_receipts,int) or not 1<=max_receipts<=32:raise OfficialSourceChangeError("max_receipts_invalid")
 validated=tuple(validate_capture_receipt(item) for item in history)
 if len(validated)>=max_receipts:raise OfficialSourceChangeError("history_capacity_reached")
 if validated:
  ids=[item["identity"]["receipt_id"] for item in validated]
  if len(ids)!=len(set(ids)):raise OfficialSourceChangeError("history_duplicate_id")
  for left,right in zip(validated,validated[1:]):classify_receipt_change(left,right)
  classify_receipt_change(validated[-1],current)
 else:classify_receipt_change(None,current)
 return (*validated,validate_capture_receipt(current))
