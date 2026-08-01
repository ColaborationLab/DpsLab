import json,tempfile,unittest
from pathlib import Path
from dpslab.release_key_ceremony_executor import CeremonyConfirmation,CeremonyExecutionPlan,CeremonyExecutorError,execute_attended_ceremony
class Protector:
    def protect(self,v):return b"dpapi:"+v
    def unprotect(self,v):return v.removeprefix(b"dpapi:")
class Transaction:
    def __init__(self):self.artifacts=None
    def commit_new(self,a):self.artifacts=dict(a)
class ExecutorTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();r=Path(self.tmp.name).resolve();self.repo=r/"repo";self.repo.mkdir();self.plan=CeremonyExecutionPlan("ceremony.production.001","dpslab.release.ed25519.001","DANIELPC\\dpcs9","2026-08-01T00:00:00Z","2027-08-01T00:00:00Z","a"*64,r/"local"/"key.dpskey",r/"external"/"recovery.enc",r/"records"/"evidence.json",(self.repo,));self.conf=[CeremonyConfirmation(s,"a"*64,"DANIELPC\\dpcs9",f"2026-08-01T00:00:0{i}Z") for i,s in enumerate(("readiness","generation","recovery","registry"),1)];self.tx=Transaction()
    def tearDown(self):self.tmp.cleanup()
    def run_ok(self,**kw):return execute_attended_ceremony(kw.get("plan",self.plan),kw.get("confirmations",self.conf),kw.get("generator",lambda:bytes(range(32))),Protector(),kw.get("encrypt",lambda v:b"recovery:"+v),kw.get("decrypt",lambda v:v.removeprefix(b"recovery:")),self.tx,"2026-08-01T00:01:00Z")
    def changed(self,**kw):return self.plan.__class__(**{**self.plan.__dict__,**kw})
    def test_01_success(self):self.assertEqual(self.run_ok().status,"key_material_created_pending_registry_review")
    def test_02_three_artifacts(self):self.run_ok();self.assertEqual(len(self.tx.artifacts),3)
    def test_03_container_has_no_plaintext(self):self.run_ok();self.assertNotIn(bytes(range(32)),self.tx.artifacts[self.plan.container_path])
    def test_04_evidence_has_no_ciphertext(self):self.run_ok();e=self.tx.artifacts[self.plan.evidence_path];self.assertNotIn(b"dpapi",e);self.assertNotIn(b"recovery:",e)
    def test_05_evidence_is_json(self):self.run_ok();self.assertEqual(json.loads(self.tx.artifacts[self.plan.evidence_path])["algorithm"],"ed25519")
    def test_06_public_key_only(self):self.assertNotIn("private",str(self.run_ok().evidence).lower())
    def test_07_sandbox_operator_rejected(self):self.assertRaises(CeremonyExecutorError,self.run_ok,plan=self.changed(operator_id="DANIELPC\\CodexSandboxOffline"))
    def test_08_wrong_key_prefix_rejected(self):self.assertRaises(CeremonyExecutorError,self.run_ok,plan=self.changed(key_id="other.key"))
    def test_09_bad_plan_hash_rejected(self):self.assertRaises(CeremonyExecutorError,self.run_ok,plan=self.changed(plan_sha256="x"))
    def test_10_invalid_window_rejected(self):self.assertRaises(CeremonyExecutorError,self.run_ok,plan=self.changed(valid_until=self.plan.valid_from))
    def test_11_relative_destination_rejected(self):self.assertRaises(CeremonyExecutorError,self.run_ok,plan=self.changed(container_path=Path("relative")))
    def test_12_duplicate_destination_rejected(self):self.assertRaises(CeremonyExecutorError,self.run_ok,plan=self.changed(recovery_path=self.plan.container_path))
    def test_13_existing_destination_rejected(self):self.plan.container_path.parent.mkdir();self.plan.container_path.write_bytes(b"x");self.assertRaises(CeremonyExecutorError,self.run_ok)
    def test_14_secret_in_repo_rejected(self):self.assertRaises(CeremonyExecutorError,self.run_ok,plan=self.changed(container_path=self.repo/"key"))
    def test_15_confirmation_order_rejected(self):self.assertRaises(CeremonyExecutorError,self.run_ok,confirmations=list(reversed(self.conf)))
    def test_16_missing_confirmation_rejected(self):self.assertRaises(CeremonyExecutorError,self.run_ok,confirmations=self.conf[:3])
    def test_17_plan_binding_rejected(self):c=list(self.conf);c[1]=CeremonyConfirmation("generation","b"*64,c[1].operator_id,c[1].confirmed_at);self.assertRaises(CeremonyExecutorError,self.run_ok,confirmations=c)
    def test_18_operator_binding_rejected(self):c=list(self.conf);c[1]=CeremonyConfirmation("generation",c[1].plan_sha256,"OTHER\\user",c[1].confirmed_at);self.assertRaises(CeremonyExecutorError,self.run_ok,confirmations=c)
    def test_19_time_order_rejected(self):c=list(self.conf);c[2]=CeremonyConfirmation("recovery",c[2].plan_sha256,c[2].operator_id,c[1].confirmed_at);self.assertRaises(CeremonyExecutorError,self.run_ok,confirmations=c)
    def test_20_short_generated_key_rejected(self):self.assertRaises(CeremonyExecutorError,self.run_ok,generator=lambda:b"x")
    def test_21_text_generated_key_rejected(self):self.assertRaises(CeremonyExecutorError,self.run_ok,generator=lambda:"secret")
    def test_22_empty_recovery_rejected(self):self.assertRaises(CeremonyExecutorError,self.run_ok,encrypt=lambda v:b"")
    def test_23_short_recovery_rejected(self):self.assertRaises(CeremonyExecutorError,self.run_ok,decrypt=lambda v:b"x")
    def test_24_recovery_mismatch_rejected(self):self.assertRaises(CeremonyExecutorError,self.run_ok,decrypt=lambda v:bytes(reversed(range(32))))
    def test_25_transaction_receives_bytes(self):self.run_ok();self.assertTrue(all(isinstance(v,bytes) for v in self.tx.artifacts.values()))
    def test_26_paths_not_in_evidence(self):self.assertNotIn(str(self.plan.recovery_path),str(self.run_ok().evidence))
    def test_27_status_is_not_published(self):self.assertNotIn("published",self.run_ok().status)
    def test_28_public_fingerprint_is_sha256(self):self.assertEqual(len(self.run_ok().evidence["public_key_sha256"]),64)
