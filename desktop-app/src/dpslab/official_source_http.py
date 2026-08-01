"""Bounded credential-free HTTPS client for validated official plans."""
from __future__ import annotations
from email.message import Message
from typing import Any,Callable
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler,Request,build_opener
from .official_source_request import OfficialRequestPlan
from .official_source_transport import RawTransportResponse,OfficialTransportOutcome,execute_injected_transport
class _DenyRedirects(HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):return None
OpenerFactory=Callable[[],Any]
def _header(headers:Message|Any,name:str)->str|None:
 value=headers.get(name) if headers is not None and hasattr(headers,"get") else None
 return value if isinstance(value,str) else None
def _raw(response:Any,plan:OfficialRequestPlan)->RawTransportResponse:
 status=response.getcode();final=response.geturl();headers=response.headers
 media=headers.get_content_type() if hasattr(headers,"get_content_type") else _header(headers,"Content-Type") or ""
 body=response.read(plan.max_bytes+1);declared=_header(headers,"Content-Length");complete=len(body)<=plan.max_bytes
 if declared is not None:
  try:length=int(declared)
  except ValueError:complete=False
  else:complete=complete and length>=0 and length==len(body)
 return RawTransportResponse(status,final,media,body,complete,_header(headers,"ETag"),_header(headers,"Last-Modified"))
def fetch_public_official_source(plan:OfficialRequestPlan,*,timeout_seconds:float=15.0,opener_factory:OpenerFactory|None=None)->OfficialTransportOutcome:
 def sender(value:OfficialRequestPlan,timeout:float)->RawTransportResponse:
  if value.credential_mode!="none":raise RuntimeError("credentialed_plan_forbidden")
  opener=(opener_factory or (lambda:build_opener(_DenyRedirects())))();request=Request(value.url,headers=dict(value.headers),method="GET")
  try:
   with opener.open(request,timeout=timeout) as response:return _raw(response,value)
  except HTTPError as exc:
   if exc.code==304:return RawTransportResponse(304,exc.geturl(),_header(exc.headers,"Content-Type") or value.accepted_media_types[0],b"",True,_header(exc.headers,"ETag"),_header(exc.headers,"Last-Modified"))
   raise
 return execute_injected_transport(plan,sender,timeout_seconds=timeout_seconds)
