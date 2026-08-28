import copy,tempfile,unittest
from pathlib import Path
from tests.strict_temporary_cleanup import strict_temporary_directory
from dpslab.windows_key_protection import WindowsDataProtector,WindowsKeyProtectionError,build_protected_key_container,protected_key_path,unprotect_container,validate_protected_key_container
class FakeProtector:
    def __init__(self):self.protected=[];self.unprotected=[]
    def protect(self,value):self.protected.append(value);return bytes(x^0xA5 for x in value)
    def unprotect(self,value):self.unprotected.append(value);return bytes(x^0xA5 for x in value)
class KeyProtectionTests(unittest.TestCase):
    def setUp(self):self.p=FakeProtector();self.private=bytes(range(32));self.public=bytes(range(32,64));self.c=build_protected_key_container(self.private,"synthetic.windows.001",self.public,"2026-08-01T00:00:00Z",self.p)
    def test_01_container_valid(self):self.assertEqual(validate_protected_key_container(self.c),self.c)
    def test_02_private_not_stored_plaintext(self):self.assertNotIn(self.private.hex(),str(self.c))
    def test_03_protector_receives_exact_key(self):self.assertEqual(self.p.protected,[self.private])
    def test_04_unprotect_returns_mutable_buffer(self):self.assertEqual(bytes(unprotect_container(self.c,self.p)),self.private)
    def test_05_scope_is_current_user(self):self.assertEqual(self.c["protection"]["scope"],"current_user")
    def test_06_ui_is_forbidden(self):self.assertIs(self.c["protection"]["ui_forbidden"],True)
    def test_07_machine_scope_rejected(self):c=copy.deepcopy(self.c);c["protection"]["scope"]="local_machine";self.assertRaises(WindowsKeyProtectionError,validate_protected_key_container,c)
    def test_08_extra_field_rejected(self):c=copy.deepcopy(self.c);c["secret"]="x";self.assertRaises(WindowsKeyProtectionError,validate_protected_key_container,c)
    def test_09_bad_ciphertext_rejected(self):c=copy.deepcopy(self.c);c["ciphertext_base64"]="***";self.assertRaises(WindowsKeyProtectionError,validate_protected_key_container,c)
    def test_10_short_private_key_rejected(self):self.assertRaises(WindowsKeyProtectionError,build_protected_key_container,b"x","synthetic.windows.001",self.public,"2026-08-01T00:00:00Z",self.p)
    def test_11_path_is_confined(self):
        with strict_temporary_directory() as d:self.assertEqual(protected_key_path(d.resolve(),"synthetic.windows.001").parent,(d.resolve()/"DpsLab"/"signing").resolve())
    def test_12_relative_root_rejected(self):self.assertRaises(WindowsKeyProtectionError,protected_key_path,Path("relative"),"synthetic.windows.001")
    def test_13_dpapi_flags_forbid_ui_without_machine_scope(self):self.assertEqual(WindowsDataProtector.flags,0x01);self.assertEqual(WindowsDataProtector.flags&0x04,0)
    def test_14_dpapi_description_is_fixed(self):self.assertEqual(WindowsDataProtector.description,"DpsLab release key 0.1")
