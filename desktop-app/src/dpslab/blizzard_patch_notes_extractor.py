"""Pure fail-closed extraction from receipt-bound synthetic patch-note HTML."""
from __future__ import annotations
from copy import deepcopy
from html.parser import HTMLParser
import hashlib,json,re
from typing import Any,Mapping
from .official_source_receipt import validate_capture_receipt

class BlizzardPatchNotesExtractorError(ValueError):pass
_TOKEN=re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$");_SHA=re.compile(r"^[0-9a-f]{64}$");_BUILD=re.compile(r"^[0-9]{5,6}$")
_TAGS={"article","section","h2","h3","ul","li"};_ROOT={"schema_version","identity","source","document","assertions","integrity"};_IDENTITY={"extraction_id","parser_revision","status"};_SOURCE={"receipt_id","receipt_sha256","content_sha256","byte_count"};_DOCUMENT={"build_token"};_ASSERTION={"assertion_id","parameter_family_id","subject_tokens","ability_token","operation","old_token","new_token","citation_token"};_INTEGRITY={"hash_algorithm","extraction_sha256"}
def _fail(reason:str)->None:raise BlizzardPatchNotesExtractorError(reason)
def canonical_extraction_bytes(document:Mapping[str,Any])->bytes:return (json.dumps(document,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n").encode("utf-8")
def calculate_extraction_sha256(document:Mapping[str,Any])->str:
 value=deepcopy(dict(document));value["integrity"]["extraction_sha256"]="";return hashlib.sha256(canonical_extraction_bytes(value)).hexdigest()
def _token(value:Any,label:str)->str:
 if not isinstance(value,str) or _TOKEN.fullmatch(value) is None:_fail(f"{label}_invalid")
 return value
class _Parser(HTMLParser):
 def __init__(self,subjects:Mapping[tuple[str,str],tuple[str,str]],families:Mapping[str,str]):super().__init__(convert_charrefs=True);self.subjects=subjects;self.families=families;self.stack=[];self.nodes=0;self.build=None;self.class_key=None;self.spec_key=None;self.items=[];self.text_target=None
 def handle_starttag(self,tag,attrs):
  self.nodes+=1
  if self.nodes>128 or len(self.stack)>=8:_fail("parser_limit_exceeded")
  if tag not in _TAGS:_fail("tag_unsupported")
  values=dict(attrs)
  if len(values)!=len(attrs):_fail("attribute_duplicate")
  allowed={"article":{"data-build"},"section":{"data-class","data-spec"},"h2":set(),"h3":set(),"ul":set(),"li":{"data-ability","data-operation","data-old","data-new"}}[tag]
  if set(values)-allowed:_fail("attribute_unsupported")
  if tag=="article":
   if self.stack or self.build is not None or set(values)!={"data-build"} or _BUILD.fullmatch(values["data-build"]) is None:_fail("article_invalid")
   self.build=values["data-build"]
  elif tag=="section":
   if set(values)=={"data-class"} and self.class_key is None:self.class_key=_token(values["data-class"],"class_key")
   elif set(values)=={"data-spec"} and self.class_key is not None and self.spec_key is None:self.spec_key=_token(values["data-spec"],"spec_key")
   else:_fail("section_invalid")
  elif tag=="h2":
   if self.class_key is None or self.spec_key is not None:_fail("class_heading_invalid")
  elif tag=="h3":
   if self.spec_key is None:_fail("spec_heading_invalid")
  elif tag=="ul":
   if self.spec_key is None:_fail("list_context_invalid")
  elif tag=="li":
   if not self.stack or self.stack[-1]!="ul" or set(values)!={"data-ability","data-operation","data-old","data-new"}:_fail("item_invalid")
   ability=_token(values["data-ability"],"ability");operation=values["data-operation"];old=values["data-old"] or None;new=values["data-new"] or None
   if ability not in self.families or (self.class_key,self.spec_key) not in self.subjects:_fail("mapping_unavailable")
   if operation not in {"add","change","remove"}:_fail("operation_invalid")
   if old is not None:_token(old,"old_token")
   if new is not None:_token(new,"new_token")
   if operation=="add" and (old is not None or new is None) or operation=="remove" and (old is None or new is not None) or operation=="change" and (old is None or new is None or old==new):_fail("value_semantics_invalid")
   self.items.append((ability,operation,old,new,self.class_key,self.spec_key));self.text_target="li"
  self.stack.append(tag)
 def handle_endtag(self,tag):
  if not self.stack or self.stack[-1]!=tag:_fail("nesting_invalid")
  self.stack.pop()
  if tag=="li":self.text_target=None
  elif tag=="section":
   if self.spec_key is not None:self.spec_key=None
   elif self.class_key is not None:self.class_key=None
 def handle_data(self,data):
  if data.strip() and (not self.stack or self.stack[-1] not in {"h2","h3","li"}):_fail("text_context_invalid")
 def handle_startendtag(self,tag,attrs):_fail("self_closing_invalid")
 def unknown_decl(self,data):_fail("declaration_invalid")
def validate_extraction(document:Mapping[str,Any])->dict[str,Any]:
 value=dict(document)
 if set(value)!=_ROOT or value.get("schema_version")!="0.1":_fail("root_fields_invalid")
 identity=value["identity"];source=value["source"];document_value=value["document"];assertions=value["assertions"];integrity=value["integrity"]
 if not isinstance(identity,dict) or set(identity)!=_IDENTITY or identity.get("status")!="pending_review":_fail("identity_invalid")
 _token(identity.get("extraction_id"),"extraction_id");_token(identity.get("parser_revision"),"parser_revision")
 if not isinstance(source,dict) or set(source)!=_SOURCE or not isinstance(source.get("byte_count"),int) or isinstance(source.get("byte_count"),bool) or source["byte_count"]<1:_fail("source_invalid")
 _token(source.get("receipt_id"),"receipt_id")
 for field in ("receipt_sha256","content_sha256"):
  if not isinstance(source.get(field),str) or _SHA.fullmatch(source[field]) is None:_fail(f"{field}_invalid")
 if not isinstance(document_value,dict) or set(document_value)!=_DOCUMENT or not isinstance(document_value.get("build_token"),str) or _BUILD.fullmatch(document_value["build_token"]) is None:_fail("document_invalid")
 if not isinstance(assertions,list) or not assertions:_fail("assertions_invalid")
 ids=set();citations=set();keys=set()
 for item in assertions:
  if not isinstance(item,dict) or set(item)!=_ASSERTION:_fail("assertion_fields_invalid")
  for field in ("assertion_id","parameter_family_id","ability_token","citation_token"):_token(item[field],field)
  if not isinstance(item["subject_tokens"],list) or len(item["subject_tokens"])!=2:
   _fail("subject_tokens_invalid")
  for subject in item["subject_tokens"]:_token(subject,"subject_token")
  if item["operation"] not in {"add","change","remove"}:_fail("operation_invalid")
  for field in ("old_token","new_token"):
   if item[field] is not None:_token(item[field],field)
  if item["assertion_id"] in ids or item["citation_token"] in citations:_fail("assertion_duplicate")
  key=(item["parameter_family_id"],*item["subject_tokens"])
  if key in keys:_fail("assertion_conflict")
  ids.add(item["assertion_id"]);citations.add(item["citation_token"]);keys.add(key)
 if not isinstance(integrity,dict) or set(integrity)!=_INTEGRITY or integrity.get("hash_algorithm")!="sha256" or not isinstance(integrity.get("extraction_sha256"),str) or _SHA.fullmatch(integrity["extraction_sha256"]) is None:_fail("integrity_invalid")
 if calculate_extraction_sha256(value)!=integrity["extraction_sha256"]:_fail("extraction_sha256_mismatch")
 return deepcopy(value)
def extract_patch_notes(html_bytes:bytes,receipt:Mapping[str,Any],extraction_id:str,subject_mapping:Mapping[tuple[str,str],tuple[str,str]],family_mapping:Mapping[str,str])->dict[str,Any]:
 receipt_value=validate_capture_receipt(receipt);capture=receipt_value["capture"]
 if capture["capture_status"]!="captured_pending_review":_fail("receipt_status_invalid")
 if not isinstance(html_bytes,bytes) or not html_bytes or len(html_bytes)>1_048_576:_fail("html_bytes_invalid")
 if len(html_bytes)!=capture["byte_count"] or hashlib.sha256(html_bytes).hexdigest()!=capture["content_sha256"]:_fail("receipt_binding_mismatch")
 try:text=html_bytes.decode("utf-8")
 except UnicodeDecodeError as exc:raise BlizzardPatchNotesExtractorError("html_utf8_invalid") from exc
 parser=_Parser(subject_mapping,family_mapping)
 try:parser.feed(text);parser.close()
 except BlizzardPatchNotesExtractorError:raise
 except Exception as exc:raise BlizzardPatchNotesExtractorError("html_parse_invalid") from exc
 if parser.stack or parser.build is None or not parser.items:_fail("document_incomplete")
 assertions=[]
 for index,(ability,operation,old,new,class_key,spec_key) in enumerate(parser.items,1):
  subjects=subject_mapping[(class_key,spec_key)];assertions.append({"assertion_id":f"assertion.{index}","parameter_family_id":family_mapping[ability],"subject_tokens":list(subjects),"ability_token":ability,"operation":operation,"old_token":old,"new_token":new,"citation_token":f"item.{index}"})
 value={"schema_version":"0.1","identity":{"extraction_id":extraction_id,"parser_revision":"blizzard.html.0.1","status":"pending_review"},"source":{"receipt_id":receipt_value["identity"]["receipt_id"],"receipt_sha256":receipt_value["integrity"]["receipt_sha256"],"content_sha256":capture["content_sha256"],"byte_count":capture["byte_count"]},"document":{"build_token":parser.build},"assertions":assertions,"integrity":{"hash_algorithm":"sha256","extraction_sha256":""}}
 value["integrity"]["extraction_sha256"]=calculate_extraction_sha256(value);return validate_extraction(value)
