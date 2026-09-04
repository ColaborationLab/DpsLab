from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import quality_gate as gate


BASELINE = "b" * 40
DIGEST = "a" * 64


def contract() -> dict:
    return {
        "contract_version": "0.1",
        "task_id": "automation_foundation_0_1",
        "title": "test",
        "baseline_commit": BASELINE,
        "authorization": {
            "status": "authorized_for_implementation",
            "authorization_id": "auth-1",
            "authorized_by": "Daniel",
            "authorized_at": "2026-07-16T00:00:00-05:00",
        },
        "scope": {
            "allowed_paths": ["allowed.txt", "new.txt", "old.txt"],
            "generated_paths": [
                ".dpslab/quality-gates/automation_foundation_0_1/implementation.json",
                ".dpslab/quality-gates/automation_foundation_0_1/audit.json",
            ],
            "forbidden_paths": ["forbidden/**"],
            "allow_deletions": False,
            "allow_renames": False,
        },
        "tests": {
            "focused": {
                "working_directory": ".",
                "argv": ["python", "-m", "unittest"],
                "environment": {"PYTHONDONTWRITEBYTECODE": "1"},
            },
            "full": {
                "working_directory": "app",
                "argv": ["python", "-m", "unittest"],
                "environment": {"PYTHONPATH": "src"},
            },
            "baseline_test_count": 208,
            "minimum_test_count": 208,
        },
        "protected_files": {"protected.txt": DIGEST},
        "audit": {"required": True, "independence": "declared_and_procedural"},
        "acceptance_criteria": ["pass"],
        "express_exclusions": ["simc"],
    }


def contract_text(value: dict) -> str:
    return (
        f"{gate.BEGIN}\n```json\n"
        f"{json.dumps(value)}\n```\n{gate.END}\n"
    )


def completed(returncode=0, stdout="", stderr=""):
    return subprocess.CompletedProcess([], returncode, stdout, stderr)


class QualityGateTests(unittest.TestCase):
    def test_valid_contract(self):
        parsed = gate.extract_contract(contract_text(contract()))
        self.assertEqual(parsed["task_id"], "automation_foundation_0_1")

    def test_unknown_key_and_missing_key_are_rejected(self):
        for mutate in (
            lambda value: value.update(extra=True),
            lambda value: value.pop("title"),
        ):
            value = contract()
            mutate(value)
            with self.assertRaises(gate.GateError):
                gate.validate_contract(value)

    def test_invalid_task_id(self):
        value = contract()
        value["task_id"] = "../bad"
        with self.assertRaises(gate.GateError):
            gate.validate_contract(value)

    def test_design_only_is_rejected_for_run(self):
        value = contract()
        value["authorization"]["status"] = "design_only"
        with self.assertRaisesRegex(gate.GateError, "not authorized"):
            gate.run_gate(Path("."), value, lambda *_: completed())

    def test_baseline_correct_and_incorrect(self):
        calls = []
        def runner(argv, cwd, env):
            calls.append(argv)
            if "rev-parse" in argv and "--show-toplevel" in argv:
                return completed(stdout=str(cwd))
            if "branch" in argv:
                return completed(stdout="main\n")
            if "rev-parse" in argv:
                return completed(stdout=BASELINE + "\n")
            return completed()
        with tempfile.TemporaryDirectory() as tmp:
            state = gate.repository_state(Path(tmp), BASELINE, runner)
        self.assertEqual(state["baseline"], BASELINE)
        self.assertTrue(any("merge-base" in call for call in calls))

    def test_baseline_not_ancestor_and_git_indeterminate(self):
        def runner(argv, cwd, env):
            return completed(returncode=1, stderr="bad git")
        with self.assertRaisesRegex(gate.GateError, "indeterminate"):
            gate.repository_state(Path("."), BASELINE, runner)

    def test_clean_and_preexisting_changes(self):
        self.assertEqual(gate.parse_name_status(""), [])
        changes = gate.parse_name_status("M\0allowed.txt\0")
        self.assertEqual(changes, [gate.Change("M", "allowed.txt")])

    def test_allowed_and_forbidden_modification(self):
        scope = contract()["scope"]
        self.assertEqual(
            gate.validate_changes([gate.Change("M", "allowed.txt")], scope)[0].path,
            "allowed.txt",
        )
        with self.assertRaises(gate.GateError):
            gate.validate_changes([gate.Change("M", "other.txt")], scope)

    def test_forbidden_precedes_allowed(self):
        scope = contract()["scope"]
        scope["allowed_paths"].append("forbidden/**")
        with self.assertRaisesRegex(gate.GateError, "forbidden"):
            gate.validate_changes([gate.Change("M", "forbidden/file.txt")], scope)

    def test_untracked_allowed_and_forbidden(self):
        scope = contract()["scope"]
        gate.validate_changes([gate.Change("A", "new.txt")], scope)
        with self.assertRaises(gate.GateError):
            gate.validate_changes([gate.Change("A", "unknown.txt")], scope)

    def test_deletion_authorized_and_rejected(self):
        scope = contract()["scope"]
        with self.assertRaisesRegex(gate.GateError, "deletion"):
            gate.validate_changes([gate.Change("D", "old.txt")], scope)
        scope["allow_deletions"] = True
        gate.validate_changes([gate.Change("D", "old.txt")], scope)

    def test_rename_authorized_and_rejected(self):
        scope = contract()["scope"]
        change = gate.Change("R", "new.txt", "old.txt")
        with self.assertRaisesRegex(gate.GateError, "rename"):
            gate.validate_changes([change], scope)
        scope["allow_renames"] = True
        gate.validate_changes([change], scope)

    def test_rename_as_delete_add(self):
        scope = contract()["scope"]
        with self.assertRaises(gate.GateError):
            gate.validate_changes(
                [gate.Change("D", "old.txt"), gate.Change("A", "new.txt")], scope
            )

    def test_absolute_and_traversal_paths(self):
        for value in ("C:/secret", "/secret", "../secret", "a/../secret"):
            with self.subTest(value=value), self.assertRaises(gate.GateError):
                gate.normalize_path(value)

    def test_generated_path_outside_scope(self):
        value = contract()
        value["scope"]["generated_paths"][0] = "outside.json"
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(gate.GateError):
            gate.validate_generated_paths(
                Path(tmp), value, lambda *_: completed()
            )

    def test_symlink_in_generated_paths(self):
        value = contract()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".dpslab").mkdir()
            original = Path.is_symlink
            def simulated_symlink(path):
                return path == root / ".dpslab" or original(path)
            with patch.object(Path, "is_symlink", simulated_symlink):
                with self.assertRaisesRegex(gate.GateError, "symlink"):
                    gate.validate_generated_paths(root, value, lambda *_: completed())

    def test_generated_path_must_be_ignored(self):
        value = contract()
        def runner(argv, cwd, env):
            if "ls-files" in argv:
                return completed()
            return completed(returncode=1)
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(gate.GateError, "not ignored"):
                gate.validate_generated_paths(Path(tmp), value, runner)

    def test_generated_path_correctly_ignored(self):
        value = contract()
        with tempfile.TemporaryDirectory() as tmp:
            gate.validate_generated_paths(
                Path(tmp), value, lambda *_: completed(returncode=0)
            )

    def test_protected_file_altered(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "protected.txt").write_text("wrong", encoding="utf-8")
            with self.assertRaisesRegex(gate.GateError, "hash mismatch"):
                gate.verify_hashes(root, {"protected.txt": DIGEST})

    def test_focused_failure_prevents_full_suite(self):
        value = contract()
        calls = []
        def runner(argv, cwd, env):
            calls.append(argv)
            return completed(returncode=1, stderr="failed")
        with patch.object(gate, "preflight", return_value={"changes": []}):
            with self.assertRaises(gate.GateError):
                gate.run_gate(Path("."), value, runner)
        self.assertEqual(len(calls), 1)

    def test_full_suite_failure(self):
        value = contract()
        results = iter([
            completed(stdout="Ran 1 test in 0.1s\n\nOK\n"),
            completed(returncode=1, stderr="FAILED"),
        ])
        with patch.object(gate, "preflight", return_value={"changes": []}):
            with self.assertRaises(gate.GateError):
                gate.run_gate(Path("."), value, lambda *_: next(results))

    def test_208_and_more_accepted_below_rejected(self):
        for count in (208, 209):
            result = gate.CommandResult(("python",), ".", 0, f"Ran {count} tests in 1s\nOK\n", "", count)
            gate.validate_test_result(result, 208)
        result = gate.CommandResult(("python",), ".", 0, "Ran 207 tests in 1s\nOK\n", "", 207)
        with self.assertRaisesRegex(gate.GateError, "below minimum"):
            gate.validate_test_result(result, 208)

    def test_atomic_write_and_cleanup_after_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "result.json"
            gate.atomic_json(path, {"ok": True})
            self.assertEqual(json.loads(path.read_text()), {"ok": True})
            with patch("quality_gate.os.replace", side_effect=OSError("replace")):
                with self.assertRaises(OSError):
                    gate.atomic_json(path, {"ok": False})
            self.assertEqual(list(Path(tmp).glob("*.tmp")), [])

    def test_equal_auditor_and_implementer_rejected(self):
        with self.assertRaisesRegex(gate.GateError, "distinct"):
            gate.audit_gate(Path("."), contract(), "same", "same", "approved")

    def test_missing_independence_rejected(self):
        value = contract()
        value["audit"]["independence"] = "none"
        with self.assertRaises(gate.GateError):
            gate.validate_contract(value)

    def test_simulationcraft_command_rejected(self):
        value = contract()
        value["tests"]["focused"]["argv"] = ["simc.exe"]
        with self.assertRaisesRegex(gate.GateError, "SimulationCraft"):
            gate.validate_contract(value)

    def test_parse_rename_record(self):
        self.assertEqual(
            gate.parse_name_status("R100\0old.txt\0new.txt\0"),
            [gate.Change("R", "new.txt", "old.txt")],
        )

    def test_git_executable_not_available(self):
        with patch("quality_gate.subprocess.run", side_effect=FileNotFoundError("git")):
            with self.assertRaises(FileNotFoundError):
                gate.default_runner(["git", "status"], Path("."), None)

    def test_path_is_not_a_git_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(gate.GateError, "indeterminate"):
                gate.repository_state(Path(tmp), BASELINE)

    def test_real_repository_preexisting_dirty_state_is_observed(self):
        value = contract()
        changes = [gate.Change("M", "allowed.txt")]
        with patch.object(gate, "collect_changes", return_value=changes), patch.object(
            gate, "repository_state", return_value={"head": BASELINE}
        ), patch.object(gate, "validate_generated_paths"), patch.object(
            gate, "verify_hashes", return_value={}
        ):
            result = gate.preflight(Path("."), value)
        self.assertEqual(result["changes"], [changes[0].__dict__])

    def test_real_repository_out_of_scope_change_is_rejected(self):
        value = contract()
        with patch.object(
            gate, "collect_changes", return_value=[gate.Change("M", "outside.txt")]
        ), patch.object(gate, "repository_state", return_value={"head": BASELINE}):
            with self.assertRaisesRegex(gate.GateError, "outside allowed"):
                gate.preflight(Path("."), value)

    def test_git_dir_is_never_injected(self):
        seen = {}
        def fake_run(argv, **kwargs):
            seen.update(kwargs["env"])
            return completed()
        with patch.dict(os.environ, {"GIT_DIR": "host-fake"}, clear=False), patch(
            "quality_gate.subprocess.run", side_effect=fake_run
        ):
            gate.default_runner(["python"], Path("."), {"GIT_DIR": "contract-fake"})
        self.assertNotIn("GIT_DIR", seen)

    def _candidate_root(self):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        (root / "allowed.txt").write_text("allowed", encoding="utf-8")
        (root / "protected.txt").write_text("protected", encoding="utf-8")
        for args in (("init",), ("config", "user.email", "test@example.invalid"), ("config", "user.name", "test"), ("add", "allowed.txt", "protected.txt"), ("commit", "-m", "base")):
            subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)
        return temporary, root

    def test_temporary_workspace_created_exact_delta_and_ignored_excluded(self):
        temporary, root = self._candidate_root()
        self.addCleanup(temporary.cleanup)
        value = contract()
        changes = [gate.Change("M", "allowed.txt")]
        destination = root / "candidate"
        destination.mkdir()
        with patch.object(
            gate, "candidate_paths", return_value=["allowed.txt", "protected.txt"]
        ):
            manifest = gate.materialize_candidate(root, destination, value, changes)
        self.assertEqual(set(manifest), {"allowed.txt", "protected.txt"})
        self.assertFalse((destination / ".dpslab").exists())

    def test_temporary_repository_clean_with_ephemeral_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            (workspace / "file.txt").write_text("x", encoding="utf-8")
            head = gate.initialize_temporary_repository(workspace)
            self.assertRegex(head, r"^[0-9a-f]{40}$")
            self.assertEqual(
                subprocess.run(
                    ["git", "status", "--porcelain"], cwd=workspace,
                    capture_output=True, text=True, check=True,
                ).stdout,
                "",
            )

    def test_functional_suite_runs_inside_temporary_workspace(self):
        temporary, root = self._candidate_root()
        self.addCleanup(temporary.cleanup)
        value = contract()
        seen = {}
        class Factory:
            def __init__(self, *args, **kwargs):
                self.path = tempfile.mkdtemp()
            def __enter__(self):
                return self.path
            def __exit__(self, *args):
                shutil.rmtree(self.path)
        def execute_in_workspace(workspace, command, runner):
            seen["workspace"] = workspace
            return gate.CommandResult(
                ("python",), ".", 0, "Ran 208 tests in 1s\nOK\n", "", 208
            )
        with patch.object(gate, "materialize_candidate", return_value={}), patch.object(
            gate, "initialize_temporary_repository", return_value="c" * 40
        ), patch.object(gate, "verify_materialized_candidate"), patch.object(
            gate, "execute_test_command", side_effect=execute_in_workspace,
        ):
            result, details = gate.execute_functional_in_temporary_candidate(
                root, value, [], lambda *_: completed(), Factory
            )
        self.assertEqual(result.test_count, 208)
        self.assertFalse(seen["workspace"].exists())
        self.assertTrue(details["workspace_removed"])

    def test_candidate_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            (workspace / "file.txt").write_text("wrong", encoding="utf-8")
            with self.assertRaisesRegex(gate.GateError, "differs"):
                gate.verify_materialized_candidate(workspace, {"file.txt": DIGEST})

    def test_temporary_creation_failure(self):
        temporary, root = self._candidate_root()
        self.addCleanup(temporary.cleanup)
        class BrokenFactory:
            def __init__(self, *args, **kwargs):
                raise OSError("creation")
        with self.assertRaisesRegex(gate.GateError, "workspace failed"):
            gate.execute_functional_in_temporary_candidate(
                root, contract(), [], lambda *_: completed(), BrokenFactory
            )

    def test_temporary_commit_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            with self.assertRaisesRegex(gate.GateError, "temporary Git command"):
                gate.initialize_temporary_repository(
                    workspace, lambda *_: completed(returncode=1, stderr="commit")
                )

    def test_temporary_cleanup_after_success_and_failure(self):
        paths = []
        class Factory:
            def __init__(self, *args, **kwargs):
                self.path = tempfile.mkdtemp()
                paths.append(Path(self.path))
            def __enter__(self):
                return self.path
            def __exit__(self, *args):
                shutil.rmtree(self.path)
        temporary, root = self._candidate_root()
        self.addCleanup(temporary.cleanup)
        with patch.object(gate, "materialize_candidate", return_value={}), patch.object(
            gate, "initialize_temporary_repository", return_value="c" * 40
        ), patch.object(gate, "verify_materialized_candidate"), patch.object(
            gate, "execute_test_command",
            return_value=gate.CommandResult(("python",), ".", 0, "Ran 208 tests in 1s\nOK\n", "", 208),
        ):
            gate.execute_functional_in_temporary_candidate(
                root, contract(), [], lambda *_: completed(), Factory
            )
        self.assertFalse(paths[-1].exists())
        with patch.object(gate, "materialize_candidate", side_effect=gate.GateError("fail")):
            with self.assertRaises(gate.GateError):
                gate.execute_functional_in_temporary_candidate(
                    root, contract(), [], lambda *_: completed(), Factory
                )
        self.assertFalse(paths[-1].exists())

    def test_real_head_index_and_config_are_not_modified(self):
        temporary, root = self._candidate_root()
        self.addCleanup(temporary.cleanup)
        before = gate.real_repository_fingerprint(root)
        with patch.object(gate, "materialize_candidate", return_value={}), patch.object(
            gate, "initialize_temporary_repository", return_value="c" * 40
        ), patch.object(gate, "verify_materialized_candidate"), patch.object(
            gate, "execute_test_command",
            return_value=gate.CommandResult(("python",), ".", 0, "Ran 208 tests in 1s\nOK\n", "", 208),
        ):
            gate.execute_functional_in_temporary_candidate(
                root, contract(), [], lambda *_: completed()
            )
        self.assertEqual(gate.real_repository_fingerprint(root), before)

    def test_fingerprint_supports_real_worktree_and_detects_mutation(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        source = Path(temporary.name) / "source"; source.mkdir()
        worktree = Path(temporary.name) / "worktree"
        for args in (("init",), ("config", "user.email", "test@example.invalid"), ("config", "user.name", "test"), ("commit", "--allow-empty", "-m", "base"), ("worktree", "add", "-b", "other", str(worktree))):
            subprocess.run(["git", *args], cwd=source, check=True, capture_output=True)
        before = gate.real_repository_fingerprint(worktree)
        index = Path(gate.run_git(worktree, ["rev-parse", "--git-path", "index"]).strip())
        if not index.is_absolute(): index = worktree / index
        index.write_bytes(index.read_bytes() + b"x")
        self.assertNotEqual(gate.real_repository_fingerprint(worktree), before)

    def test_audit_requires_valid_decision_and_integrity(self):
        value = contract()
        with self.assertRaisesRegex(gate.GateError, "invalid audit decision"):
            gate.audit_gate(Path("."), value, "a", "b", "other")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / value["scope"]["generated_paths"][0]
            path.parent.mkdir(parents=True)
            document = {"task_id": value["task_id"], "status": "ok"}
            document["document_sha256"] = gate.document_digest(document)
            path.write_text(json.dumps(document), encoding="utf-8")
            with patch.object(gate, "preflight", return_value={}):
                audit = gate.audit_gate(root, value, "a", "b", "changes_required")
            self.assertEqual(audit["decision"], "changes_required")
            self.assertEqual(audit["findings"], [])
            document["status"] = "tampered"
            path.write_text(json.dumps(document), encoding="utf-8")
            with patch.object(gate, "preflight", return_value={}):
                with self.assertRaisesRegex(gate.GateError, "integrity mismatch"):
                    gate.audit_gate(root, value, "a", "b", "blocked")


if __name__ == "__main__":
    unittest.main()
