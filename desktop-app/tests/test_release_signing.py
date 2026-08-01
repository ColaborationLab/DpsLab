import base64,copy,json,unittest
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from dpslab.candidate_release_bundle import calculate_release_manifest_sha256,canonical_release_manifest_bytes
from dpslab.release_signing import ReleaseSigningError,calculate_trust_registry_sha256,sign_release_manifest,validate_release_trust_registry,verify_release_signature

ROOT=Path(__file__).resolve().parents[2]
def load(path):return json.loads((ROOT/path).read_text(encoding="utf-8"))
class ReleaseSigningTests(unittest.TestCase):
    def setUp(self):
        self.bundle=load("knowledge/releases/candidate_knowledge_release_bundle_synthetic_0_1.json");self.manifest=self.bundle["manifest"];self.registry=load("knowledge/trust/release_trust_registry_synthetic_0_1.json");self.private=Ed25519PrivateKey.from_private_bytes(bytes(range(32)));self.record=sign_release_manifest(self.manifest,"synthetic.release.ed25519.001","2026-08-01T08:00:00Z",self.private.sign)
    def rehash(self,r):r["integrity"]["registry_sha256"]="";r["integrity"]["registry_sha256"]=calculate_trust_registry_sha256(r);return r
    def assertRegistryFails(self,mutator):
        r=copy.deepcopy(self.registry);mutator(r);self.rehash(r)
        with self.assertRaises(ReleaseSigningError):validate_release_trust_registry(r)
    def test_01_fixture_valid(self):self.assertEqual(validate_release_trust_registry(self.registry),self.registry)
    def test_02_registry_hash_stable(self):self.assertEqual(calculate_trust_registry_sha256(self.registry),self.registry["integrity"]["registry_sha256"])
    def test_03_signer_receives_exact_bytes(self):
        seen=[];sign_release_manifest(self.manifest,"synthetic.release.ed25519.001","2026-08-01T08:00:00Z",lambda b:(seen.append(b),self.private.sign(b))[1]);self.assertEqual(seen,[canonical_release_manifest_bytes(self.manifest)])
    def test_04_sign_does_not_mutate(self):m=copy.deepcopy(self.manifest);sign_release_manifest(m,"synthetic.release.ed25519.001","2026-08-01T08:00:00Z",self.private.sign);self.assertEqual(m,self.manifest)
    def test_05_verify_success_is_eligibility_only(self):self.assertEqual(verify_release_signature(self.manifest,self.record,self.registry,"2026-08-01T08:00:01Z").status,"signature_valid_release_eligible")
    def test_06_signature_is_64_bytes(self):self.assertEqual(len(base64.b64decode(self.record["signature_base64"])),64)
    def test_07_public_key_is_32_bytes(self):self.assertEqual(len(base64.b64decode(self.registry["keys"][0]["public_key_base64"])),32)
    def test_08_bad_signature_rejected(self):r=copy.deepcopy(self.record);r["signature_base64"]=base64.b64encode(bytes(64)).decode();self.assertRaises(ReleaseSigningError,verify_release_signature,self.manifest,r,self.registry,"2026-08-01T00:00:01Z")
    def test_09_tampered_manifest_rejected(self):
        m=copy.deepcopy(self.manifest);m["identity"]["bundle_id"]="synthetic.changed";m["integrity"]["manifest_sha256"]="";m["integrity"]["manifest_sha256"]=calculate_release_manifest_sha256(m)
        self.assertRaises(ReleaseSigningError,verify_release_signature,m,self.record,self.registry,"2026-08-01T00:00:01Z")
    def test_10_unknown_key_rejected(self):r=copy.deepcopy(self.record);r["key_id"]="synthetic.unknown";self.assertRaises(ReleaseSigningError,verify_release_signature,self.manifest,r,self.registry,"2026-08-01T00:00:01Z")
    def test_11_revoked_key_rejected(self):
        r=copy.deepcopy(self.registry);k=r["keys"][0];k.update(status="revoked",revoked_at="2026-07-01T00:00:00Z",revocation_reason="synthetic compromise");self.rehash(r);self.assertRaises(ReleaseSigningError,verify_release_signature,self.manifest,self.record,r,"2026-08-01T00:00:01Z")
    def test_12_expired_key_rejected(self):r=copy.deepcopy(self.record);r["signed_at"]="2028-01-01T00:00:00Z";self.assertRaises(ReleaseSigningError,verify_release_signature,self.manifest,r,self.registry,"2028-01-01T00:00:01Z")
    def test_13_not_yet_valid_rejected(self):r=copy.deepcopy(self.record);r["signed_at"]="2025-01-01T00:00:00Z";self.assertRaises(ReleaseSigningError,verify_release_signature,self.manifest,r,self.registry,"2025-01-01T00:00:01Z")
    def test_14_future_signature_rejected(self):self.assertRaises(ReleaseSigningError,verify_release_signature,self.manifest,self.record,self.registry,"2026-07-31T23:59:59Z")
    def test_15_wrong_algorithm_rejected(self):r=copy.deepcopy(self.record);r["algorithm"]="rsa";self.assertRaises(ReleaseSigningError,verify_release_signature,self.manifest,r,self.registry,"2026-08-01T00:00:01Z")
    def test_16_wrong_status_rejected(self):r=copy.deepcopy(self.record);r["status"]="published";self.assertRaises(ReleaseSigningError,verify_release_signature,self.manifest,r,self.registry,"2026-08-01T00:00:01Z")
    def test_17_extra_signature_field_rejected(self):r=copy.deepcopy(self.record);r["publish"]=True;self.assertRaises(ReleaseSigningError,verify_release_signature,self.manifest,r,self.registry,"2026-08-01T00:00:01Z")
    def test_18_short_signer_output_rejected(self):self.assertRaises(ReleaseSigningError,sign_release_manifest,self.manifest,"synthetic.release.ed25519.001","2026-08-01T08:00:00Z",lambda _:bytes(63))
    def test_19_text_signer_output_rejected(self):self.assertRaises(ReleaseSigningError,sign_release_manifest,self.manifest,"synthetic.release.ed25519.001","2026-08-01T08:00:00Z",lambda _:"secret")
    def test_20_duplicate_key_rejected(self):self.assertRegistryFails(lambda r:r["keys"].append(copy.deepcopy(r["keys"][0])))
    def test_21_rotation_missing_parent_rejected(self):self.assertRegistryFails(lambda r:r["keys"][0].update(rotated_from_key_id="missing"))
    def test_22_invalid_window_rejected(self):self.assertRegistryFails(lambda r:r["keys"][0].update(valid_until=r["keys"][0]["valid_from"]))
    def test_23_bad_public_key_base64_rejected(self):self.assertRegistryFails(lambda r:r["keys"][0].update(public_key_base64="***"))
    def test_24_short_public_key_rejected(self):self.assertRegistryFails(lambda r:r["keys"][0].update(public_key_base64=base64.b64encode(bytes(31)).decode()))
    def test_25_trusted_with_revocation_rejected(self):self.assertRegistryFails(lambda r:r["keys"][0].update(revoked_at="2026-07-01T00:00:00Z",revocation_reason="x"))
    def test_26_revoked_without_reason_rejected(self):self.assertRegistryFails(lambda r:r["keys"][0].update(status="revoked",revoked_at="2026-07-01T00:00:00Z"))
    def test_27_unknown_registry_field_rejected(self):
        r=copy.deepcopy(self.registry);r["private_key"]="forbidden"
        with self.assertRaises(ReleaseSigningError):validate_release_trust_registry(r)
    def test_28_registry_hash_mismatch_rejected(self):r=copy.deepcopy(self.registry);r["identity"]["content_version"]="0.1.1";self.assertRaises(ReleaseSigningError,validate_release_trust_registry,r)
    def test_29_signature_before_manifest_rejected(self):r=copy.deepcopy(self.record);r["signed_at"]="2026-01-01T00:00:00Z";self.assertRaises(ReleaseSigningError,verify_release_signature,self.manifest,r,self.registry,"2026-08-01T00:00:01Z")
    def test_30_rotation_must_advance_validity(self):
        r=copy.deepcopy(self.registry);child=copy.deepcopy(r["keys"][0]);child.update(key_id="synthetic.release.ed25519.002",rotated_from_key_id="synthetic.release.ed25519.001");r["keys"].append(child);self.rehash(r)
        with self.assertRaises(ReleaseSigningError):validate_release_trust_registry(r)
