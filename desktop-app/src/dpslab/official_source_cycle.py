"""One injected, non-persistent official-source maintenance transaction."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime,timezone
from typing import Any,Callable,Mapping
from .official_source_change import ReceiptChange,classify_receipt_change
from .official_source_receipt import build_capture_receipt,validate_capture_receipt
from .official_source_request import OfficialRequestPlan,plan_content_update_notes
from .official_source_schedule import ScheduleDecision,SchedulePolicy,assess_official_source_schedule
from .official_source_transport import OfficialTransportOutcome
from .patch_source_adapter import PreviousCapture,capture_injected_response
Fetcher=Callable[[OfficialRequestPlan],OfficialTransportOutcome]
@dataclass(frozen=True)
class OfficialSourceCycleResult:
 status:str
 reason:str|None
 schedule:ScheduleDecision
 receipt:Mapping[str,Any]|None
 change:ReceiptChange|None
 consecutive_failures:int
 fetch_count:int
def _captured_at(now:datetime)->str:return now.astimezone(timezone.utc).isoformat().replace("+00:00","Z")
def _previous(receipt:Mapping[str,Any]|None)->tuple[dict[str,Any]|None,PreviousCapture|None]:
 if receipt is None:return None,None
 value=validate_capture_receipt(receipt);capture=value["capture"]
 return value,PreviousCapture(capture["content_sha256"],capture["etag"],capture["last_modified"])
def run_official_source_cycle(registry:Mapping[str,Any],now:datetime,receipt_id:str,fetcher:Fetcher,*,previous_receipt:Mapping[str,Any]|None=None,last_attempt_at:datetime|None=None,consecutive_failures:int=0,policy:SchedulePolicy=SchedulePolicy())->OfficialSourceCycleResult:
 previous,previous_capture=_previous(previous_receipt)
 schedule=assess_official_source_schedule(now,previous,last_attempt_at=last_attempt_at,consecutive_failures=consecutive_failures,policy=policy)
 if schedule.status!="due":return OfficialSourceCycleResult(schedule.status,schedule.reason,schedule,None,None,consecutive_failures,0)
 etag=previous["capture"]["etag"] if previous else None;modified=previous["capture"]["last_modified"] if previous else None
 plan=plan_content_update_notes(etag,modified)
 try:transport=fetcher(plan)
 except Exception:transport=None
 if not isinstance(transport,OfficialTransportOutcome) or transport.response is None or transport.status!="response_quarantined_pending_capture_validation":
  reason=transport.reason if isinstance(transport,OfficialTransportOutcome) else "transport_error"
  return OfficialSourceCycleResult("evidence_unavailable",reason or "transport_error",schedule,None,None,min(consecutive_failures+1,16),1)
 capture=capture_injected_response(registry,plan.source_id,transport.response,previous_capture)
 if capture.status=="evidence_unavailable":return OfficialSourceCycleResult("evidence_unavailable",capture.reason,schedule,None,None,min(consecutive_failures+1,16),1)
 receipt=build_capture_receipt(receipt_id,_captured_at(now),plan,transport,capture)
 change=classify_receipt_change(previous,receipt)
 return OfficialSourceCycleResult(change.status,None,schedule,receipt,change,0,1)
