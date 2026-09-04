import json,unittest
from dpslab.advisor_guidance_package import *
def doc():return {"schema_version":"0.1","synthetic":True,"lifecycle":{"state":"synthetic_fixture"},"safety":{"actionable":False,"no_automation":True},"roles":{r:{"statistic_target":"stat","gear_priority":"gear","priority_display":"priority","safety_first":s} for r,s in (("damage","damage"),("tank","survival"),("healer","healing"))}}
def payload(value=None):return PREFIX+canonical_advisor_guidance_package_bytes(value or doc()).decode()
class AdvisorGuidanceTests(unittest.TestCase):
 def test_valid(self):self.assertEqual("survival",parse_synthetic_advisor_guidance_package(payload(),"tank").safety_first)
 def test_rejects_actionable(self):
  value=doc();value["safety"]["actionable"]=True
  with self.assertRaisesRegex(AdvisorGuidancePackageError,"safety"):parse_synthetic_advisor_guidance_package(payload(value),"damage")
 def test_rejects_role_safety_mismatch(self):
  value=doc();value["roles"]["healer"]["safety_first"]="damage"
  with self.assertRaisesRegex(AdvisorGuidancePackageError,"role"):parse_synthetic_advisor_guidance_package(payload(value),"healer")
 def test_rejects_noncanonical(self):
  with self.assertRaisesRegex(AdvisorGuidancePackageError,"noncanonical"):parse_synthetic_advisor_guidance_package(PREFIX+json.dumps(doc(),indent=1)+"\n","damage")
