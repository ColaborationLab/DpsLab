"""Strict decoder for a player-pasted live DpsLab analysis export."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib, json
from typing import Any, Mapping

PREFIX = "DPSLAB-LIVE-ANALYSIS-0.1\n"
MAX_BYTES = 65536

class LiveAnalysisTransportError(ValueError): pass

@dataclass(frozen=True, repr=False)
class LiveAnalysisItem:
    item_id: int; item_level: int; item_link: str; location: int; slot: str; source: str
@dataclass(frozen=True, repr=False)
class LiveAnalysisSnapshot:
    build: int; interface_version: int; class_id: int; specialization_id: int; role: str; level: int; race_id: int; equipped: tuple[LiveAnalysisItem,...]; bag: tuple[LiveAnalysisItem,...]; receipt_sha256: str

def _fail(reason: str): raise LiveAnalysisTransportError(reason)
def _integer(value: Any, name: str, low: int, high: int) -> int:
    if isinstance(value,bool) or not isinstance(value,int) or not low <= value <= high: _fail(f"live_analysis_{name}_invalid")
    return value
def _closed(value: Any, fields: set[str], label: str) -> dict[str,Any]:
    if not isinstance(value,dict) or set(value) != fields: _fail(f"live_analysis_{label}_fields_invalid")
    return value
def _pairs(values):
    result={}
    for key,value in values:
        if key in result: _fail("live_analysis_duplicate_json_key")
        result[key]=value
    return result
def _nonfinite(_): _fail("live_analysis_nonfinite_number")
def canonical_live_analysis_bytes(document: Mapping[str,Any]) -> bytes:
    try: return (json.dumps(document,ensure_ascii=False,allow_nan=False,sort_keys=True,separators=(",",":"))+"\n").encode()
    except (TypeError,ValueError) as exc: raise LiveAnalysisTransportError("live_analysis_not_canonicalizable") from exc
def _item(value: Any, source: str) -> LiveAnalysisItem:
    item=_closed(value,{"item_id","item_level","item_link","location","slot","source"},"item")
    if item["source"] != source or not isinstance(item["item_link"],str) or not 1 <= len(item["item_link"]) <= 2048 or not isinstance(item["slot"],str) or not item["slot"]: _fail("live_analysis_item_invalid")
    return LiveAnalysisItem(_integer(item["item_id"],"item_id",1,9_999_999),_integer(item["item_level"],"item_level",1,9_999),item["item_link"],_integer(item["location"],"location",0,40),item["slot"],source)
def parse_live_analysis_export(text: str) -> LiveAnalysisSnapshot:
    if not isinstance(text,str) or not text.startswith(PREFIX): _fail("live_analysis_prefix_invalid")
    raw=text[len(PREFIX):].encode("utf-8")
    if not 1 <= len(raw) <= MAX_BYTES: _fail("live_analysis_payload_size_invalid")
    try: doc=json.loads(raw.decode("utf-8"),object_pairs_hook=_pairs,parse_constant=_nonfinite)
    except (UnicodeDecodeError,json.JSONDecodeError) as exc: raise LiveAnalysisTransportError("live_analysis_json_invalid") from exc
    root=_closed(doc,{"compatibility","equipment","observation_type","safety","schema_version","subject"},"root")
    if root["schema_version"] != "0.1" or root["observation_type"] != "live_manual_analysis_export": _fail("live_analysis_schema_incompatible")
    if raw != canonical_live_analysis_bytes(doc): _fail("live_analysis_json_noncanonical")
    compatibility=_closed(root["compatibility"],{"build","interface_version","wow_product"},"compatibility")
    if compatibility["wow_product"] != "retail": _fail("live_analysis_product_unsupported")
    subject=_closed(root["subject"],{"class_id","level","race_id","role","specialization_id"},"subject")
    if subject["role"] not in {"damage","healer","tank"}: _fail("live_analysis_role_invalid")
    equipment=_closed(root["equipment"],{"bag","equipped"},"equipment")
    if not isinstance(equipment["equipped"],list) or not 1 <= len(equipment["equipped"]) <= 19 or not isinstance(equipment["bag"],list) or len(equipment["bag"]) > 40: _fail("live_analysis_items_invalid")
    equipped=tuple(_item(v,"equipped") for v in equipment["equipped"]); bag=tuple(_item(v,"designated_bag") for v in equipment["bag"])
    if len({(x.source,x.location) for x in (*equipped,*bag)}) != len(equipped)+len(bag): _fail("live_analysis_item_duplicate")
    safety=_closed(root["safety"],{"contains_direct_identifiers","executable","no_automation"},"safety")
    if safety != {"contains_direct_identifiers":False,"executable":False,"no_automation":True}: _fail("live_analysis_safety_invalid")
    return LiveAnalysisSnapshot(_integer(compatibility["build"],"build",1,9_999_999),_integer(compatibility["interface_version"],"interface_version",1,9_999_999),_integer(subject["class_id"],"class_id",1,1000),_integer(subject["specialization_id"],"specialization_id",1,100000),subject["role"],_integer(subject["level"],"level",1,1000),_integer(subject["race_id"],"race_id",1,1000),equipped,bag,hashlib.sha256(raw).hexdigest())
