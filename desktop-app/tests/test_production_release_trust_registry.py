import base64
import hashlib
import json
import unittest
from pathlib import Path

from dpslab.release_signing import calculate_trust_registry_sha256, validate_release_trust_registry


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "knowledge/trust/release_trust_registry_0_1.json"
EXPECTED_KEY_ID = "dpslab.release.ed25519.001"
EXPECTED_FINGERPRINT = "dbcca6f6baf6ceb5e883971ad8727de2a7a858e1669a86d8bcc04d49ba9a4af3"


class ProductionReleaseTrustRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = REGISTRY.read_bytes()
        cls.registry = json.loads(cls.raw)

    def test_registry_validates(self):
        self.assertEqual(self.registry, validate_release_trust_registry(self.registry))

    def test_registry_hash_is_canonical(self):
        self.assertEqual(self.registry["integrity"]["registry_sha256"], calculate_trust_registry_sha256(self.registry))

    def test_public_identity_matches_attested_ceremony(self):
        key = self.registry["keys"][0]
        public = base64.b64decode(key["public_key_base64"], validate=True)
        self.assertEqual(EXPECTED_KEY_ID, key["key_id"])
        self.assertEqual(32, len(public))
        self.assertEqual(EXPECTED_FINGERPRINT, hashlib.sha256(public).hexdigest())

    def test_validity_matches_attested_ceremony(self):
        key = self.registry["keys"][0]
        self.assertEqual("2026-08-01T15:25:53Z", key["valid_from"])
        self.assertEqual("2027-08-01T15:25:53Z", key["valid_until"])

    def test_registry_contains_public_material_only(self):
        text = self.raw.decode("utf-8").lower()
        for forbidden in ("private", "ciphertext", "passphrase", "dpapi", "recovery", "c:\\", "d:\\", "f:\\"):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
