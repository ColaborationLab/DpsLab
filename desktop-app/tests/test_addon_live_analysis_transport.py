import json
import unittest
from dpslab.addon_live_analysis_transport import *

def document():
 return {"schema_version":"0.1","observation_type":"live_manual_analysis_export","compatibility":{"wow_product":"retail","build":120000,"interface_version":120000},"subject":{"class_id":11,"specialization_id":102,"role":"damage","level":80,"race_id":4},"equipment":{"equipped":[{"item_id":1,"item_level":100,"item_link":"item:1","location":1,"slot":"head","source":"equipped"}],"bag":[{"item_id":2,"item_level":100,"item_link":"item:2","location":1,"slot":"bag","source":"designated_bag"}]},"safety":{"contains_direct_identifiers":False,"executable":False,"no_automation":True}}
def payload(value=None): return PREFIX+canonical_live_analysis_bytes(value or document()).decode()
class LiveAnalysisTransportTests(unittest.TestCase):
 def test_valid(self):
  result=parse_live_analysis_export(payload()); self.assertEqual(1,len(result.equipped)); self.assertEqual(64,len(result.receipt_sha256))
 def test_prefix(self):
  with self.assertRaisesRegex(LiveAnalysisTransportError,"prefix"): parse_live_analysis_export("bad")
 def test_boolean(self):
  value=document(); value["compatibility"]["build"]=True
  with self.assertRaisesRegex(LiveAnalysisTransportError,"build"): parse_live_analysis_export(payload(value))
 def test_duplicate_location(self):
  value=document(); value["equipment"]["bag"][0]["source"]="equipped"; value["equipment"]["bag"][0]["location"]=1
  with self.assertRaisesRegex(LiveAnalysisTransportError,"item_invalid"): parse_live_analysis_export(payload(value))
 def test_noncanonical(self):
  with self.assertRaisesRegex(LiveAnalysisTransportError,"noncanonical"): parse_live_analysis_export(PREFIX+json.dumps(document(),indent=1)+"\n")
 def test_bounds(self):
  value=document(); value["equipment"]["bag"]=[value["equipment"]["bag"][0]]*41
  with self.assertRaisesRegex(LiveAnalysisTransportError,"items_invalid"): parse_live_analysis_export(payload(value))
