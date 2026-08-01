import io,unittest
from email.message import Message
from dpslab.official_source_http import fetch_public_official_source
from dpslab.official_source_request import plan_content_update_notes,plan_game_data_api
class FakeResponse:
 def __init__(self,url,body=b"official",status=200,content_type="text/html",length=True):
  self._url=url;self._body=io.BytesIO(body);self._status=status;self.headers=Message();self.headers["Content-Type"]=content_type
  if length is True:self.headers["Content-Length"]=str(len(body))
  elif isinstance(length,str):self.headers["Content-Length"]=length
 def getcode(self):return self._status
 def geturl(self):return self._url
 def read(self,size=-1):return self._body.read(size)
 def __enter__(self):return self
 def __exit__(self,*_):return False
class FakeOpener:
 def __init__(self,response=None,error=None):self.response=response;self.error=error;self.calls=[]
 def open(self,request,timeout):
  self.calls.append((request,timeout))
  if self.error:raise self.error
  return self.response
class OfficialSourceHttpTests(unittest.TestCase):
 def setUp(self):self.plan=plan_content_update_notes()
 def fetch(self,response=None,error=None,timeout=15):
  opener=FakeOpener(response or FakeResponse(self.plan.url),error);outcome=fetch_public_official_source(self.plan,timeout_seconds=timeout,opener_factory=lambda:opener);return outcome,opener
 def test_exact_request_is_sent_once(self):
  outcome,opener=self.fetch();request,timeout=opener.calls[0];self.assertEqual("response_quarantined_pending_capture_validation",outcome.status);self.assertEqual((self.plan.url,"GET",15.0),(request.full_url,request.get_method(),timeout))
 def test_plan_headers_are_forwarded_without_authorization(self):
  _,opener=self.fetch();headers={k.lower():v for k,v in opener.calls[0][0].header_items()};self.assertEqual(self.plan.headers["Accept"],headers["accept"]);self.assertNotIn("authorization",headers)
 def test_credentialed_plan_never_opens(self):
  plan=plan_game_data_api("/data/wow/x","static-us");opener=FakeOpener();outcome=fetch_public_official_source(plan,opener_factory=lambda:opener);self.assertEqual("credential_required",outcome.reason);self.assertEqual([],opener.calls)
 def test_oversized_body_fails_closed(self):self.assertEqual("body_incomplete_or_size_invalid",self.fetch(FakeResponse(self.plan.url,b"x"*(self.plan.max_bytes+1),length=False))[0].reason)
 def test_content_length_mismatch_fails_closed(self):
  for length in ("99","bad","-1"):self.assertEqual("body_incomplete_or_size_invalid",self.fetch(FakeResponse(self.plan.url,b"x",length=length))[0].reason)
 def test_content_type_is_validated(self):self.assertEqual("media_type_invalid",self.fetch(FakeResponse(self.plan.url,content_type="application/json"))[0].reason)
 def test_final_url_is_validated(self):self.assertEqual("final_url_not_allowlisted",self.fetch(FakeResponse("https://evil.invalid/x"))[0].reason)
 def test_transport_exception_is_sanitized(self):
  outcome,_=self.fetch(error=OSError("private detail"));self.assertEqual(("evidence_unavailable","transport_error"),(outcome.status,outcome.reason))
 def test_timeout_fails_before_open(self):
  outcome,opener=self.fetch(timeout=31);self.assertEqual("timeout_invalid",outcome.reason);self.assertEqual([],opener.calls)
 def test_response_remains_memory_only(self):
  outcome,_=self.fetch();self.assertEqual(b"official",outcome.response.body);self.assertFalse(hasattr(outcome,"path"))
if __name__=="__main__":unittest.main()
