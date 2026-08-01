import json
from datetime import datetime,timedelta,timezone
from pathlib import Path
import unittest
from dpslab.official_source_schedule import OfficialSourceScheduleError,SchedulePolicy,assess_official_source_schedule
ROOT=Path(__file__).parents[2];FIXTURE=ROOT/"knowledge/snapshots/official_source_capture_receipt_synthetic_0_1.json"
class ScheduleTests(unittest.TestCase):
 def setUp(self):self.receipt=json.loads(FIXTURE.read_text());self.captured=datetime(2026,8,1,20,0,tzinfo=timezone.utc)
 def test_initial_check_due(self):self.assertEqual(("due","initial_check"),(lambda x:(x.status,x.reason))(assess_official_source_schedule(self.captured)))
 def test_fresh_receipt_not_due(self):
  result=assess_official_source_schedule(self.captured+timedelta(hours=1),self.receipt);self.assertEqual(("not_due",self.captured+timedelta(hours=6)),(result.status,result.next_due_at))
 def test_interval_boundary_due(self):self.assertEqual("interval_elapsed",assess_official_source_schedule(self.captured+timedelta(hours=6),self.receipt).reason)
 def test_expired_freshness_due(self):self.assertEqual("freshness_expired",assess_official_source_schedule(self.captured+timedelta(days=1),self.receipt).reason)
 def test_first_failure_backoff(self):
  result=assess_official_source_schedule(self.captured+timedelta(seconds=1),last_attempt_at=self.captured,consecutive_failures=1);self.assertEqual(("backoff",300),(result.status,result.backoff_seconds))
 def test_backoff_is_exponential_and_capped(self):
  for failures,seconds in ((2,600),(7,14400),(16,14400)):
   result=assess_official_source_schedule(self.captured,last_attempt_at=self.captured,consecutive_failures=failures);self.assertEqual(seconds,result.backoff_seconds)
 def test_retry_becomes_due(self):self.assertEqual("retry_due",assess_official_source_schedule(self.captured+timedelta(minutes=5),last_attempt_at=self.captured,consecutive_failures=1).reason)
 def test_failure_requires_attempt(self):
  with self.assertRaisesRegex(OfficialSourceScheduleError,"last_attempt_required"):assess_official_source_schedule(self.captured,consecutive_failures=1)
 def test_naive_clocks_rejected(self):
  for kwargs in ({"now":datetime(2026,1,1)},{"now":self.captured,"last_attempt_at":datetime(2026,1,1),"consecutive_failures":1}):
   with self.assertRaises(OfficialSourceScheduleError):assess_official_source_schedule(**kwargs)
 def test_clock_regression_rejected(self):
  with self.assertRaisesRegex(OfficialSourceScheduleError,"clock_regression"):assess_official_source_schedule(self.captured-timedelta(seconds=1),self.receipt)
 def test_bool_and_invalid_failures_rejected(self):
  for value in (True,-1,17):
   with self.assertRaisesRegex(OfficialSourceScheduleError,"consecutive_failures"):assess_official_source_schedule(self.captured,consecutive_failures=value)
 def test_invalid_policy_ranges_rejected(self):
  for policy in (SchedulePolicy(interval_seconds=True),SchedulePolicy(max_age_seconds=1),SchedulePolicy(base_backoff_seconds=500,max_backoff_seconds=300)):
   with self.assertRaises(OfficialSourceScheduleError):assess_official_source_schedule(self.captured,policy=policy)
if __name__=="__main__":unittest.main()
