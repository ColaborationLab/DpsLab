import json,tempfile
from datetime import datetime,timedelta,timezone
from pathlib import Path
import unittest
from dpslab.official_source_operator import OfficialSourceOperatorError,SOURCE_ID,expected_confirmation,run_attended_official_source_operation
from dpslab.official_source_store import load_receipt_ledger
from dpslab.official_source_transport import OfficialTransportOutcome
from dpslab.patch_source_adapter import InjectedResponse
ROOT=Path(__file__).parents[2];REGISTRY=ROOT/"knowledge/sources/official_patch_source_registry_0_1.json"
class OperatorTests(unittest.TestCase):
 def setUp(self):self.registry=json.loads(REGISTRY.read_text());self.temp=tempfile.TemporaryDirectory(ignore_cleanup_errors=True);self.store=Path(self.temp.name).resolve();self.now=datetime(2026,8,2,3,0,tzinfo=timezone.utc);self.calls=0
 def tearDown(self):self.temp.cleanup()
 def fetch(self,body=b"<html>synthetic</html>"):
  def value(plan):self.calls+=1;return OfficialTransportOutcome("response_quarantined_pending_capture_validation",None,InjectedResponse(200,"worldofwarcraft.blizzard.com","text/html",body,True,'"s1"',None))
  return value
 def operate(self,receipt="synthetic.operator.001",**kwargs):return run_attended_official_source_operation(self.registry,self.store,self.now,receipt,expected_confirmation(receipt),fetcher=self.fetch(),**kwargs)
 def test_confirmation_is_exact(self):
  with self.assertRaisesRegex(OfficialSourceOperatorError,"confirmation_not_exact"):run_attended_official_source_operation(self.registry,self.store,self.now,"synthetic.operator.001","yes",fetcher=self.fetch())
 def test_success_persists_one(self):self.assertEqual((True,1),(lambda x:(x.persisted,x.receipt_count))(self.operate()))
 def test_success_fetches_once(self):self.assertEqual(1,self.operate().fetch_count)
 def test_persisted_ledger_is_loadable(self):self.operate();self.assertEqual(1,len(load_receipt_ledger(self.store,SOURCE_ID)["receipts"]))
 def test_second_unchanged_is_persisted(self):
  self.operate();self.now+=timedelta(hours=6);result=self.operate("synthetic.operator.002");self.assertEqual(("unchanged",2),(result.status,result.receipt_count))
 def test_not_due_does_not_mutate(self):
  self.operate();self.now+=timedelta(hours=1);result=self.operate("synthetic.operator.002");self.assertEqual(("not_due",False,1),(result.status,result.persisted,result.receipt_count))
 def test_backoff_does_not_mutate(self):
  result=self.operate(last_attempt_at=self.now,consecutive_failures=1);self.assertEqual(("backoff",False,0),(result.status,result.persisted,result.receipt_count))
 def test_transport_failure_does_not_mutate(self):
  def bad(plan):return OfficialTransportOutcome("evidence_unavailable","transport_error",None)
  receipt="synthetic.operator.001";result=run_attended_official_source_operation(self.registry,self.store,self.now,receipt,expected_confirmation(receipt),fetcher=bad);self.assertEqual(("evidence_unavailable",False,0),(result.status,result.persisted,result.receipt_count))
 def test_fetch_exception_does_not_mutate(self):
  def bad(plan):raise RuntimeError("secret")
  receipt="synthetic.operator.001";result=run_attended_official_source_operation(self.registry,self.store,self.now,receipt,expected_confirmation(receipt),fetcher=bad);self.assertEqual(("evidence_unavailable",0),(result.status,result.receipt_count))
 def test_changed_content_is_pending(self):
  self.operate();self.now+=timedelta(hours=6);receipt="synthetic.operator.002";result=run_attended_official_source_operation(self.registry,self.store,self.now,receipt,expected_confirmation(receipt),fetcher=self.fetch(b"changed"));self.assertEqual("changed_pending_review",result.status)
 def test_result_contains_no_receipt_or_body(self):self.assertNotIn("receipt",self.operate().__dict__)
 def test_empty_store_has_no_files_after_denial(self):
  with self.assertRaises(OfficialSourceOperatorError):run_attended_official_source_operation(self.registry,self.store,self.now,"x","bad",fetcher=self.fetch())
  self.assertEqual([],list(self.store.iterdir()))
if __name__=="__main__":unittest.main()
