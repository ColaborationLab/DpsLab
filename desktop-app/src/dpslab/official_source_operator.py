"""Attended one-shot official-source operation."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any,Mapping
from .official_source_cycle import Fetcher,OfficialSourceCycleResult,run_official_source_cycle
from .official_source_http import fetch_public_official_source
from .official_source_schedule import SchedulePolicy
from .official_source_store import append_receipt_atomic,load_receipt_ledger
SOURCE_ID="blizzard.wow.content_update_notes"
class OfficialSourceOperatorError(ValueError):pass
@dataclass(frozen=True)
class OfficialSourceOperatorResult:
 status:str
 reason:str|None
 persisted:bool
 receipt_count:int
 fetch_count:int
def expected_confirmation(receipt_id:str)->str:return f"CONFIRM OFFICIAL SOURCE CHECK {SOURCE_ID} {receipt_id}"
def run_attended_official_source_operation(registry:Mapping[str,Any],store_root:Path,now:datetime,receipt_id:str,confirmation:str,*,fetcher:Fetcher|None=None,last_attempt_at:datetime|None=None,consecutive_failures:int=0,policy:SchedulePolicy=SchedulePolicy())->OfficialSourceOperatorResult:
 if not isinstance(receipt_id,str) or confirmation!=expected_confirmation(receipt_id):raise OfficialSourceOperatorError("confirmation_not_exact")
 ledger=load_receipt_ledger(store_root,SOURCE_ID);previous=ledger["receipts"][-1] if ledger["receipts"] else None
 selected=fetcher or (lambda plan:fetch_public_official_source(plan))
 cycle=run_official_source_cycle(registry,now,receipt_id,selected,previous_receipt=previous,last_attempt_at=last_attempt_at,consecutive_failures=consecutive_failures,policy=policy)
 if cycle.receipt is None:return OfficialSourceOperatorResult(cycle.status,cycle.reason,False,len(ledger["receipts"]),cycle.fetch_count)
 updated=append_receipt_atomic(store_root,cycle.receipt)
 return OfficialSourceOperatorResult(cycle.status,cycle.reason,True,len(updated["receipts"]),cycle.fetch_count)
