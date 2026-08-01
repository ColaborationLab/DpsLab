import copy,unittest
from dpslab.release_key_ceremony import ReleaseKeyCeremonyError,calculate_ceremony_plan_sha256,evaluate_ceremony_dry_run,validate_ceremony_plan
def plan():
    p={"schema_version":"0.1","mode":"synthetic_dry_run","identity":{"ceremony_id":"synthetic.ceremony.001","key_id":"synthetic.release.001","algorithm":"ed25519","proposed_valid_from":"2026-08-01T00:00:00Z","proposed_valid_until":"2027-08-01T00:00:00Z"},"destinations":{"local_container":"synthetic://local/container","recovery_copy":"synthetic://media/recovery","recovery_record":"synthetic://media/record"},"checkpoints":["readiness","generation","recovery","registry"],"integrity":{"hash_algorithm":"sha256","plan_sha256":""}};p["integrity"]["plan_sha256"]=calculate_ceremony_plan_sha256(p);return p
def observations():return {"repository_clean":True,"remote_synchronized":True,"ci_green":True,"operator_attested":True,"destinations_available":True,"media_present":True,"recording_disabled":True}
def confirmations():return {"readiness":True,"generation":True,"recovery":True,"registry":True}
class CeremonyTests(unittest.TestCase):
    def test_01_plan_valid(self):self.assertEqual(validate_ceremony_plan(plan()),plan())
    def test_02_ready(self):self.assertEqual(evaluate_ceremony_dry_run(plan(),observations(),confirmations(),"2026-08-01T01:00:00Z").status,"synthetic_dry_run_ready")
    def test_03_evidence_is_synthetic(self):self.assertEqual(evaluate_ceremony_dry_run(plan(),observations(),confirmations(),"2026-08-01T01:00:00Z").evidence["mode"],"synthetic_dry_run")
    def test_04_no_secret_fields(self):self.assertNotIn("private",str(evaluate_ceremony_dry_run(plan(),observations(),confirmations(),"2026-08-01T01:00:00Z").evidence).lower())
    def test_05_plan_not_mutated(self):p=plan();evaluate_ceremony_dry_run(p,observations(),confirmations(),"2026-08-01T01:00:00Z");self.assertEqual(p,plan())
    def test_06_production_mode_rejected(self):p=plan();p["mode"]="production";p["integrity"]["plan_sha256"]=calculate_ceremony_plan_sha256(p);self.assertRaises(ReleaseKeyCeremonyError,validate_ceremony_plan,p)
    def test_07_real_path_rejected(self):p=plan();p["destinations"]["local_container"]="C:/secret";p["integrity"]["plan_sha256"]=calculate_ceremony_plan_sha256(p);self.assertRaises(ReleaseKeyCeremonyError,validate_ceremony_plan,p)
    def test_08_duplicate_destination_rejected(self):p=plan();p["destinations"]["recovery_copy"]=p["destinations"]["local_container"];p["integrity"]["plan_sha256"]=calculate_ceremony_plan_sha256(p);self.assertRaises(ReleaseKeyCeremonyError,validate_ceremony_plan,p)
    def test_09_non_synthetic_key_rejected(self):p=plan();p["identity"]["key_id"]="dpslab.real";p["integrity"]["plan_sha256"]=calculate_ceremony_plan_sha256(p);self.assertRaises(ReleaseKeyCeremonyError,validate_ceremony_plan,p)
    def test_10_wrong_algorithm_rejected(self):p=plan();p["identity"]["algorithm"]="rsa";p["integrity"]["plan_sha256"]=calculate_ceremony_plan_sha256(p);self.assertRaises(ReleaseKeyCeremonyError,validate_ceremony_plan,p)
    def test_11_invalid_window_rejected(self):p=plan();p["identity"]["proposed_valid_until"]=p["identity"]["proposed_valid_from"];p["integrity"]["plan_sha256"]=calculate_ceremony_plan_sha256(p);self.assertRaises(ReleaseKeyCeremonyError,validate_ceremony_plan,p)
    def test_12_checkpoint_order_closed(self):p=plan();p["checkpoints"].reverse();p["integrity"]["plan_sha256"]=calculate_ceremony_plan_sha256(p);self.assertRaises(ReleaseKeyCeremonyError,validate_ceremony_plan,p)
    def test_13_hash_mismatch_rejected(self):p=plan();p["identity"]["ceremony_id"]="synthetic.changed";self.assertRaises(ReleaseKeyCeremonyError,validate_ceremony_plan,p)
    def test_14_extra_plan_field_rejected(self):p=plan();p["secret"]=None;self.assertRaises(ReleaseKeyCeremonyError,validate_ceremony_plan,p)
    def test_15_observation_false_aborts(self):o=observations();o["ci_green"]=False;self.assertEqual(evaluate_ceremony_dry_run(plan(),o,confirmations(),"2026-08-01T01:00:00Z").reason,"observation_ci_green_failed")
    def test_16_first_observation_reason_is_stable(self):o=observations();o["repository_clean"]=False;o["ci_green"]=False;self.assertEqual(evaluate_ceremony_dry_run(plan(),o,confirmations(),"2026-08-01T01:00:00Z").reason,"observation_repository_clean_failed")
    def test_17_bool_only_observations(self):o=observations();o["ci_green"]=1;self.assertRaises(ReleaseKeyCeremonyError,evaluate_ceremony_dry_run,plan(),o,confirmations(),"2026-08-01T01:00:00Z")
    def test_18_missing_observation_rejected(self):o=observations();o.pop("ci_green");self.assertRaises(ReleaseKeyCeremonyError,evaluate_ceremony_dry_run,plan(),o,confirmations(),"2026-08-01T01:00:00Z")
    def test_19_unconfirmed_checkpoint_aborts(self):c=confirmations();c["recovery"]=False;self.assertEqual(evaluate_ceremony_dry_run(plan(),observations(),c,"2026-08-01T01:00:00Z").reason,"checkpoint_recovery_unconfirmed")
    def test_20_confirmation_order_closed(self):c={"generation":True,"readiness":True,"recovery":True,"registry":True};self.assertRaises(ReleaseKeyCeremonyError,evaluate_ceremony_dry_run,plan(),observations(),c,"2026-08-01T01:00:00Z")
    def test_21_bool_only_confirmations(self):c=confirmations();c["registry"]=1;self.assertRaises(ReleaseKeyCeremonyError,evaluate_ceremony_dry_run,plan(),observations(),c,"2026-08-01T01:00:00Z")
    def test_22_naive_time_rejected(self):self.assertRaises(ReleaseKeyCeremonyError,evaluate_ceremony_dry_run,plan(),observations(),confirmations(),"2026-08-01T01:00:00")
    def test_23_evidence_hash_present(self):self.assertEqual(len(evaluate_ceremony_dry_run(plan(),observations(),confirmations(),"2026-08-01T01:00:00Z").evidence["evidence_sha256"]),64)
    def test_24_evidence_contains_no_destinations(self):self.assertNotIn("destinations",evaluate_ceremony_dry_run(plan(),observations(),confirmations(),"2026-08-01T01:00:00Z").evidence)
