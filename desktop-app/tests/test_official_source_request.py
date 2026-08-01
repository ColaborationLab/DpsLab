import unittest
from urllib.parse import parse_qs, urlsplit

from dpslab.official_source_request import (
    OfficialSourceRequestError,
    plan_content_update_notes,
    plan_game_data_api,
)


class OfficialSourceRequestTests(unittest.TestCase):
    def test_patch_notes_plan_is_exact_and_inert(self):
        plan = plan_content_update_notes()
        self.assertEqual("https://worldofwarcraft.blizzard.com/en-us/content-update-notes", plan.url)
        self.assertEqual(("text/html",), plan.accepted_media_types)
        self.assertEqual("ready_for_injected_transport", plan.status)

    def test_patch_notes_plan_has_no_credentials(self):
        plan = plan_content_update_notes()
        self.assertEqual("none", plan.credential_mode)
        self.assertNotIn("Authorization", plan.headers)

    def test_api_plan_is_exact_and_requires_external_bearer(self):
        plan = plan_game_data_api("/data/wow/playable-specialization/index", "static-us")
        url = urlsplit(plan.url)
        self.assertEqual(("https", "us.api.blizzard.com", "/data/wow/playable-specialization/index"), (url.scheme, url.netloc, url.path))
        self.assertEqual({"namespace": ["static-us"], "locale": ["en_US"]}, parse_qs(url.query))
        self.assertEqual("external_bearer_required", plan.credential_mode)
        self.assertNotIn("Authorization", plan.headers)

    def test_api_path_fails_closed(self):
        for path in ("data/wow/x", "/profile/wow/x", "/data/wow/../secret", "/data/wow/x?access_token=x", "/data/wow/x#fragment"):
            with self.subTest(path=path), self.assertRaisesRegex(OfficialSourceRequestError, "api_path_invalid"):
                plan_game_data_api(path, "static-us")

    def test_namespace_fails_closed(self):
        for namespace in ("static", "profile-us", "static-US", "static-us&locale=es_MX"):
            with self.subTest(namespace=namespace), self.assertRaisesRegex(OfficialSourceRequestError, "namespace_invalid"):
                plan_game_data_api("/data/wow/x", namespace)

    def test_locale_is_closed(self):
        with self.assertRaisesRegex(OfficialSourceRequestError, "locale_invalid"):
            plan_game_data_api("/data/wow/x", "static-us", locale="es_MX")

    def test_conditional_headers_are_sanitized(self):
        plan = plan_content_update_notes('"revision-1"', "Sat, 01 Aug 2026 00:00:00 GMT")
        self.assertEqual('"revision-1"', plan.headers["If-None-Match"])
        self.assertIn("If-Modified-Since", plan.headers)

    def test_control_characters_are_rejected(self):
        for value in ("bad\r\nInjected: true", "", "x" * 257):
            with self.subTest(value=value), self.assertRaises(OfficialSourceRequestError):
                plan_content_update_notes(etag=value)

    def test_headers_are_immutable(self):
        plan = plan_content_update_notes()
        with self.assertRaises(TypeError):
            plan.headers["Authorization"] = "secret"

    def test_plans_have_bounded_body_and_no_redirect_expansion(self):
        for plan in (plan_content_update_notes(), plan_game_data_api("/data/wow/x", "dynamic-us")):
            self.assertEqual(1_048_576, plan.max_bytes)
            self.assertEqual((), plan.allowed_redirect_hosts)
            self.assertEqual("GET", plan.method)


if __name__ == "__main__":
    unittest.main()
