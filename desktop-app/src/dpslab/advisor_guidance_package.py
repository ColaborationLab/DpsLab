"""Bounded parser for a non-actionable synthetic Advisor guidance package."""
from __future__ import annotations
from dataclasses import dataclass
import json
from typing import Any, Mapping
PREFIX="DPSLAB-SYNTHETIC-ADVISOR-0.1\n"; MAX_BYTES=4096
class AdvisorGuidancePackageError(ValueError): pass
@dataclass(frozen=True, repr=False)
class AdvisorGuidancePackage: role:str; statistic_target:str; gear_priority:str; priority_display:str; safety_first:str
def _fail(reason:str): raise AdvisorGuidancePackageError(reason)
def _closed(value:Any, keys:set[str], label:str)->dict[str,Any]:
 if not isinstance(value,dict) or set(value)!=keys: _fail(f"advisor_{label}_invalid")
 return value
def _pairs(values):
 result={}
 for key,value in values:
  if key in result:_fail("advisor_duplicate_json_key")
  result[key]=value
 return result
def canonical_advisor_guidance_package_bytes(value:Mapping[str,Any])->bytes:return (json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n").encode()
def parse_synthetic_advisor_guidance_package(text:str, role:str)->AdvisorGuidancePackage:
 if not isinstance(text,str) or not text.startswith(PREFIX):_fail("advisor_prefix_invalid")
 raw=text[len(PREFIX):].encode()
 if not 1<=len(raw)<=MAX_BYTES:_fail("advisor_payload_size_invalid")
 try:value=json.loads(raw.decode(),object_pairs_hook=_pairs,parse_constant=lambda _: _fail("advisor_nonfinite_number"))
 except (UnicodeDecodeError,json.JSONDecodeError) as exc:raise AdvisorGuidancePackageError("advisor_json_invalid") from exc
 root=_closed(value,{"lifecycle","roles","safety","schema_version","synthetic"},"root")
 if root["schema_version"]!="0.1" or root["synthetic"] is not True:_fail("advisor_schema_invalid")
 if raw!=canonical_advisor_guidance_package_bytes(value):_fail("advisor_json_noncanonical")
 if _closed(root["lifecycle"],{"state"},"lifecycle")["state"]!="synthetic_fixture":_fail("advisor_lifecycle_invalid")
 if _closed(root["safety"],{"actionable","no_automation"},"safety")!={"actionable":False,"no_automation":True}:_fail("advisor_safety_invalid")
 if role not in {"damage","tank","healer"}:_fail("advisor_role_invalid")
 entry=_closed(_closed(root["roles"],{"damage","tank","healer"},"roles")[role],{"statistic_target","gear_priority","priority_display","safety_first"},"role")
 if not all(isinstance(entry[k],str) and 1<=len(entry[k])<=160 for k in entry):_fail("advisor_role_invalid")
 expected={"damage":"damage","tank":"survival","healer":"healing"}[role]
 if entry["safety_first"]!=expected:_fail("advisor_role_invalid")
 return AdvisorGuidancePackage(role,entry["statistic_target"],entry["gear_priority"],entry["priority_display"],entry["safety_first"])
