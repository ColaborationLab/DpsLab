import json, unittest
from dpslab.training_dummy_session_transport import *
def doc(): return {"schema_version":"0.1","observation_type":"synthetic_training_dummy_session","state":"completed","duration_seconds":180,"target_classification":"confirmed","metrics":{"action_count":12,"resource_cap_count":0,"inactivity_seconds":3},"safety":{"synthetic":True,"executable":False,"no_automation":True}}
def payload(value=None): return PREFIX + canonical_training_dummy_session_bytes(value or doc()).decode()
class TrainingTransportTests(unittest.TestCase):
 def test_valid(self): self.assertEqual(180, parse_synthetic_training_dummy_session(payload()).duration_seconds)
 def test_rejects_bool(self):
  value=doc(); value["duration_seconds"]=True
  with self.assertRaisesRegex(TrainingDummySessionTransportError,"duration"): parse_synthetic_training_dummy_session(payload(value))
 def test_rejects_noncanonical(self):
  with self.assertRaisesRegex(TrainingDummySessionTransportError,"noncanonical"): parse_synthetic_training_dummy_session(PREFIX+json.dumps(doc(), indent=1)+"\n")
 def test_rejects_unsafe_state(self):
  value=doc(); value["state"]="active"
  with self.assertRaisesRegex(TrainingDummySessionTransportError,"state"): parse_synthetic_training_dummy_session(payload(value))
