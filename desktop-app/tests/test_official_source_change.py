import copy,json
from pathlib import Path
import unittest
from dpslab.official_source_change import OfficialSourceChangeError,append_receipt_history,classify_receipt_change
from dpslab.official_source_receipt import calculate_receipt_sha256
ROOT=Path(__file__).parents[2];FIXTURE=ROOT/"knowledge/snapshots/official_source_capture_receipt_synthetic_0_1.json"
def rehash(value):value["integrity"]["receipt_sha256"]=calculate_receipt_sha256(value);return value
class ChangeTests(unittest.TestCase):
 def setUp(self):self.first=json.loads(FIXTURE.read_text())
 def next(self,*,digest=None,source=None,host=None,media=None,time="2026-08-01T20:01:00Z",receipt="synthetic.receipt.002"):
  value=copy.deepcopy(self.first);value["identity"].update(receipt_id=receipt,captured_at=time)
  if digest:value["capture"]["content_sha256"]=digest
  if source:value["source"]["source_id"]=source
  if host:value["source"]["final_host"]=host
  if media:value["source"]["media_type"]=media
  return rehash(value)
 def test_first_seen_is_pending(self):self.assertEqual("first_seen_pending_review",classify_receipt_change(None,self.first).status)
 def test_equal_hash_is_unchanged(self):self.assertEqual("unchanged",classify_receipt_change(self.first,self.next()).status)
 def test_new_hash_is_pending(self):self.assertEqual("changed_pending_review",classify_receipt_change(self.first,self.next(digest="f"*64)).status)
 def test_result_is_historical_only(self):self.assertTrue(classify_receipt_change(self.first,self.next()).historical_only)
 def test_source_mismatch_rejected(self):
  with self.assertRaisesRegex(OfficialSourceChangeError,"source_identity_mismatch"):classify_receipt_change(self.first,self.next(source="other.source"))
 def test_host_mismatch_rejected(self):
  with self.assertRaisesRegex(OfficialSourceChangeError,"source_identity_mismatch"):classify_receipt_change(self.first,self.next(host="other.invalid"))
 def test_media_mismatch_rejected(self):
  with self.assertRaisesRegex(OfficialSourceChangeError,"source_identity_mismatch"):classify_receipt_change(self.first,self.next(media="application/json"))
 def test_duplicate_id_rejected(self):
  with self.assertRaisesRegex(OfficialSourceChangeError,"receipt_id_duplicate"):classify_receipt_change(self.first,self.next(receipt="synthetic.receipt.001"))
 def test_equal_or_older_time_rejected(self):
  for time in ("2026-08-01T20:00:00Z","2026-07-31T20:00:00Z"):
   with self.assertRaisesRegex(OfficialSourceChangeError,"strictly_increasing"):classify_receipt_change(self.first,self.next(time=time))
 def test_append_is_copy_on_write(self):
  history=[self.first];result=append_receipt_history(history,self.next());self.assertEqual((1,2),(len(history),len(result)))
 def test_capacity_is_bounded(self):
  with self.assertRaisesRegex(OfficialSourceChangeError,"capacity"):append_receipt_history([self.first],self.next(),max_receipts=1)
 def test_invalid_capacity_rejected(self):
  for value in (True,0,33):
   with self.assertRaisesRegex(OfficialSourceChangeError,"max_receipts"):append_receipt_history([],self.first,max_receipts=value)
if __name__=="__main__":unittest.main()
