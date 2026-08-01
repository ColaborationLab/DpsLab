"""Canonical metadata-only receipts for quarantined official captures."""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime
import hashlib,json,re
from typing import Any,Mapping
from .official_source_request import OfficialRequestPlan
from .official_source_transport import OfficialTransportOutcome
from .patch_source_adapter import CaptureOutcome

class OfficialSourceReceiptError(ValueError): pass
_SHA=re.compile(r"^[0-9a-f]{64}$")
_TOKEN=re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
_ROOT={"schema_version","identity","source","capture","integrity"}
_IDENTITY={"receipt_id","captured_at"}
_SOURCE={"source_id","final_host","media_type"}
_CAPTURE={"transport_status","capture_status","complete","byte_count","content_sha256","etag","last_modified","reused_previous"}
_INTEGRITY={"hash_algorithm","receipt_sha256"}
_STATUSES={"captured_pending_review","duplicate","not_modified"}

def _fail(reason:str)->None: raise OfficialSourceReceiptError(reason)
def _closed(value:Any,fields:set[str],label:str)->dict[str,Any]:
 if not isinstance(value,dict) or set(value)!=fields:_fail(f"{label}_fields_invalid")
 return value
def _timestamp(value:Any)->None:
 if not isinstance(value,str) or not value.endswith("Z"):_fail("captured_at_invalid")
 try: datetime.fromisoformat(value[:-1]+"+00:00")
 except ValueError as exc: raise OfficialSourceReceiptError("captured_at_invalid") from exc
def _validator(value:Any)->bool:return value is None or isinstance(value,str) and 1<=len(value)<=256 and "\r" not in value and "\n" not in value
def canonical_receipt_bytes(document:Mapping[str,Any])->bytes:
 return (json.dumps(document,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n").encode("utf-8")
def calculate_receipt_sha256(document:Mapping[str,Any])->str:
 value=deepcopy(dict(document));value["integrity"]["receipt_sha256"]=""
 return hashlib.sha256(canonical_receipt_bytes(value)).hexdigest()
def validate_capture_receipt(document:Mapping[str,Any])->dict[str,Any]:
 root=_closed(dict(document),_ROOT,"root")
 if root["schema_version"]!="0.1":_fail("schema_version_invalid")
 identity=_closed(root["identity"],_IDENTITY,"identity")
 if not isinstance(identity["receipt_id"],str) or _TOKEN.fullmatch(identity["receipt_id"]) is None:_fail("receipt_id_invalid")
 _timestamp(identity["captured_at"])
 source=_closed(root["source"],_SOURCE,"source")
 if not all(isinstance(source[k],str) and source[k] for k in _SOURCE):_fail("source_invalid")
 capture=_closed(root["capture"],_CAPTURE,"capture")
 if capture["transport_status"]!="response_quarantined_pending_capture_validation" or capture["capture_status"] not in _STATUSES:_fail("status_invalid")
 if not isinstance(capture["complete"],bool) or not capture["complete"]:_fail("complete_invalid")
 if isinstance(capture["byte_count"],bool) or not isinstance(capture["byte_count"],int) or capture["byte_count"]<0:_fail("byte_count_invalid")
 if not isinstance(capture["content_sha256"],str) or _SHA.fullmatch(capture["content_sha256"]) is None:_fail("content_sha256_invalid")
 if not _validator(capture["etag"]) or not _validator(capture["last_modified"]):_fail("validator_invalid")
 if not isinstance(capture["reused_previous"],bool):_fail("reused_previous_invalid")
 if capture["capture_status"]=="captured_pending_review" and (capture["byte_count"]==0 or capture["reused_previous"]):_fail("capture_semantics_invalid")
 if capture["capture_status"]=="not_modified" and (capture["byte_count"]!=0 or not capture["reused_previous"]):_fail("capture_semantics_invalid")
 integrity=_closed(root["integrity"],_INTEGRITY,"integrity")
 if integrity["hash_algorithm"]!="sha256" or not isinstance(integrity["receipt_sha256"],str) or _SHA.fullmatch(integrity["receipt_sha256"]) is None:_fail("integrity_invalid")
 if calculate_receipt_sha256(root)!=integrity["receipt_sha256"]:_fail("receipt_sha256_mismatch")
 return deepcopy(root)
def build_capture_receipt(receipt_id:str,captured_at:str,plan:OfficialRequestPlan,transport:OfficialTransportOutcome,capture:CaptureOutcome)->dict[str,Any]:
 response=transport.response
 if transport.status!="response_quarantined_pending_capture_validation" or transport.reason is not None or response is None:_fail("transport_not_quarantined")
 if capture.reason is not None or capture.status not in _STATUSES or capture.source_id!=plan.source_id:_fail("capture_not_eligible")
 if response.final_host=="" or response.media_type=="" or not response.complete:_fail("response_invalid")
 if capture.status!="not_modified" and capture.byte_count!=len(response.body):_fail("byte_count_mismatch")
 if capture.status!="not_modified" and hashlib.sha256(response.body).hexdigest()!=capture.content_sha256:_fail("content_sha256_mismatch")
 value={"schema_version":"0.1","identity":{"receipt_id":receipt_id,"captured_at":captured_at},"source":{"source_id":plan.source_id,"final_host":response.final_host,"media_type":response.media_type},"capture":{"transport_status":transport.status,"capture_status":capture.status,"complete":response.complete,"byte_count":capture.byte_count,"content_sha256":capture.content_sha256,"etag":response.etag,"last_modified":response.last_modified,"reused_previous":capture.reused_previous},"integrity":{"hash_algorithm":"sha256","receipt_sha256":""}}
 value["integrity"]["receipt_sha256"]=calculate_receipt_sha256(value)
 return validate_capture_receipt(value)
