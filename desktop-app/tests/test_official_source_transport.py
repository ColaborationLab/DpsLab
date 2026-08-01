import unittest

from dpslab.official_source_request import plan_content_update_notes, plan_game_data_api
from dpslab.official_source_transport import RawTransportResponse, execute_injected_transport


class OfficialSourceTransportTests(unittest.TestCase):
    def setUp(self):
        self.plan = plan_content_update_notes()
        self.raw = RawTransportResponse(200, self.plan.url, "text/html; charset=utf-8", b"official bytes", True, '"r1"', None)

    def execute(self, raw=None, plan=None, timeout=15):
        calls = []
        outcome = execute_injected_transport(plan or self.plan, lambda value, seconds: (calls.append((value, seconds)), raw or self.raw)[1], timeout_seconds=timeout)
        return outcome, calls

    def test_success_is_quarantined_only(self):
        outcome, calls = self.execute()
        self.assertEqual("response_quarantined_pending_capture_validation", outcome.status)
        self.assertEqual(b"official bytes", outcome.response.body)
        self.assertEqual(1, len(calls))

    def test_credentialed_plan_stops_before_sender(self):
        plan = plan_game_data_api("/data/wow/x", "static-us")
        outcome, calls = self.execute(plan=plan)
        self.assertEqual("credential_required", outcome.reason)
        self.assertEqual([], calls)

    def test_transport_exception_is_sanitized(self):
        outcome = execute_injected_transport(self.plan, lambda *_: (_ for _ in ()).throw(RuntimeError("secret detail")))
        self.assertEqual(("evidence_unavailable", "transport_error", None), (outcome.status, outcome.reason, outcome.response))

    def test_status_fails_closed(self):
        for status in (201, 301, 404, 500, True):
            raw = RawTransportResponse(status, self.plan.url, "text/html", b"x", True)
            self.assertEqual("status_not_accepted", self.execute(raw=raw)[0].reason)

    def test_final_target_is_confined(self):
        for url in ("http://worldofwarcraft.blizzard.com/en-us/content-update-notes", "https://evil.invalid/en-us/content-update-notes", "https://worldofwarcraft.blizzard.com/other", self.plan.url + "#x"):
            raw = RawTransportResponse(200, url, "text/html", b"x", True)
            self.assertIn(self.execute(raw=raw)[0].reason, {"final_url_not_allowlisted", "final_target_changed"})

    def test_media_type_fails_closed(self):
        raw = RawTransportResponse(200, self.plan.url, "application/json", b"x", True)
        self.assertEqual("media_type_invalid", self.execute(raw=raw)[0].reason)

    def test_body_must_be_complete_bounded_bytes(self):
        candidates = (("text", True), (b"", True), (b"x", False), (b"x" * (self.plan.max_bytes + 1), True))
        for body, complete in candidates:
            raw = RawTransportResponse(200, self.plan.url, "text/html", body, complete)
            self.assertIn(self.execute(raw=raw)[0].reason, {"body_type_invalid", "body_incomplete_or_size_invalid"})

    def test_304_requires_empty_complete_validated_response(self):
        valid = RawTransportResponse(304, self.plan.url, "text/html", b"", True, '"r1"')
        self.assertEqual("response_quarantined_pending_capture_validation", self.execute(raw=valid)[0].status)
        for body, complete, etag in ((b"x", True, '"r1"'), (b"", False, '"r1"'), (b"", True, None)):
            raw = RawTransportResponse(304, self.plan.url, "text/html", body, complete, etag)
            self.assertEqual("not_modified_invalid", self.execute(raw=raw)[0].reason)

    def test_cache_validators_reject_control_characters(self):
        raw = RawTransportResponse(200, self.plan.url, "text/html", b"x", True, "bad\r\nheader")
        self.assertEqual("cache_validator_invalid", self.execute(raw=raw)[0].reason)

    def test_timeout_is_bounded_before_sender(self):
        for timeout in (True, 0, 31):
            outcome, calls = self.execute(timeout=timeout)
            self.assertEqual("timeout_invalid", outcome.reason)
            self.assertEqual([], calls)


if __name__ == "__main__":
    unittest.main()
