import copy,json
from pathlib import Path
import unittest
from dpslab.official_source_request import plan_content_update_notes
from dpslab.official_source_transport import OfficialTransportOutcome
from dpslab.patch_source_adapter import CaptureOutcome,InjectedResponse
from dpslab.official_source_receipt import OfficialSourceReceiptError,build_capture_receipt,calculate_receipt_sha256,canonical_receipt_bytes,validate_capture_receipt
ROOT=Path(__file__).parents[2]
FIXTURE=ROOT/"knowledge/snapshots/official_source_capture_receipt_synthetic_0_1.json"
class ReceiptTests(unittest.TestCase):
 def setUp(self):
  self.plan=plan_content_update_notes();self.body=b"<html>synthetic</html>"
  import hashlib
  self.digest=hashlib.sha256(self.body).hexdigest()
  self.response=InjectedResponse(200,"worldofwarcraft.blizzard.com","text/html",self.body,True,'"s1"',None)
  self.transport=OfficialTransportOutcome("response_quarantined_pending_capture_validation",None,self.response)
  self.capture=CaptureOutcome("captured_pending_review",None,self.plan.source_id,self.digest,len(self.body),False)
 def build(self):return build_capture_receipt("synthetic.receipt.001","2026-08-01T20:00:00Z",self.plan,self.transport,self.capture)
 def test_build_is_valid_and_pending(self):self.assertEqual("captured_pending_review",self.build()["capture"]["capture_status"])
 def test_fixture_is_canonical_and_valid(self):
  value=json.loads(FIXTURE.read_text());self.assertEqual(FIXTURE.read_bytes(),canonical_receipt_bytes(validate_capture_receipt(value)))
 def test_hash_projection_omits_only_hash(self):
  value=self.build();value["integrity"]["receipt_sha256"]="f"*64;self.assertEqual(calculate_receipt_sha256(value),calculate_receipt_sha256(self.build()))
 def test_tamper_rejected(self):
  value=self.build();value["capture"]["byte_count"]+=1
  with self.assertRaisesRegex(OfficialSourceReceiptError,"sha256_mismatch"):validate_capture_receipt(value)
 def test_closed_root_rejects_body(self):
  value=self.build();value["body"]="forbidden"
  with self.assertRaises(OfficialSourceReceiptError):validate_capture_receipt(value)
 def test_bad_timestamp_rejected(self):
  with self.assertRaises(OfficialSourceReceiptError):build_capture_receipt("synthetic.receipt.001","now",self.plan,self.transport,self.capture)
 def test_transport_failure_rejected(self):
  bad=OfficialTransportOutcome("evidence_unavailable","transport_error",None)
  with self.assertRaisesRegex(OfficialSourceReceiptError,"transport_not_quarantined"):build_capture_receipt("synthetic.receipt.001","2026-08-01T20:00:00Z",self.plan,bad,self.capture)
 def test_source_mismatch_rejected(self):
  bad=CaptureOutcome(self.capture.status,None,"other.source",self.digest,len(self.body),False)
  with self.assertRaisesRegex(OfficialSourceReceiptError,"capture_not_eligible"):build_capture_receipt("synthetic.receipt.001","2026-08-01T20:00:00Z",self.plan,self.transport,bad)
 def test_hash_mismatch_rejected(self):
  bad=CaptureOutcome(self.capture.status,None,self.plan.source_id,"f"*64,len(self.body),False)
  with self.assertRaisesRegex(OfficialSourceReceiptError,"content_sha256_mismatch"):build_capture_receipt("synthetic.receipt.001","2026-08-01T20:00:00Z",self.plan,self.transport,bad)
 def test_byte_count_mismatch_rejected(self):
  bad=CaptureOutcome(self.capture.status,None,self.plan.source_id,self.digest,1,False)
  with self.assertRaisesRegex(OfficialSourceReceiptError,"byte_count_mismatch"):build_capture_receipt("synthetic.receipt.001","2026-08-01T20:00:00Z",self.plan,self.transport,bad)
 def test_validators_sanitized(self):
  response=InjectedResponse(200,self.response.final_host,self.response.media_type,self.body,True,"bad\nvalue",None)
  with self.assertRaises(OfficialSourceReceiptError):build_capture_receipt("synthetic.receipt.001","2026-08-01T20:00:00Z",self.plan,OfficialTransportOutcome(self.transport.status,None,response),self.capture)
 def test_no_body_or_recommendation_fields(self):
  text=json.dumps(self.build());self.assertNotIn("synthetic</html>",text);self.assertNotIn("recommendation",text)
if __name__=="__main__":unittest.main()
