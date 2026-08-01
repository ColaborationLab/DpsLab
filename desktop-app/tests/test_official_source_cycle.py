import copy,hashlib,json
from datetime import datetime,timedelta,timezone
from pathlib import Path
import unittest
from dpslab.official_source_cycle import run_official_source_cycle
from dpslab.official_source_receipt import calculate_receipt_sha256
from dpslab.official_source_schedule import SchedulePolicy
from dpslab.official_source_transport import OfficialTransportOutcome
from dpslab.patch_source_adapter import InjectedResponse
ROOT=Path(__file__).parents[2];REGISTRY=ROOT/"knowledge/sources/official_patch_source_registry_0_1.json";FIXTURE=ROOT/"knowledge/snapshots/official_source_capture_receipt_synthetic_0_1.json"
class CycleTests(unittest.TestCase):
 def setUp(self):
  self.registry=json.loads(REGISTRY.read_text());self.previous=json.loads(FIXTURE.read_text());self.base=datetime(2026,8,2,2,0,tzinfo=timezone.utc);self.calls=[]
 def response(self,body=b"<html>synthetic</html>",status=200,etag='"s1"'):
  return OfficialTransportOutcome("response_quarantined_pending_capture_validation",None,InjectedResponse(status,"worldofwarcraft.blizzard.com","text/html",body,True,etag,None))
 def fetch(self,outcome):
  def value(plan):self.calls.append(plan);return outcome
  return value
 def cycle(self,outcome,**kwargs):return run_official_source_cycle(self.registry,self.base,"synthetic.receipt.002",self.fetch(outcome),**kwargs)
 def test_first_seen_pending(self):self.assertEqual("first_seen_pending_review",self.cycle(self.response()).status)
 def test_due_cycle_fetches_once(self):self.assertEqual(1,self.cycle(self.response()).fetch_count)
 def test_equal_previous_is_unchanged(self):self.assertEqual("unchanged",self.cycle(self.response(),previous_receipt=self.previous).status)
 def test_changed_hash_is_pending(self):self.assertEqual("changed_pending_review",self.cycle(self.response(b"<html>changed</html>"),previous_receipt=self.previous).status)
 def test_conditional_etag_from_previous(self):self.cycle(self.response(),previous_receipt=self.previous);self.assertEqual('"s1"',self.calls[0].headers["If-None-Match"])
 def test_304_reuses_previous(self):
  result=self.cycle(self.response(b"",304),previous_receipt=self.previous);self.assertEqual(("unchanged",0,True),(result.status,result.receipt["capture"]["byte_count"],result.receipt["capture"]["reused_previous"]))
 def test_not_due_does_not_fetch(self):
  now=datetime(2026,8,1,21,0,tzinfo=timezone.utc);result=run_official_source_cycle(self.registry,now,"synthetic.receipt.002",self.fetch(self.response()),previous_receipt=self.previous);self.assertEqual(("not_due",0,len(self.calls)),(result.status,result.fetch_count,len(self.calls)))
 def test_backoff_does_not_fetch(self):
  result=run_official_source_cycle(self.registry,self.base,"synthetic.receipt.002",self.fetch(self.response()),last_attempt_at=self.base,consecutive_failures=1);self.assertEqual(("backoff",0),(result.status,result.fetch_count))
 def test_transport_failure_is_sanitized(self):
  result=self.cycle(OfficialTransportOutcome("evidence_unavailable","transport_error",None));self.assertEqual(("evidence_unavailable","transport_error",1),(result.status,result.reason,result.consecutive_failures))
 def test_fetch_exception_is_sanitized(self):
  def bad(plan):raise RuntimeError("secret")
  result=run_official_source_cycle(self.registry,self.base,"synthetic.receipt.002",bad);self.assertEqual(("evidence_unavailable","transport_error"),(result.status,result.reason))
 def test_invalid_fetch_type_is_sanitized(self):
  result=run_official_source_cycle(self.registry,self.base,"synthetic.receipt.002",lambda plan:object());self.assertEqual("evidence_unavailable",result.status)
 def test_capture_policy_failure_has_no_receipt(self):
  outcome=OfficialTransportOutcome("response_quarantined_pending_capture_validation",None,InjectedResponse(200,"other.invalid","text/html",b"x",True,None,None));result=self.cycle(outcome);self.assertEqual(("evidence_unavailable",None),(result.status,result.receipt))
 def test_success_resets_failures(self):self.assertEqual(0,self.cycle(self.response()).consecutive_failures)
 def test_receipt_contains_no_body(self):self.assertNotIn("synthetic</html>",json.dumps(self.cycle(self.response()).receipt))
if __name__=="__main__":unittest.main()
