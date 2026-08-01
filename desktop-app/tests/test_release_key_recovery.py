import base64,copy,unittest
from dpslab.release_key_recovery import ReleaseKeyRecoveryError,calculate_recovery_bundle_sha256,decrypt_recovery_bundle,encrypt_recovery_bundle,validate_recovery_bundle
class RecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.private=bytes(range(32));cls.password=b"synthetic passphrase only 001";cls.bundle=encrypt_recovery_bundle(cls.private,cls.password,"synthetic.release.001")
    def rehash(self,b):b["integrity"]["bundle_sha256"]="";b["integrity"]["bundle_sha256"]=calculate_recovery_bundle_sha256(b);return b
    def test_01_round_trip(self):self.assertEqual(decrypt_recovery_bundle(self.bundle,self.password),self.private)
    def test_02_bundle_valid(self):self.assertEqual(validate_recovery_bundle(self.bundle),self.bundle)
    def test_03_private_not_plaintext(self):self.assertNotIn(self.private.hex(),str(self.bundle))
    def test_04_passphrase_not_stored(self):self.assertNotIn(self.password.decode(),str(self.bundle))
    def test_05_aes_256_gcm(self):self.assertEqual(self.bundle["cipher"]["name"],"aes-256-gcm")
    def test_06_scrypt_parameters(self):self.assertEqual((self.bundle["kdf"]["n"],self.bundle["kdf"]["r"],self.bundle["kdf"]["p"]),(32768,8,1))
    def test_07_salt_16_bytes(self):self.assertEqual(len(base64.b64decode(self.bundle["kdf"]["salt_base64"])),16)
    def test_08_nonce_12_bytes(self):self.assertEqual(len(base64.b64decode(self.bundle["cipher"]["nonce_base64"])),12)
    def test_09_wrong_password_rejected(self):self.assertRaises(ReleaseKeyRecoveryError,decrypt_recovery_bundle,self.bundle,b"wrong passphrase long enough")
    def test_10_short_password_rejected(self):self.assertRaises(ReleaseKeyRecoveryError,decrypt_recovery_bundle,self.bundle,b"short")
    def test_11_tampered_ciphertext_rejected(self):b=copy.deepcopy(self.bundle);b["cipher"]["ciphertext_base64"]=base64.b64encode(bytes(48)).decode();self.rehash(b);self.assertRaises(ReleaseKeyRecoveryError,decrypt_recovery_bundle,b,self.password)
    def test_12_tampered_identity_rejected(self):b=copy.deepcopy(self.bundle);b["key_id"]="synthetic.other";self.rehash(b);self.assertRaises(ReleaseKeyRecoveryError,decrypt_recovery_bundle,b,self.password)
    def test_13_bad_kdf_rejected(self):b=copy.deepcopy(self.bundle);b["kdf"]["n"]=2;self.rehash(b);self.assertRaises(ReleaseKeyRecoveryError,validate_recovery_bundle,b)
    def test_14_extra_field_rejected(self):b=copy.deepcopy(self.bundle);b["secret"]=None;self.assertRaises(ReleaseKeyRecoveryError,validate_recovery_bundle,b)
    def test_15_hash_mismatch_rejected(self):b=copy.deepcopy(self.bundle);b["key_id"]="synthetic.changed";self.assertRaises(ReleaseKeyRecoveryError,validate_recovery_bundle,b)
    def test_16_encryption_is_randomized(self):self.assertNotEqual(encrypt_recovery_bundle(self.private,self.password,"synthetic.release.001")["cipher"],self.bundle["cipher"])
