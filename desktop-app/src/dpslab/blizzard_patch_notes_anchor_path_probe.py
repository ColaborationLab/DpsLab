"""Value-blind ancestry probe for receipt-bound data-props carriers."""
from __future__ import annotations
from collections import Counter
from copy import deepcopy
from html.parser import HTMLParser
import hashlib,json,re
from typing import Any,Mapping
from .official_source_receipt import validate_capture_receipt
class BlizzardPatchNotesAnchorPathProbeError(ValueError):pass
_TOKEN=re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$");_TAG=re.compile(r"^[a-z][a-z0-9:_-]{0,63}$");_SHA=re.compile(r"^[0-9a-f]{64}$");_VOID={"area","base","br","col","embed","hr","img","input","link","meta","param","source","track","wbr"}
_ROOT={"schema_version","identity","source","paths","integrity"};_IDENTITY={"report_id","probe_revision","status"};_SOURCE={"receipt_id","receipt_sha256","content_sha256","byte_count"};_PATHS={"carrier_count","anchored_count","unanchored_count","signatures"};_SIGNATURE={"tags","depth","occurrences"};_INTEGRITY={"hash_algorithm","report_sha256"}
def _fail(reason):raise BlizzardPatchNotesAnchorPathProbeError(reason)
def canonical_anchor_path_bytes(document):return (json.dumps(document,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n").encode()
def calculate_anchor_path_sha256(document):value=deepcopy(dict(document));value["integrity"]["report_sha256"]="";return hashlib.sha256(canonical_anchor_path_bytes(value)).hexdigest()
def _token(value,label):
 if not isinstance(value,str) or _TOKEN.fullmatch(value) is None:_fail(f"{label}_invalid")
 return value
class _Parser(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.stack=[];self.nodes=0;self.carriers=0;self.unanchored=0;self.paths=Counter()
 def handle_starttag(self,tag,attrs):
  tag=tag.lower();self.nodes+=1
  if _TAG.fullmatch(tag) is None:_fail("tag_invalid")
  if self.nodes>4096 or len(self.stack)>=64 or len(attrs)>32:_fail("probe_limit_exceeded")
  names=[name.lower() for name,value in attrs]
  if len(names)!=len(set(names)):_fail("attribute_duplicate")
  if tag=="div" and "data-props" in names:
   self.carriers+=1
   if self.carriers>128:_fail("carrier_limit_exceeded")
   indices=[index for index,value in enumerate(self.stack) if value=="article"]
   if not indices:self.unanchored+=1
   else:
    path=tuple(self.stack[indices[-1]:]+[tag])
    if len(path)>32:_fail("path_limit_exceeded")
    self.paths[path]+=1
    if len(self.paths)>128:_fail("path_cardinality_exceeded")
  if tag not in _VOID:self.stack.append(tag)
 def handle_startendtag(self,tag,attrs):self.handle_starttag(tag,attrs);self.handle_endtag(tag)
 def handle_endtag(self,tag):
  tag=tag.lower()
  if tag in _VOID:return
  if not self.stack or self.stack[-1]!=tag:_fail("nesting_invalid")
  self.stack.pop()
 def handle_data(self,data):pass
def validate_anchor_path_report(document):
 value=dict(document)
 if set(value)!=_ROOT or value.get("schema_version")!="0.1":_fail("root_invalid")
 identity=value["identity"];source=value["source"];paths=value["paths"];integrity=value["integrity"]
 if not isinstance(identity,dict) or set(identity)!=_IDENTITY or identity.get("probe_revision")!="blizzard.anchor-path.0.1" or identity.get("status")!="anchor_path_observed_pending_review":_fail("identity_invalid")
 _token(identity.get("report_id"),"report_id")
 if not isinstance(source,dict) or set(source)!=_SOURCE or not isinstance(source.get("byte_count"),int) or isinstance(source.get("byte_count"),bool) or source["byte_count"]<1:_fail("source_invalid")
 _token(source.get("receipt_id"),"receipt_id")
 for field in ("receipt_sha256","content_sha256"):
  if not isinstance(source.get(field),str) or _SHA.fullmatch(source[field]) is None:_fail("source_hash_invalid")
 if not isinstance(paths,dict) or set(paths)!=_PATHS:_fail("paths_invalid")
 for field in ("carrier_count","anchored_count","unanchored_count"):
  if not isinstance(paths.get(field),int) or isinstance(paths[field],bool) or paths[field]<0:_fail("path_count_invalid")
 if paths["carrier_count"]<1 or paths["anchored_count"]+paths["unanchored_count"]!=paths["carrier_count"]:_fail("carrier_count_mismatch")
 if not isinstance(paths["signatures"],list):_fail("signatures_invalid")
 previous=None;total=0
 for item in paths["signatures"]:
  if not isinstance(item,dict) or set(item)!=_SIGNATURE or not isinstance(item["tags"],list) or len(item["tags"])<2 or item["tags"][0]!="article" or item["tags"][-1]!="div":_fail("signature_invalid")
  for tag in item["tags"]:
   if not isinstance(tag,str) or _TAG.fullmatch(tag) is None:_fail("signature_invalid")
  if item["depth"]!=len(item["tags"]) or not isinstance(item["occurrences"],int) or isinstance(item["occurrences"],bool) or item["occurrences"]<1:_fail("signature_invalid")
  key=tuple(item["tags"])
  if previous is not None and key<=previous:_fail("signature_order_invalid")
  previous=key;total+=item["occurrences"]
 if total!=paths["anchored_count"]:_fail("anchored_count_mismatch")
 if not isinstance(integrity,dict) or set(integrity)!=_INTEGRITY or integrity.get("hash_algorithm")!="sha256" or not isinstance(integrity.get("report_sha256"),str) or _SHA.fullmatch(integrity["report_sha256"]) is None:_fail("integrity_invalid")
 if calculate_anchor_path_sha256(value)!=integrity["report_sha256"]:_fail("report_sha256_mismatch")
 return deepcopy(value)
def probe_anchor_paths(html_bytes:bytes,receipt:Mapping[str,Any],report_id:str):
 receipt_value=validate_capture_receipt(receipt);capture=receipt_value["capture"]
 if capture["capture_status"]!="captured_pending_review":_fail("receipt_status_invalid")
 if not isinstance(html_bytes,bytes) or not html_bytes or len(html_bytes)>1_048_576:_fail("html_bytes_invalid")
 if len(html_bytes)!=capture["byte_count"] or hashlib.sha256(html_bytes).hexdigest()!=capture["content_sha256"]:_fail("receipt_binding_mismatch")
 try:text=html_bytes.decode()
 except UnicodeDecodeError as exc:raise BlizzardPatchNotesAnchorPathProbeError("html_utf8_invalid") from exc
 parser=_Parser();parser.feed(text);parser.close()
 if parser.stack:_fail("document_incomplete")
 if parser.carriers<1:_fail("anchor_carrier_unavailable")
 signatures=[{"tags":list(path),"depth":len(path),"occurrences":count} for path,count in sorted(parser.paths.items())]
 result={"schema_version":"0.1","identity":{"report_id":_token(report_id,"report_id"),"probe_revision":"blizzard.anchor-path.0.1","status":"anchor_path_observed_pending_review"},"source":{"receipt_id":receipt_value["identity"]["receipt_id"],"receipt_sha256":receipt_value["integrity"]["receipt_sha256"],"content_sha256":capture["content_sha256"],"byte_count":capture["byte_count"]},"paths":{"carrier_count":parser.carriers,"anchored_count":parser.carriers-parser.unanchored,"unanchored_count":parser.unanchored,"signatures":signatures},"integrity":{"hash_algorithm":"sha256","report_sha256":""}}
 result["integrity"]["report_sha256"]=calculate_anchor_path_sha256(result);return validate_anchor_path_report(result)
