"""Synthetic, callback-driven core for an attended semantic review ceremony."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from .patch_note_semantic_slot_review import create_semantic_slot_review
from .patch_note_structural_slots import validate_structural_slots
class SemanticReviewCeremonyError(ValueError):pass
@dataclass(frozen=True)
class CeremonyOutcome:
 status:str
 review:dict|None
 reviewed_slots:int
 buffers_zeroized:bool
ContentProvider=Callable[[str],bytearray]
DecisionProvider=Callable[[str,memoryview],dict[str,str]|None]
BindingVerifier=Callable[[],bool]
def _zeroize(buffer:bytearray)->None:buffer[:]=b"\x00"*len(buffer)
def run_semantic_review_ceremony(slots:dict,*,review_id:str,reviewer_id:str,observed_at:str,receipt_id:str,receipt_sha256:str,verify_binding:BindingVerifier,provide_content:ContentProvider,request_decision:DecisionProvider,max_slot_bytes:int=65536)->CeremonyOutcome:
 validated=validate_structural_slots(slots)
 if not isinstance(max_slot_bytes,int) or isinstance(max_slot_bytes,bool) or max_slot_bytes<1:_raise("max_slot_bytes_invalid")
 if verify_binding() is not True:return CeremonyOutcome("ceremony_binding_rejected",None,0,True)
 decisions=[]
 for item in validated["slots"]:
  if verify_binding() is not True:return CeremonyOutcome("ceremony_source_drifted",None,len(decisions),True)
  slot_id=item["slot_id"];buffer=provide_content(slot_id)
  if type(buffer) is not bytearray:_raise("content_must_be_owned_bytearray")
  if not buffer or len(buffer)>max_slot_bytes:
   _zeroize(buffer);_raise("content_size_invalid")
  try:decision=request_decision(slot_id,memoryview(buffer).toreadonly())
  finally:_zeroize(buffer)
  if decision is None:return CeremonyOutcome("ceremony_cancelled",None,len(decisions),True)
  if not isinstance(decision,dict):_raise("decision_invalid")
  decisions.append({"slot_id":slot_id,**decision})
 if verify_binding() is not True:return CeremonyOutcome("ceremony_source_drifted",None,len(decisions),True)
 review=create_semantic_slot_review(validated,review_id=review_id,reviewer_id=reviewer_id,observed_at=observed_at,receipt_id=receipt_id,receipt_sha256=receipt_sha256,decisions=decisions)
 return CeremonyOutcome("ceremony_completed",review,len(decisions),True)
def _raise(reason):raise SemanticReviewCeremonyError(reason)
