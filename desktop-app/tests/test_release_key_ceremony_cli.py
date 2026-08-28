import tempfile,unittest
from pathlib import Path
from tests.strict_temporary_cleanup import strict_temporary_cleanup
from dpslab.release_key_ceremony_cli import CeremonyLauncherError,LauncherConfig,LauncherDependencies,calculate_launcher_plan_sha256,confirmation_phrase,read_masked_secret,run_attended_launcher
class Protector:
    def protect(self,v):return b"p:"+v
    def unprotect(self,v):return v.removeprefix(b"p:")
class Tx:
    def __init__(self):self.a=None
    def commit_new(self,a):self.a=dict(a)
class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();r=Path(self.tmp.name).resolve();self.repo=r/"repo";self.repo.mkdir();self.cdir=r/"c";self.fdir=r/"f";self.ddir=r/"d";[p.mkdir() for p in (self.cdir,self.fdir,self.ddir)];self.cfg=LauncherConfig("ceremony.001","dpslab.release.ed25519.001","DANIELPC\\dpcs9","2026-08-01T00:00:00Z","2027-08-01T00:00:00Z",self.cdir/"key",self.fdir/"recovery",self.ddir/"evidence",(self.repo,));self.plan=calculate_launcher_plan_sha256(self.cfg);self.answers=[confirmation_phrase(s,self.plan) for s in ("readiness","generation","recovery","registry")];self.secrets=["synthetic password 001","synthetic password 001"];self.out=[];self.tx=Tx();self.times=iter([f"2026-08-01T00:00:0{i}Z" for i in range(1,6)])
    def tearDown(self):strict_temporary_cleanup(self.tmp,Path(self.tmp.name))
    def deps(self,identity="DANIELPC\\dpcs9",answers=None,secrets=None):
        a=iter(self.answers if answers is None else answers);s=iter(self.secrets if secrets is None else secrets);return LauncherDependencies(lambda:identity,lambda _:next(a),lambda _:next(s),self.out.append,lambda:next(self.times),lambda:bytes(range(32)),Protector(),self.tx)
    def test_01_success(self):self.assertEqual(run_attended_launcher(self.cfg,self.deps()).status,"key_material_created_pending_registry_review")
    def test_02_plan_stable(self):self.assertEqual(calculate_launcher_plan_sha256(self.cfg),self.plan)
    def test_03_phrase_bound(self):self.assertEqual(confirmation_phrase("readiness",self.plan),f"CONFIRMO READINESS {self.plan[:12]}")
    def test_04_summary_identity(self):run_attended_launcher(self.cfg,self.deps());self.assertIn("Operador: DANIELPC\\dpcs9",self.out)
    def test_05_summary_key(self):run_attended_launcher(self.cfg,self.deps());self.assertTrue(any(self.cfg.key_id in x for x in self.out))
    def test_06_summary_paths(self):run_attended_launcher(self.cfg,self.deps());self.assertTrue(any(str(self.cfg.recovery_path) in x for x in self.out))
    def test_07_password_not_output(self):run_attended_launcher(self.cfg,self.deps());self.assertNotIn("synthetic password",str(self.out))
    def test_08_sandbox_rejected(self):self.assertRaises(CeremonyLauncherError,run_attended_launcher,self.cfg,self.deps(identity="DANIELPC\\CodexSandboxOffline"))
    def test_09_other_operator_rejected(self):self.assertRaises(CeremonyLauncherError,run_attended_launcher,self.cfg,self.deps(identity="OTHER\\user"))
    def test_10_first_checkpoint_rejected(self):self.assertRaises(CeremonyLauncherError,run_attended_launcher,self.cfg,self.deps(answers=["no"]))
    def test_11_second_checkpoint_rejected(self):a=list(self.answers);a[1]="no";self.assertRaises(CeremonyLauncherError,run_attended_launcher,self.cfg,self.deps(answers=a))
    def test_12_third_checkpoint_rejected(self):a=list(self.answers);a[2]="no";self.assertRaises(CeremonyLauncherError,run_attended_launcher,self.cfg,self.deps(answers=a))
    def test_13_fourth_checkpoint_rejected(self):a=list(self.answers);a[3]="no";self.assertRaises(CeremonyLauncherError,run_attended_launcher,self.cfg,self.deps(answers=a))
    def test_14_mismatched_password_rejected(self):self.assertRaises(CeremonyLauncherError,run_attended_launcher,self.cfg,self.deps(secrets=["synthetic password 001","different password 002"]*3))
    def test_15_short_password_rejected(self):self.assertRaises(CeremonyLauncherError,run_attended_launcher,self.cfg,self.deps(secrets=["short","short"]*3))
    def test_16_existing_target_rejected(self):self.cfg.recovery_path.write_bytes(b"x");self.assertRaises(CeremonyLauncherError,run_attended_launcher,self.cfg,self.deps())
    def test_17_missing_parent_rejected(self):cfg=self.cfg.__class__(**{**self.cfg.__dict__,"recovery_path":self.fdir/"missing"/"x"});self.assertRaises(CeremonyLauncherError,run_attended_launcher,cfg,self.deps())
    def test_18_three_artifacts(self):run_attended_launcher(self.cfg,self.deps());self.assertEqual(len(self.tx.a),3)
    def test_19_recovery_is_encrypted_json(self):run_attended_launcher(self.cfg,self.deps());self.assertIn(b"aes-256-gcm",self.tx.a[self.cfg.recovery_path])
    def test_20_no_generation_before_confirmations(self):
        called=[];d=self.deps(answers=["no"]);d.generate_key=lambda:(called.append(True),bytes(32))[1];self.assertRaises(CeremonyLauncherError,run_attended_launcher,self.cfg,d);self.assertEqual(called,[])
    def test_21_surrounding_whitespace_is_ignored(self):self.assertEqual(run_attended_launcher(self.cfg,self.deps(answers=[f"  {value}  " for value in self.answers])).status,"key_material_created_pending_registry_review")
    def test_22_masked_input_returns_text(self):chars=iter("secret phrase\r");out=[];self.assertEqual(read_masked_secret("P: ",lambda:next(chars),out.append),"secret phrase")
    def test_23_masked_input_shows_only_stars(self):chars=iter("secret\r");out=[];read_masked_secret("P: ",lambda:next(chars),out.append);self.assertNotIn("secret","".join(out));self.assertEqual("".join(out).count("*"),6)
    def test_24_masked_backspace_corrects(self):chars=iter("abx\bc\r");out=[];self.assertEqual(read_masked_secret("P: ",lambda:next(chars),out.append),"abc")
    def test_25_masked_special_key_ignored(self):chars=iter(["a","\xe0","K","b","\r"]);out=[];self.assertEqual(read_masked_secret("P: ",lambda:next(chars),out.append),"ab")
    def test_26_masked_ctrl_c_aborts(self):chars=iter(["a","\x03"]);self.assertRaises(KeyboardInterrupt,read_masked_secret,"P: ",lambda:next(chars),lambda _:None)
    def test_27_password_mismatch_can_retry(self):self.assertEqual(run_attended_launcher(self.cfg,self.deps(secrets=["first password value","different password xx","synthetic password 001","synthetic password 001"])).status,"key_material_created_pending_registry_review")
    def test_28_short_password_can_retry(self):self.assertEqual(run_attended_launcher(self.cfg,self.deps(secrets=["short","short","synthetic password 001","synthetic password 001"])).status,"key_material_created_pending_registry_review")
    def test_29_retry_message_contains_no_secret(self):run_attended_launcher(self.cfg,self.deps(secrets=["first password value","different password xx","synthetic password 001","synthetic password 001"]));self.assertIn("Las contrasenas no coinciden. Intente nuevamente.",self.out);self.assertNotIn("first password",str(self.out))
