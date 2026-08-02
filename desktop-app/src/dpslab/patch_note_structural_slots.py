"""Neutral classification of validated patch-note text topology paths."""
from copy import deepcopy
import hashlib,json,re
from .blizzard_patch_notes_text_topology_probe import validate_text_topology
class PatchNoteStructuralSlotsError(ValueError):pass
_SHA=re.compile(r"^[0-9a-f]{64}$");_EXPECTED={
 ("article",)+("div",)*5:"slot.path_01",
 ("article",)+("div",)*8:"slot.path_02",
 ("article",)+("div",)*4+("p",):"slot.path_03"}
def _fail(reason):raise PatchNoteStructuralSlotsError(reason)
def canonical_structural_slots_bytes(d):return (json.dumps(d,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n").encode()
def calculate_structural_slots_sha256(d):v=deepcopy(dict(d));v["integrity"]["slots_sha256"]="";return hashlib.sha256(canonical_structural_slots_bytes(v)).hexdigest()
def validate_structural_slots(d):
 v=dict(d)
 if set(v)!={"schema_version","identity","source","slots","integrity"} or v.get("schema_version")!="0.1":_fail("root_invalid")
 i=v["identity"];s=v["source"];slots=v["slots"];g=v["integrity"]
 if set(i)!={"classification_id","status"} or i.get("status")!="structural_slots_pending_review" or not isinstance(i.get("classification_id"),str):_fail("identity_invalid")
 if set(s)!={"topology_report_id","topology_report_sha256"} or not isinstance(s.get("topology_report_id"),str) or not isinstance(s.get("topology_report_sha256"),str) or _SHA.fullmatch(s["topology_report_sha256"]) is None:_fail("source_invalid")
 if not isinstance(slots,list) or len(slots)!=3:_fail("slots_invalid")
 for item,(path,slot_id) in zip(slots,sorted(_EXPECTED.items(),key=lambda x:x[1])):
  if set(item)!={"slot_id","tags","text_nodes","total_characters","max_characters"} or item.get("slot_id")!=slot_id or item.get("tags")!=list(path):_fail("slot_invalid")
  for f in ("text_nodes","total_characters","max_characters"):
   if not isinstance(item.get(f),int) or isinstance(item[f],bool) or item[f]<1:_fail("slot_metric_invalid")
 if set(g)!={"hash_algorithm","slots_sha256"} or g.get("hash_algorithm")!="sha256" or not isinstance(g.get("slots_sha256"),str) or _SHA.fullmatch(g["slots_sha256"]) is None or calculate_structural_slots_sha256(v)!=g["slots_sha256"]:_fail("integrity_invalid")
 return deepcopy(v)
def classify_structural_slots(topology,classification_id):
 t=validate_text_topology(topology);observed={tuple(x["tags"]):x for x in t["topology"]["paths"]}
 if set(observed)!=set(_EXPECTED):_fail("topology_paths_not_exact")
 slots=[]
 for path,slot_id in sorted(_EXPECTED.items(),key=lambda x:x[1]):
  x=observed[path];slots.append({"slot_id":slot_id,"tags":list(path),"text_nodes":x["text_nodes"],"total_characters":x["total_characters"],"max_characters":x["max_characters"]})
 v={"schema_version":"0.1","identity":{"classification_id":classification_id,"status":"structural_slots_pending_review"},"source":{"topology_report_id":t["identity"]["report_id"],"topology_report_sha256":t["integrity"]["report_sha256"]},"slots":slots,"integrity":{"hash_algorithm":"sha256","slots_sha256":""}}
 v["integrity"]["slots_sha256"]=calculate_structural_slots_sha256(v);return validate_structural_slots(v)
