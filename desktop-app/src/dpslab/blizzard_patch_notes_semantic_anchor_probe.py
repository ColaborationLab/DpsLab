"""Value-erasing semantic shape probe for receipt-bound HTML anchors."""
from __future__ import annotations
from copy import deepcopy
from html.parser import HTMLParser
import hashlib,json,math,re
from typing import Any,Mapping
from .official_source_receipt import validate_capture_receipt

class BlizzardPatchNotesSemanticAnchorProbeError(ValueError):pass
_TOKEN=re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$");_KEY=re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,63}$");_PATH=re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,63}(?:\[\]|\.[A-Za-z][A-Za-z0-9_-]{0,63})*$");_SHA=re.compile(r"^[0-9a-f]{64}$")
_ROOT={"schema_version","identity","source","shape","integrity"};_IDENTITY={"report_id","probe_revision","status"};_SOURCE={"receipt_id","receipt_sha256","content_sha256","byte_count"};_SHAPE={"anchor_count","paths"};_PATH_FIELDS={"path","json_type","occurrences","max_array_length","max_object_keys"};_INTEGRITY={"hash_algorithm","report_sha256"};_TYPES={"object","array","string","number","boolean","null"};_VOID={"area","base","br","col","embed","hr","img","input","link","meta","param","source","track","wbr"}
def _fail(reason:str)->None:raise BlizzardPatchNotesSemanticAnchorProbeError(reason)
def canonical_semantic_shape_bytes(document:Mapping[str,Any])->bytes:return (json.dumps(document,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n").encode("utf-8")
def calculate_semantic_shape_sha256(document:Mapping[str,Any])->str:
 value=deepcopy(dict(document));value["integrity"]["report_sha256"]="";return hashlib.sha256(canonical_semantic_shape_bytes(value)).hexdigest()
def _token(value:Any,label:str)->str:
 if not isinstance(value,str) or _TOKEN.fullmatch(value) is None:_fail(f"{label}_invalid")
 return value
def _pairs(pairs):
 result={}
 for key,value in pairs:
  if key in result:_fail("json_key_duplicate")
  if not isinstance(key,str) or _KEY.fullmatch(key) is None:_fail("json_key_invalid")
  result[key]=value
 return result
def _constant(value):_fail("json_number_invalid")
class _AnchorParser(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.stack=[];self.values=[];self.nodes=0
 def handle_starttag(self,tag,attrs):
  tag=tag.lower();self.nodes+=1
  if self.nodes>4096 or len(self.stack)>=64 or len(attrs)>32:_fail("html_limit_exceeded")
  names=[name.lower() for name,value in attrs]
  if len(names)!=len(set(names)):_fail("html_attribute_duplicate")
  if tag=="div" and self.stack and self.stack[-1]=="article" and "data-props" in names:
   if len(self.values)>=64:_fail("anchor_limit_exceeded")
   value=next(value for name,value in attrs if name.lower()=="data-props")
   if not isinstance(value,str) or not value or len(value.encode("utf-8"))>65536:_fail("anchor_value_invalid")
   self.values.append(value)
  if tag not in _VOID:self.stack.append(tag)
 def handle_startendtag(self,tag,attrs):self.handle_starttag(tag,attrs);self.handle_endtag(tag)
 def handle_endtag(self,tag):
  tag=tag.lower()
  if tag in _VOID:return
  if not self.stack or self.stack[-1]!=tag:_fail("html_nesting_invalid")
  self.stack.pop()
 def handle_data(self,data):pass
class _Shape:
 def __init__(self):self.paths={};self.nodes=0
 def observe(self,path,value,depth=1):
  self.nodes+=1
  if self.nodes>4096 or depth>16:_fail("json_limit_exceeded")
  if isinstance(value,dict):kind="object";array_len=0;object_keys=len(value)
  elif isinstance(value,list):kind="array";array_len=len(value);object_keys=0
  elif isinstance(value,str):kind="string";array_len=object_keys=0
  elif isinstance(value,bool):kind="boolean";array_len=object_keys=0
  elif value is None:kind="null";array_len=object_keys=0
  elif isinstance(value,(int,float)) and not isinstance(value,bool) and (not isinstance(value,float) or math.isfinite(value)):kind="number";array_len=object_keys=0
  else:_fail("json_value_invalid")
  if len(path)>256 or _PATH.fullmatch(path) is None:_fail("json_path_invalid")
  old=self.paths.get(path)
  if old is not None and old[0]!=kind:_fail("json_type_conflict")
  count=1+(old[1] if old else 0);max_array=max(array_len,old[2] if old else 0);max_keys=max(object_keys,old[3] if old else 0);self.paths[path]=(kind,count,max_array,max_keys)
  if len(self.paths)>512:_fail("report_cardinality_exceeded")
  if isinstance(value,dict):
   if len(value)>128:_fail("object_key_limit_exceeded")
   for key in sorted(value):self.observe(f"{path}.{key}" if path else key,value[key],depth+1)
  elif isinstance(value,list):
   if len(value)>256:_fail("array_length_limit_exceeded")
   for item in value:self.observe(path+"[]",item,depth+1)
def validate_semantic_shape(document:Mapping[str,Any])->dict[str,Any]:
 value=dict(document)
 if set(value)!=_ROOT or value.get("schema_version")!="0.1":_fail("root_fields_invalid")
 identity=value["identity"];source=value["source"];shape=value["shape"];integrity=value["integrity"]
 if not isinstance(identity,dict) or set(identity)!=_IDENTITY or identity.get("probe_revision")!="blizzard.semantic-shape.0.1" or identity.get("status")!="semantic_shape_observed_pending_review":_fail("identity_invalid")
 _token(identity.get("report_id"),"report_id")
 if not isinstance(source,dict) or set(source)!=_SOURCE or not isinstance(source.get("byte_count"),int) or isinstance(source.get("byte_count"),bool) or source["byte_count"]<1:_fail("source_invalid")
 _token(source.get("receipt_id"),"receipt_id")
 for field in ("receipt_sha256","content_sha256"):
  if not isinstance(source.get(field),str) or _SHA.fullmatch(source[field]) is None:_fail(f"{field}_invalid")
 if not isinstance(shape,dict) or set(shape)!=_SHAPE or not isinstance(shape.get("anchor_count"),int) or isinstance(shape.get("anchor_count"),bool) or not 1<=shape["anchor_count"]<=64 or not isinstance(shape.get("paths"),list) or not shape["paths"]:_fail("shape_invalid")
 previous=None
 for item in shape["paths"]:
  if not isinstance(item,dict) or set(item)!=_PATH_FIELDS or not isinstance(item.get("path"),str) or _PATH.fullmatch(item["path"]) is None or item.get("json_type") not in _TYPES:_fail("path_invalid")
  if previous is not None and item["path"]<=previous:_fail("path_order_invalid")
  previous=item["path"]
  for field in ("occurrences","max_array_length","max_object_keys"):
   if not isinstance(item[field],int) or isinstance(item[field],bool) or item[field]<0:_fail("path_count_invalid")
  if item["occurrences"]<1:_fail("path_count_invalid")
 if not isinstance(integrity,dict) or set(integrity)!=_INTEGRITY or integrity.get("hash_algorithm")!="sha256" or not isinstance(integrity.get("report_sha256"),str) or _SHA.fullmatch(integrity["report_sha256"]) is None:_fail("integrity_invalid")
 if calculate_semantic_shape_sha256(value)!=integrity["report_sha256"]:_fail("report_sha256_mismatch")
 return deepcopy(value)
def probe_semantic_anchor_shape(html_bytes:bytes,receipt:Mapping[str,Any],report_id:str)->dict[str,Any]:
 receipt_value=validate_capture_receipt(receipt);capture=receipt_value["capture"]
 if capture["capture_status"]!="captured_pending_review":_fail("receipt_status_invalid")
 if not isinstance(html_bytes,bytes) or not html_bytes or len(html_bytes)>1_048_576:_fail("html_bytes_invalid")
 if len(html_bytes)!=capture["byte_count"] or hashlib.sha256(html_bytes).hexdigest()!=capture["content_sha256"]:_fail("receipt_binding_mismatch")
 try:text=html_bytes.decode("utf-8")
 except UnicodeDecodeError as exc:raise BlizzardPatchNotesSemanticAnchorProbeError("html_utf8_invalid") from exc
 parser=_AnchorParser();parser.feed(text);parser.close()
 if parser.stack:_fail("html_incomplete")
 if not parser.values:_fail("semantic_anchor_unavailable")
 shape=_Shape()
 for raw in parser.values:
  try:value=json.loads(raw,object_pairs_hook=_pairs,parse_constant=_constant)
  except BlizzardPatchNotesSemanticAnchorProbeError:raise
  except (json.JSONDecodeError,TypeError,ValueError) as exc:raise BlizzardPatchNotesSemanticAnchorProbeError("anchor_json_invalid") from exc
  if not isinstance(value,dict) or not value:_fail("anchor_root_invalid")
  for key in sorted(value):shape.observe(key,value[key])
 paths=[{"path":path,"json_type":kind,"occurrences":count,"max_array_length":array_len,"max_object_keys":key_count} for path,(kind,count,array_len,key_count) in sorted(shape.paths.items())]
 result={"schema_version":"0.1","identity":{"report_id":_token(report_id,"report_id"),"probe_revision":"blizzard.semantic-shape.0.1","status":"semantic_shape_observed_pending_review"},"source":{"receipt_id":receipt_value["identity"]["receipt_id"],"receipt_sha256":receipt_value["integrity"]["receipt_sha256"],"content_sha256":capture["content_sha256"],"byte_count":capture["byte_count"]},"shape":{"anchor_count":len(parser.values),"paths":paths},"integrity":{"hash_algorithm":"sha256","report_sha256":""}}
 result["integrity"]["report_sha256"]=calculate_semantic_shape_sha256(result);return validate_semantic_shape(result)
