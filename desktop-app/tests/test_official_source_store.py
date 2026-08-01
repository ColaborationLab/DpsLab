import copy,json,tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
from dpslab.official_source_receipt import calculate_receipt_sha256
from dpslab.official_source_store import OfficialSourceStoreError,append_receipt_atomic,build_receipt_ledger,calculate_ledger_sha256,canonical_ledger_bytes,load_receipt_ledger,validate_receipt_ledger
ROOT=Path(__file__).parents[2];FIXTURE=ROOT/"knowledge/snapshots/official_source_capture_receipt_synthetic_0_1.json"
def rehash(value):value["integrity"]["receipt_sha256"]=calculate_receipt_sha256(value);return value
class StoreTests(unittest.TestCase):
 def setUp(self):self.receipt=json.loads(FIXTURE.read_text());self.temp=tempfile.TemporaryDirectory(ignore_cleanup_errors=True);self.root=Path(self.temp.name).resolve()
 def tearDown(self):self.temp.cleanup()
 def next(self):
  value=copy.deepcopy(self.receipt);value["identity"].update(receipt_id="synthetic.receipt.002",captured_at="2026-08-01T20:01:00Z");return rehash(value)
 def test_missing_ledger_is_empty(self):self.assertEqual([],load_receipt_ledger(self.root,self.receipt["source"]["source_id"])["receipts"])
 def test_append_and_load(self):append_receipt_atomic(self.root,self.receipt);self.assertEqual(self.receipt,load_receipt_ledger(self.root,self.receipt["source"]["source_id"])["receipts"][0])
 def test_two_receipts_are_ordered(self):append_receipt_atomic(self.root,self.receipt);append_receipt_atomic(self.root,self.next());self.assertEqual(2,len(load_receipt_ledger(self.root,self.receipt["source"]["source_id"])["receipts"]))
 def test_ledger_is_canonical(self):
  ledger=build_receipt_ledger(self.receipt["source"]["source_id"],[self.receipt]);self.assertEqual(ledger,validate_receipt_ledger(json.loads(canonical_ledger_bytes(ledger))))
 def test_hash_projection(self):
  ledger=build_receipt_ledger(self.receipt["source"]["source_id"],[self.receipt]);ledger["integrity"]["ledger_sha256"]="f"*64;self.assertEqual(calculate_ledger_sha256(ledger),calculate_ledger_sha256(build_receipt_ledger(self.receipt["source"]["source_id"],[self.receipt])))
 def test_tamper_rejected(self):
  ledger=build_receipt_ledger(self.receipt["source"]["source_id"],[self.receipt]);ledger["receipts"][0]["capture"]["byte_count"]+=1
  with self.assertRaises(OfficialSourceStoreError):validate_receipt_ledger(ledger)
 def test_source_mismatch_rejected(self):
  with self.assertRaisesRegex(OfficialSourceStoreError,"source_id_mismatch"):build_receipt_ledger("other.source",[self.receipt])
 def test_relative_root_rejected(self):
  with self.assertRaisesRegex(OfficialSourceStoreError,"store_root_invalid"):load_receipt_ledger(Path("relative"),self.receipt["source"]["source_id"])
 def test_missing_root_rejected(self):
  with self.assertRaisesRegex(OfficialSourceStoreError,"store_root_invalid"):load_receipt_ledger(self.root/"missing",self.receipt["source"]["source_id"])
 def test_duplicate_receipt_rejected(self):
  append_receipt_atomic(self.root,self.receipt)
  with self.assertRaises(Exception):append_receipt_atomic(self.root,self.receipt)
 def test_capacity_bounded(self):
  receipts=[]
  for index in range(33):
   value=copy.deepcopy(self.receipt);value["identity"].update(receipt_id=f"synthetic.receipt.{index:03d}",captured_at=f"2026-08-02T00:{index:02d}:00Z");receipts.append(rehash(value))
  with self.assertRaises(Exception):build_receipt_ledger(self.receipt["source"]["source_id"],receipts)
 def test_atomic_replace_is_used(self):
  with patch("dpslab.official_source_store.os.replace",wraps=__import__("os").replace) as replace:append_receipt_atomic(self.root,self.receipt);replace.assert_called_once()
 def test_replace_failure_preserves_prior(self):
  append_receipt_atomic(self.root,self.receipt);before=load_receipt_ledger(self.root,self.receipt["source"]["source_id"])
  with patch("dpslab.official_source_store.os.replace",side_effect=OSError("blocked")):
   with self.assertRaisesRegex(OfficialSourceStoreError,"write_failed"):append_receipt_atomic(self.root,self.next())
  self.assertEqual(before,load_receipt_ledger(self.root,self.receipt["source"]["source_id"]))
 def test_failed_replace_cleans_temp(self):
  with patch("dpslab.official_source_store.os.replace",side_effect=OSError("blocked")):
   with self.assertRaises(OfficialSourceStoreError):append_receipt_atomic(self.root,self.receipt)
  self.assertEqual([],list(self.root.iterdir()))
if __name__=="__main__":unittest.main()
