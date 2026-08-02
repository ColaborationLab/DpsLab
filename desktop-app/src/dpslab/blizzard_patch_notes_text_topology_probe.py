"""Character-erasing article text topology probe."""
from __future__ import annotations
from collections import Counter
from copy import deepcopy
from html.parser import HTMLParser
import hashlib,json,re
from .official_source_receipt import validate_capture_receipt
class BlizzardPatchNotesTextTopologyProbeError(ValueError):pass
_TOKEN=re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$");_TAG=re.compile(r"^[a-z][a-z0-9:_-]{0,63}$");_SHA=re.compile(r"^[0-9a-f]{64}$");_VOID={"area","base","br","col","embed","hr","img","input","link","meta","param","source","track","wbr"};_EXCLUDED={"script","style","noscript","template"}
def _fail(reason):raise BlizzardPatchNotesTextTopologyProbeError(reason)
def canonical_text_topology_bytes(d):return (json.dumps(d,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n").encode()
def calculate_text_topology_sha256(d):v=deepcopy(dict(d));v["integrity"]["report_sha256"]="";return hashlib.sha256(canonical_text_topology_bytes(v)).hexdigest()
class _Parser(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.stack=[];self.nodes=0;self.metrics={};self.excluded=0
 def handle_starttag(self,tag,attrs):
  tag=tag.lower();self.nodes+=1
  if _TAG.fullmatch(tag) is None or self.nodes>4096 or len(self.stack)>=64:_fail("html_limit_exceeded")
  if tag not in _VOID:self.stack.append(tag)
 def handle_startendtag(self,tag,attrs):self.handle_starttag(tag,attrs);self.handle_endtag(tag)
 def handle_endtag(self,tag):
  tag=tag.lower()
  if tag in _VOID:return
  if not self.stack or self.stack[-1]!=tag:_fail("nesting_invalid")
  self.stack.pop()
 def handle_data(self,data):
  length=len(data.strip())
  if not length:return
  if any(tag in _EXCLUDED for tag in self.stack):self.excluded+=1;return
  articles=[i for i,tag in enumerate(self.stack) if tag=="article"]
  if not articles:return
  path=tuple(self.stack[articles[-1]:])
  if not path or len(path)>32:_fail("path_limit_exceeded")
  old=self.metrics.get(path,(0,0,0));self.metrics[path]=(old[0]+1,old[1]+length,max(old[2],length))
  if len(self.metrics)>256:_fail("path_cardinality_exceeded")
def validate_text_topology(d):
 v=dict(d)
 if set(v)!={"schema_version","identity","source","topology","integrity"} or v.get("schema_version")!="0.1":_fail("root_invalid")
 i=v["identity"];s=v["source"];t=v["topology"];g=v["integrity"]
 if set(i)!={"report_id","probe_revision","status"} or i.get("probe_revision")!="blizzard.text-topology.0.1" or i.get("status")!="text_topology_observed_pending_review" or not isinstance(i.get("report_id"),str) or _TOKEN.fullmatch(i["report_id"]) is None:_fail("identity_invalid")
 if set(s)!={"receipt_id","receipt_sha256","content_sha256","byte_count"} or not isinstance(s.get("byte_count"),int) or isinstance(s["byte_count"],bool) or s["byte_count"]<1 or not isinstance(s.get("receipt_id"),str) or _TOKEN.fullmatch(s["receipt_id"]) is None:_fail("source_invalid")
 for f in ("receipt_sha256","content_sha256"):
  if not isinstance(s.get(f),str) or _SHA.fullmatch(s[f]) is None:_fail("source_invalid")
 if set(t)!={"paths","visible_text_nodes","excluded_text_nodes"} or not isinstance(t["paths"],list) or not t["paths"]:_fail("topology_invalid")
 prev=None;total=0
 for x in t["paths"]:
  if set(x)!={"tags","text_nodes","total_characters","max_characters"} or not isinstance(x["tags"],list) or not x["tags"] or x["tags"][0]!="article":_fail("path_invalid")
  for tag in x["tags"]:
   if not isinstance(tag,str) or _TAG.fullmatch(tag) is None:_fail("path_invalid")
  key=tuple(x["tags"])
  if prev is not None and key<=prev:_fail("path_order_invalid")
  prev=key
  for f in ("text_nodes","total_characters","max_characters"):
   if not isinstance(x[f],int) or isinstance(x[f],bool) or x[f]<1:_fail("metric_invalid")
  if x["max_characters"]>x["total_characters"]:_fail("metric_invalid")
  total+=x["text_nodes"]
 if t["visible_text_nodes"]!=total or not isinstance(t["excluded_text_nodes"],int) or isinstance(t["excluded_text_nodes"],bool) or t["excluded_text_nodes"]<0:_fail("topology_count_invalid")
 if set(g)!={"hash_algorithm","report_sha256"} or g.get("hash_algorithm")!="sha256" or not isinstance(g.get("report_sha256"),str) or _SHA.fullmatch(g["report_sha256"]) is None or calculate_text_topology_sha256(v)!=g["report_sha256"]:_fail("integrity_invalid")
 return deepcopy(v)
def probe_text_topology(html_bytes,receipt,report_id):
 rv=validate_capture_receipt(receipt);c=rv["capture"]
 if c["capture_status"]!="captured_pending_review":_fail("receipt_status_invalid")
 if not isinstance(html_bytes,bytes) or not html_bytes or len(html_bytes)>1048576:_fail("html_bytes_invalid")
 if len(html_bytes)!=c["byte_count"] or hashlib.sha256(html_bytes).hexdigest()!=c["content_sha256"]:_fail("receipt_binding_mismatch")
 try:text=html_bytes.decode()
 except UnicodeDecodeError as e:raise BlizzardPatchNotesTextTopologyProbeError("html_utf8_invalid") from e
 p=_Parser();p.feed(text);p.close()
 if p.stack:_fail("document_incomplete")
 if not p.metrics:_fail("visible_article_text_unavailable")
 paths=[{"tags":list(k),"text_nodes":n,"total_characters":total,"max_characters":maximum} for k,(n,total,maximum) in sorted(p.metrics.items())]
 v={"schema_version":"0.1","identity":{"report_id":report_id,"probe_revision":"blizzard.text-topology.0.1","status":"text_topology_observed_pending_review"},"source":{"receipt_id":rv["identity"]["receipt_id"],"receipt_sha256":rv["integrity"]["receipt_sha256"],"content_sha256":c["content_sha256"],"byte_count":c["byte_count"]},"topology":{"paths":paths,"visible_text_nodes":sum(x["text_nodes"] for x in paths),"excluded_text_nodes":p.excluded},"integrity":{"hash_algorithm":"sha256","report_sha256":""}}
 v["integrity"]["report_sha256"]=calculate_text_topology_sha256(v);return validate_text_topology(v)
