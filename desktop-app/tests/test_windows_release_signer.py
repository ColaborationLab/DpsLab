import copy,json,unittest
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
from dpslab.windows_key_protection import build_protected_key_container
from dpslab.windows_release_signer import WindowsReleaseSigner,WindowsReleaseSignerError,sign_manifest_with_protected_key
from dpslab.release_signing import verify_release_signature
ROOT=Path(__file__).resolve().parents[2]
class FakeProtector:
    def protect(self,value):return b"protected:"+value
    def unprotect(self,value):return value.removeprefix(b"protected:")
class ReleaseSignerTests(unittest.TestCase):
    def setUp(self):
        self.private=bytes(range(32));key=Ed25519PrivateKey.from_private_bytes(self.private);self.public=key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw);self.p=FakeProtector();self.c=build_protected_key_container(self.private,"synthetic.release.ed25519.001",self.public,"2026-08-01T00:00:00Z",self.p);self.bundle=json.loads((ROOT/"knowledge/releases/candidate_knowledge_release_bundle_synthetic_0_1.json").read_text());self.registry=json.loads((ROOT/"knowledge/trust/release_trust_registry_synthetic_0_1.json").read_text())
    def test_01_signature_is_detached(self):self.assertEqual(len(WindowsReleaseSigner(self.c,self.p).sign(b"payload")),64)
    def test_02_key_id_is_public(self):self.assertEqual(WindowsReleaseSigner(self.c,self.p).key_id,"synthetic.release.ed25519.001")
    def test_03_no_private_key_property(self):self.assertFalse(hasattr(WindowsReleaseSigner(self.c,self.p),"private_key"))
    def test_04_empty_payload_rejected(self):self.assertRaises(WindowsReleaseSignerError,WindowsReleaseSigner(self.c,self.p).sign,b"")
    def test_05_text_payload_rejected(self):self.assertRaises(WindowsReleaseSignerError,WindowsReleaseSigner(self.c,self.p).sign,"payload")
    def test_06_fingerprint_mismatch_rejected(self):c=copy.deepcopy(self.c);c["public_key_sha256"]="0"*64;self.assertRaises(WindowsReleaseSignerError,WindowsReleaseSigner(c,self.p).sign,b"payload")
    def test_07_manifest_signature_verifies(self):
        record=sign_manifest_with_protected_key(self.bundle["manifest"],self.c,"2026-08-01T08:00:00Z",self.p);out=verify_release_signature(self.bundle["manifest"],record,self.registry,"2026-08-01T08:00:01Z");self.assertEqual(out.status,"signature_valid_release_eligible")
    def test_08_manifest_is_not_mutated(self):m=copy.deepcopy(self.bundle["manifest"]);sign_manifest_with_protected_key(m,self.c,"2026-08-01T08:00:00Z",self.p);self.assertEqual(m,self.bundle["manifest"])
    def test_09_record_contains_no_ciphertext(self):self.assertNotIn("ciphertext",str(sign_manifest_with_protected_key(self.bundle["manifest"],self.c,"2026-08-01T08:00:00Z",self.p)))
    def test_10_record_contains_no_private_material(self):self.assertNotIn(self.private.hex(),str(sign_manifest_with_protected_key(self.bundle["manifest"],self.c,"2026-08-01T08:00:00Z",self.p)))
    def test_11_tampered_container_fails_closed(self):c=copy.deepcopy(self.c);c["ciphertext_base64"]="eA==";self.assertRaises(Exception,WindowsReleaseSigner(c,self.p).sign,b"payload")
    def test_12_each_signature_is_exact_ed25519(self):
        signature=WindowsReleaseSigner(self.c,self.p).sign(b"exact");Ed25519PrivateKey.from_private_bytes(self.private).public_key().verify(signature,b"exact")
