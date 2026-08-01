import copy
import hashlib
import json
from pathlib import Path
import unittest

from dpslab.patch_evidence import PatchContext
from dpslab.patch_source_adapter import (InjectedResponse, PatchSourceError,
    PreviousCapture, calculate_registry_sha256, canonical_registry_bytes,
    capture_injected_response, handoff_structured_evidence,
    validate_source_registry)

ROOT = Path(__file__).parents[2]
REGISTRY = ROOT / "knowledge/registries/patch_source_registry_synthetic_0_1.json"
OFFICIAL_REGISTRY = ROOT / "knowledge/sources/official_patch_source_registry_0_1.json"
EVIDENCE = ROOT / "knowledge/snapshots/patch_evidence_synthetic_0_1.json"

def rehash(value):
    value["integrity"]["registry_sha256"] = calculate_registry_sha256(value)
    return value

class PatchSourceAdapterTests(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.response = InjectedResponse(200, "patches.synthetic.invalid", "application/json", b'{"synthetic":true}', True, '"r1"', "synthetic-time")
        self.digest = hashlib.sha256(self.response.body).hexdigest()
        self.previous = PreviousCapture(self.digest, '"r1"', "synthetic-time")

    def mutate(self, path, content):
        value = copy.deepcopy(self.registry); target = value
        for part in path[:-1]: target = target[part]
        target[path[-1]] = content
        return rehash(value)

    def test_fixture_is_canonical_and_valid(self):
        self.assertEqual(REGISTRY.read_bytes(), canonical_registry_bytes(validate_source_registry(self.registry)))
    def test_hash_projection_omits_only_hash(self):
        value = copy.deepcopy(self.registry); value["integrity"]["registry_sha256"] = "f" * 64
        self.assertEqual(calculate_registry_sha256(value), calculate_registry_sha256(self.registry))
    def test_wrong_hash_rejected(self):
        value = copy.deepcopy(self.registry); value["integrity"]["registry_sha256"] = "f" * 64
        with self.assertRaisesRegex(PatchSourceError, "sha256_mismatch"): validate_source_registry(value)
    def test_root_closed(self):
        value = copy.deepcopy(self.registry); value["extra"] = True
        with self.assertRaises(PatchSourceError): validate_source_registry(value)
    def test_identity_closed(self):
        value = copy.deepcopy(self.registry); value["identity"]["extra"] = True
        with self.assertRaises(PatchSourceError): validate_source_registry(value)
    def test_source_closed(self):
        value = copy.deepcopy(self.registry); value["sources"][0]["extra"] = True
        with self.assertRaises(PatchSourceError): validate_source_registry(value)
    def test_schema_rejected(self):
        with self.assertRaises(PatchSourceError): validate_source_registry(self.mutate(["schema_version"], "0.2"))
    def test_non_retail_rejected(self):
        with self.assertRaises(PatchSourceError): validate_source_registry(self.mutate(["identity","wow_product"], "classic"))
    def test_empty_sources_rejected(self):
        with self.assertRaises(PatchSourceError): validate_source_registry(self.mutate(["sources"], []))
    def test_duplicate_source_rejected(self):
        value = copy.deepcopy(self.registry); value["sources"].append(copy.deepcopy(value["sources"][0]))
        with self.assertRaisesRegex(PatchSourceError, "duplicate"): validate_source_registry(rehash(value))
    def test_invalid_host_rejected(self):
        with self.assertRaises(PatchSourceError): validate_source_registry(self.mutate(["sources",0,"canonical_host"], "https://bad"))
    def test_duplicate_redirect_rejected(self):
        with self.assertRaises(PatchSourceError): validate_source_registry(self.mutate(["sources",0,"redirect_hosts"], ["cdn.synthetic.invalid","cdn.synthetic.invalid"]))
    def test_canonical_redirect_rejected(self):
        with self.assertRaises(PatchSourceError): validate_source_registry(self.mutate(["sources",0,"redirect_hosts"], ["patches.synthetic.invalid"]))
    def test_unknown_media_policy_rejected(self):
        with self.assertRaises(PatchSourceError): validate_source_registry(self.mutate(["sources",0,"media_types"], ["application/xml"]))
    def test_official_html_registry_is_canonical_and_valid(self):
        registry = json.loads(OFFICIAL_REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(OFFICIAL_REGISTRY.read_bytes(), canonical_registry_bytes(validate_source_registry(registry)))
    def test_official_html_capture_is_pending_review(self):
        registry = json.loads(OFFICIAL_REGISTRY.read_text(encoding="utf-8"))
        response = InjectedResponse(200, "worldofwarcraft.blizzard.com", "text/html", b"<html>official</html>", True, '"revision"', None)
        self.assertEqual("captured_pending_review", capture_injected_response(registry, "blizzard.wow.content_update_notes", response).status)
    def test_html_remains_rejected_for_json_only_source(self):
        response = InjectedResponse(**{**self.response.__dict__, "media_type":"text/html"})
        self.assertEqual("media_type_invalid", capture_injected_response(self.registry, "synthetic.official.patch", response).reason)
    def test_invalid_size_policy_rejected(self):
        for content in (True, 0, 1_048_577):
            with self.assertRaises(PatchSourceError): validate_source_registry(self.mutate(["sources",0,"max_bytes"], content))
    def test_invalid_locale_policy_rejected(self):
        with self.assertRaises(PatchSourceError): validate_source_registry(self.mutate(["sources",0,"locale_policy"], "guess"))
    def test_valid_capture_is_pending_review(self):
        result = capture_injected_response(self.registry, "synthetic.official.patch", self.response)
        self.assertEqual(("captured_pending_review", self.digest, len(self.response.body)), (result.status, result.content_sha256, result.byte_count))
    def test_allowlisted_redirect_is_accepted(self):
        response = InjectedResponse(**{**self.response.__dict__, "final_host":"cdn.synthetic.invalid"})
        self.assertEqual("captured_pending_review", capture_injected_response(self.registry, "synthetic.official.patch", response).status)
    def test_unknown_source_fails_closed(self):
        self.assertEqual("source_not_allowlisted", capture_injected_response(self.registry, "synthetic.unknown", self.response).reason)
    def test_unknown_redirect_fails_closed(self):
        response = InjectedResponse(**{**self.response.__dict__, "final_host":"other.synthetic.invalid"})
        self.assertEqual("redirect_not_allowlisted", capture_injected_response(self.registry, "synthetic.official.patch", response).reason)
    def test_bad_statuses_fail_closed(self):
        for status in (201, 301, 401, 404, 500, True):
            response = InjectedResponse(**{**self.response.__dict__, "status_code":status})
            self.assertEqual("evidence_unavailable", capture_injected_response(self.registry, "synthetic.official.patch", response).status)
    def test_wrong_media_fails_closed(self):
        response = InjectedResponse(**{**self.response.__dict__, "media_type":"text/html"})
        self.assertEqual("media_type_invalid", capture_injected_response(self.registry, "synthetic.official.patch", response).reason)
    def test_partial_transfer_fails_closed(self):
        response = InjectedResponse(**{**self.response.__dict__, "complete":False})
        self.assertEqual("partial_transfer", capture_injected_response(self.registry, "synthetic.official.patch", response).reason)
    def test_empty_body_fails_closed(self):
        response = InjectedResponse(**{**self.response.__dict__, "body":b""})
        self.assertEqual("body_size_invalid", capture_injected_response(self.registry, "synthetic.official.patch", response).reason)
    def test_oversize_body_fails_closed(self):
        response = InjectedResponse(**{**self.response.__dict__, "body":b"x"*1025})
        self.assertEqual("body_size_invalid", capture_injected_response(self.registry, "synthetic.official.patch", response).reason)
    def test_nonbytes_body_fails_closed(self):
        response = InjectedResponse(**{**self.response.__dict__, "body":"text"})
        self.assertEqual("body_type_invalid", capture_injected_response(self.registry, "synthetic.official.patch", response).reason)
    def test_duplicate_reuses_previous(self):
        result = capture_injected_response(self.registry, "synthetic.official.patch", self.response, self.previous)
        self.assertEqual(("duplicate", True), (result.status, result.reused_previous))
    def test_changed_bytes_do_not_reuse_previous(self):
        previous = PreviousCapture("f"*64, '"old"', "old")
        self.assertEqual("captured_pending_review", capture_injected_response(self.registry, "synthetic.official.patch", self.response, previous).status)
    def test_valid_304_reuses_verified_previous(self):
        response = InjectedResponse(304, "patches.synthetic.invalid", "application/json", b"", True, '"r1"', None)
        result = capture_injected_response(self.registry, "synthetic.official.patch", response, self.previous)
        self.assertEqual(("not_modified", self.digest, True), (result.status, result.content_sha256, result.reused_previous))
    def test_304_without_previous_fails_closed(self):
        response = InjectedResponse(304, "patches.synthetic.invalid", "application/json", b"", True, '"r1"', None)
        self.assertEqual("not_modified_without_verified_previous", capture_injected_response(self.registry, "synthetic.official.patch", response).reason)
    def test_304_mismatched_validator_fails_closed(self):
        response = InjectedResponse(304, "patches.synthetic.invalid", "application/json", b"", True, '"other"', None)
        self.assertEqual("not_modified_invalid", capture_injected_response(self.registry, "synthetic.official.patch", response, self.previous).reason)
    def test_304_unknown_host_fails_closed(self):
        response = InjectedResponse(304, "other.synthetic.invalid", "application/json", b"", True, '"r1"', None)
        self.assertEqual("redirect_not_allowlisted", capture_injected_response(self.registry, "synthetic.official.patch", response, self.previous).reason)
    def test_304_wrong_media_fails_closed(self):
        response = InjectedResponse(304, "patches.synthetic.invalid", "text/html", b"", True, '"r1"', None)
        self.assertEqual("media_type_invalid", capture_injected_response(self.registry, "synthetic.official.patch", response, self.previous).reason)
    def test_cache_validators_are_sanitized(self):
        for etag in ("", "bad\r\nvalue", "x"*257):
            response = InjectedResponse(**{**self.response.__dict__, "etag":etag})
            self.assertEqual("cache_validator_invalid", capture_injected_response(self.registry, "synthetic.official.patch", response).reason)
    def test_304_with_body_or_partial_fails_closed(self):
        for body, complete in ((b"unexpected", True), (b"", False)):
            response = InjectedResponse(304, "patches.synthetic.invalid", "application/json", body, complete, '"r1"', None)
            self.assertEqual("not_modified_invalid", capture_injected_response(self.registry, "synthetic.official.patch", response, self.previous).reason)
    def test_invalid_previous_hash_cannot_be_reused(self):
        previous = PreviousCapture("bad", '"r1"', None)
        response = InjectedResponse(304, "patches.synthetic.invalid", "application/json", b"", True, '"r1"', None)
        self.assertEqual("not_modified_without_verified_previous", capture_injected_response(self.registry, "synthetic.official.patch", response, previous).reason)
    def test_handoff_remains_pending_review(self):
        evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        result = handoff_structured_evidence(evidence, PatchContext("retail",120500,120500), frozenset({"synthetic.role.damage"}))
        self.assertEqual("pending_review", result.status)
    def test_fixtures_have_no_real_sources_or_network(self):
        text = (REGISTRY.read_text()+EVIDENCE.read_text()).lower()
        for forbidden in ("battle.net", "blizzard.com", "wowhead", "http://", "https://", "socket", "requests"):
            self.assertNotIn(forbidden, text)

if __name__ == "__main__": unittest.main()
