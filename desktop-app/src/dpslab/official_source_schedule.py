"""Pure bounded scheduling policy for official-source checks."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime,timedelta,timezone
from typing import Any,Mapping
from .official_source_receipt import validate_capture_receipt
class OfficialSourceScheduleError(ValueError):pass
@dataclass(frozen=True)
class SchedulePolicy:
 interval_seconds:int=21600
 max_age_seconds:int=86400
 base_backoff_seconds:int=300
 max_backoff_seconds:int=14400
@dataclass(frozen=True)
class ScheduleDecision:
 status:str
 reason:str
 next_due_at:datetime
 backoff_seconds:int
def _utc(value:datetime,label:str)->datetime:
 if not isinstance(value,datetime) or value.tzinfo is None or value.utcoffset() is None:raise OfficialSourceScheduleError(f"{label}_invalid")
 return value.astimezone(timezone.utc)
def _positive(value:Any,label:str)->int:
 if isinstance(value,bool) or not isinstance(value,int) or value<1:raise OfficialSourceScheduleError(f"{label}_invalid")
 return value
def _policy(value:SchedulePolicy)->SchedulePolicy:
 if not isinstance(value,SchedulePolicy):raise OfficialSourceScheduleError("policy_invalid")
 interval=_positive(value.interval_seconds,"interval_seconds");maximum=_positive(value.max_age_seconds,"max_age_seconds")
 base=_positive(value.base_backoff_seconds,"base_backoff_seconds");cap=_positive(value.max_backoff_seconds,"max_backoff_seconds")
 if maximum<interval or cap<base:raise OfficialSourceScheduleError("policy_range_invalid")
 return value
def _captured_at(receipt:Mapping[str,Any])->datetime:
 value=validate_capture_receipt(receipt)["identity"]["captured_at"]
 return datetime.fromisoformat(value[:-1]+"+00:00")
def assess_official_source_schedule(now:datetime,last_receipt:Mapping[str,Any]|None=None,*,last_attempt_at:datetime|None=None,consecutive_failures:int=0,policy:SchedulePolicy=SchedulePolicy())->ScheduleDecision:
 current=_utc(now,"now");rules=_policy(policy)
 if isinstance(consecutive_failures,bool) or not isinstance(consecutive_failures,int) or consecutive_failures<0 or consecutive_failures>16:raise OfficialSourceScheduleError("consecutive_failures_invalid")
 if consecutive_failures:
  if last_attempt_at is None:raise OfficialSourceScheduleError("last_attempt_required")
  attempted=_utc(last_attempt_at,"last_attempt_at")
  if current<attempted:raise OfficialSourceScheduleError("clock_regression")
  backoff=min(rules.base_backoff_seconds*(2**(consecutive_failures-1)),rules.max_backoff_seconds);due=attempted+timedelta(seconds=backoff)
  if current<due:return ScheduleDecision("backoff","failure_backoff_active",due,backoff)
  return ScheduleDecision("due","retry_due",current,backoff)
 if last_attempt_at is not None:_utc(last_attempt_at,"last_attempt_at")
 if last_receipt is None:return ScheduleDecision("due","initial_check",current,0)
 captured=_captured_at(last_receipt)
 if current<captured:raise OfficialSourceScheduleError("clock_regression")
 age=(current-captured).total_seconds()
 if age>=rules.max_age_seconds:return ScheduleDecision("due","freshness_expired",current,0)
 due=captured+timedelta(seconds=rules.interval_seconds)
 if current>=due:return ScheduleDecision("due","interval_elapsed",current,0)
 return ScheduleDecision("not_due","receipt_fresh",due,0)
