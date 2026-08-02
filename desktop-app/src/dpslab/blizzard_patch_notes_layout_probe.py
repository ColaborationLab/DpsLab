"""Receipt-bound metadata-only HTML layout probe."""
from __future__ import annotations
from collections import Counter
from copy import deepcopy
from html.parser import HTMLParser
import hashlib,json,re
from typing import Any,Mapping
from .official_source_receipt import validate_capture_receipt

class BlizzardPatchNotesLayoutProbeError(ValueError):pass
_TOKEN=re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$");_NAME=re.compile(r"^[a-z][a-z0-9:_-]{0,63}$");_SHA=re.compile(r"^[0-9a-f]{64}$")
_ROOT={"schema_version","identity","source","layout","integrity"};_IDENTITY={"report_id","probe_revision","status"};_SOURCE={"receipt_id","receipt_sha256","content_sha256","byte_count"};_LAYOUT={"tags","edges","attribute_names","node_count","max_depth","hazards"};_INTEGRITY={"hash_algorithm","report_sha256"};_HAZARDS={"comments","declarations","scripts","styles","embedded_json"}
_VOID={"area","base","br","col","embed","hr","img","input","link","meta","param","source","track","wbr"}
def _fail(reason:str)->None:raise BlizzardPatchNotesLayoutProbeError(reason)
def canonical_layout_report_bytes(document:Mapping[str,Any])->bytes:return (json.dumps(document,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n").encode("utf-8")
def calculate_layout_report_sha256(document:Mapping[str,Any])->str:
 value=deepcopy(dict(document));value["integrity"]["report_sha256"]="";return hashlib.sha256(canonical_layout_report_bytes(value)).hexdigest()
def _token(value:Any,label:str)->str:
 if not isinstance(value,str) or _TOKEN.fullmatch(value) is None:_fail(f"{label}_invalid")
 return value
def _name(value:Any,label:str)->str:
 if not isinstance(value,str) or _NAME.fullmatch(value) is None:_fail(f"{label}_invalid")
 return value
class _Probe(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.stack=[];self.tags=Counter();self.edges=Counter();self.attrs=Counter();self.nodes=0;self.max_depth=0;self.hazards={key:False for key in _HAZARDS}
 def _observe(self,tag,attrs,push):
  tag=tag.lower();self.nodes+=1
  if self.nodes>4096 or len(self.stack)>=64 or len(attrs)>32:_fail("probe_limit_exceeded")
  _name(tag,"tag");names=[]
  for name,value in attrs:
   name=name.lower();_name(name,"attribute_name")
   if name in names:_fail("attribute_duplicate")
   names.append(name);self.attrs[(tag,name)]+=1
   if tag=="script" and name=="type" and isinstance(value,str) and value.lower() in {"application/json","application/ld+json"}:self.hazards["embedded_json"]=True
  parent=self.stack[-1] if self.stack else None;self.tags[tag]+=1
  if parent is not None:self.edges[(parent,tag)]+=1
  if len(self.tags)>128 or len(self.edges)>512 or len(self.attrs)>256:_fail("report_cardinality_exceeded")
  if tag=="script":self.hazards["scripts"]=True
  if tag=="style":self.hazards["styles"]=True
  depth=len(self.stack)+1;self.max_depth=max(self.max_depth,depth)
  if push and tag not in _VOID:self.stack.append(tag)
 def handle_starttag(self,tag,attrs):self._observe(tag,attrs,True)
 def handle_startendtag(self,tag,attrs):self._observe(tag,attrs,False)
 def handle_endtag(self,tag):
  tag=tag.lower()
  if tag in _VOID:return
  if not self.stack or self.stack[-1]!=tag:_fail("nesting_invalid")
  self.stack.pop()
 def handle_comment(self,data):self.hazards["comments"]=True
 def handle_decl(self,decl):self.hazards["declarations"]=True
 def unknown_decl(self,data):self.hazards["declarations"]=True
 def handle_data(self,data):pass
def validate_layout_report(document:Mapping[str,Any])->dict[str,Any]:
 value=dict(document)
 if set(value)!=_ROOT or value.get("schema_version")!="0.1":_fail("root_fields_invalid")
 identity=value["identity"];source=value["source"];layout=value["layout"];integrity=value["integrity"]
 if not isinstance(identity,dict) or set(identity)!=_IDENTITY or identity.get("probe_revision")!="blizzard.layout.0.1" or identity.get("status")!="layout_observed_pending_review":_fail("identity_invalid")
 _token(identity.get("report_id"),"report_id")
 if not isinstance(source,dict) or set(source)!=_SOURCE or not isinstance(source.get("byte_count"),int) or isinstance(source.get("byte_count"),bool) or source["byte_count"]<1:_fail("source_invalid")
 _token(source.get("receipt_id"),"receipt_id")
 for field in ("receipt_sha256","content_sha256"):
  if not isinstance(source.get(field),str) or _SHA.fullmatch(source[field]) is None:_fail(f"{field}_invalid")
 if not isinstance(layout,dict) or set(layout)!=_LAYOUT:_fail("layout_invalid")
 if not isinstance(layout["node_count"],int) or isinstance(layout["node_count"],bool) or not 1<=layout["node_count"]<=4096 or not isinstance(layout["max_depth"],int) or isinstance(layout["max_depth"],bool) or not 1<=layout["max_depth"]<=64:_fail("layout_counts_invalid")
 for field,keys,order_fields in (("tags",{"name","count"},("name",)),("edges",{"parent","child","count"},("parent","child")),("attribute_names",{"tag","name","count"},("tag","name"))):
  if not isinstance(layout[field],list):_fail(f"{field}_invalid")
  previous=None
  for item in layout[field]:
   if not isinstance(item,dict) or set(item)!=keys or not isinstance(item["count"],int) or isinstance(item["count"],bool) or item["count"]<1:_fail(f"{field}_invalid")
   for name in keys-{"count"}:_name(item[name],name)
   order=tuple(item[name] for name in order_fields)
   if previous is not None and order<=previous:_fail(f"{field}_order_invalid")
   previous=order
 if sum(item["count"] for item in layout["tags"])!=layout["node_count"]:_fail("node_count_mismatch")
 if not isinstance(layout["hazards"],dict) or set(layout["hazards"])!=_HAZARDS or any(not isinstance(v,bool) for v in layout["hazards"].values()):_fail("hazards_invalid")
 if not isinstance(integrity,dict) or set(integrity)!=_INTEGRITY or integrity.get("hash_algorithm")!="sha256" or not isinstance(integrity.get("report_sha256"),str) or _SHA.fullmatch(integrity["report_sha256"]) is None:_fail("integrity_invalid")
 if calculate_layout_report_sha256(value)!=integrity["report_sha256"]:_fail("report_sha256_mismatch")
 return deepcopy(value)
def probe_patch_notes_layout(html_bytes:bytes,receipt:Mapping[str,Any],report_id:str)->dict[str,Any]:
 receipt_value=validate_capture_receipt(receipt);capture=receipt_value["capture"]
 if capture["capture_status"]!="captured_pending_review":_fail("receipt_status_invalid")
 if not isinstance(html_bytes,bytes) or not html_bytes or len(html_bytes)>1_048_576:_fail("html_bytes_invalid")
 if len(html_bytes)!=capture["byte_count"] or hashlib.sha256(html_bytes).hexdigest()!=capture["content_sha256"]:_fail("receipt_binding_mismatch")
 try:text=html_bytes.decode("utf-8")
 except UnicodeDecodeError as exc:raise BlizzardPatchNotesLayoutProbeError("html_utf8_invalid") from exc
 parser=_Probe()
 try:parser.feed(text);parser.close()
 except BlizzardPatchNotesLayoutProbeError:raise
 except Exception as exc:raise BlizzardPatchNotesLayoutProbeError("html_parse_invalid") from exc
 if parser.stack or parser.nodes<1:_fail("document_incomplete")
 tags=[{"name":name,"count":count} for name,count in sorted(parser.tags.items())]
 edges=[{"parent":parent,"child":child,"count":count} for (parent,child),count in sorted(parser.edges.items())]
 attrs=[{"tag":tag,"name":name,"count":count} for (tag,name),count in sorted(parser.attrs.items())]
 value={"schema_version":"0.1","identity":{"report_id":_token(report_id,"report_id"),"probe_revision":"blizzard.layout.0.1","status":"layout_observed_pending_review"},"source":{"receipt_id":receipt_value["identity"]["receipt_id"],"receipt_sha256":receipt_value["integrity"]["receipt_sha256"],"content_sha256":capture["content_sha256"],"byte_count":capture["byte_count"]},"layout":{"tags":tags,"edges":edges,"attribute_names":attrs,"node_count":parser.nodes,"max_depth":parser.max_depth,"hazards":parser.hazards},"integrity":{"hash_algorithm":"sha256","report_sha256":""}}
 value["integrity"]["report_sha256"]=calculate_layout_report_sha256(value);return validate_layout_report(value)
