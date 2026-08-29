import hashlib
import tempfile
import unittest
from pathlib import Path

from tools.public_addon_export_rehearsal import (
    ExportRehearsalError,
    materialize_synthetic_export,
)


def entry(path: str, classification: str, content: bytes) -> dict[str, object]:
    return {
        "path": path,
        "classification": classification,
        "content": content,
        "sha256": hashlib.sha256(content).hexdigest(),
    }


class PublicAddonExportRehearsalTests(unittest.TestCase):
    def test_materializes_only_validated_synthetic_entries(self) -> None:
        manifest = [
            entry("DpsLab/DpsLab.toc", "public_safe_addon", b"## Interface: 120000\n"),
            entry("README.md", "public_safe_documentation", b"Synthetic rehearsal only.\n"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "public-addon"
            receipt = materialize_synthetic_export(manifest, target)
            self.assertEqual(receipt.file_count, 2)
            self.assertEqual([path for path, _digest in receipt.file_sha256], ["DpsLab/DpsLab.toc", "README.md"])
            self.assertEqual((target / "DpsLab" / "DpsLab.toc").read_bytes(), manifest[0]["content"])
            self.assertEqual((target / "README.md").read_bytes(), manifest[1]["content"])
            self.assertEqual(sorted(path.relative_to(target).as_posix() for path in target.rglob("*") if path.is_file()), ["DpsLab/DpsLab.toc", "README.md"])

    def test_receipt_is_deterministic_for_manifest_order(self) -> None:
        first = entry("a.lua", "public_safe_addon", b"print('a')\n")
        second = entry("docs/README.md", "public_safe_documentation", b"synthetic\n")
        with tempfile.TemporaryDirectory() as tmp:
            left = materialize_synthetic_export([first, second], Path(tmp) / "left")
            right = materialize_synthetic_export([second, first], Path(tmp) / "right")
        self.assertEqual(left.aggregate_sha256, right.aggregate_sha256)
        self.assertEqual(left.file_sha256, right.file_sha256)

    def test_rejects_non_public_classifications(self) -> None:
        for classification in ("private_only", "review_required", "unknown"):
            with self.subTest(classification=classification), tempfile.TemporaryDirectory() as tmp:
                with self.assertRaisesRegex(ExportRehearsalError, "unapproved classification"):
                    materialize_synthetic_export([entry("a.lua", classification, b"x")], Path(tmp) / "out")

    def test_rejects_unsafe_and_duplicate_paths(self) -> None:
        unsafe = ("../private.txt", "/absolute.txt", "folder\\file.lua", "./file.lua")
        for path in unsafe:
            with self.subTest(path=path), tempfile.TemporaryDirectory() as tmp:
                with self.assertRaises(ExportRehearsalError):
                    materialize_synthetic_export([entry(path, "public_safe_addon", b"x")], Path(tmp) / "out")
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ExportRehearsalError, "duplicate path"):
                materialize_synthetic_export(
                    [entry("a.lua", "public_safe_addon", b"x"), entry("a.lua", "public_safe_addon", b"y")],
                    Path(tmp) / "out",
                )

    def test_rejects_hash_mismatch_and_secret_shaped_content_without_output(self) -> None:
        broken = entry("a.lua", "public_safe_addon", b"safe")
        broken["sha256"] = "0" * 64
        secret = entry("b.lua", "public_safe_addon", b"token ghp_abcdefghijk")
        for manifest in ([broken], [secret]):
            with self.subTest(manifest=manifest), tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / "out"
                with self.assertRaises(ExportRehearsalError):
                    materialize_synthetic_export(manifest, target)
                self.assertFalse(target.exists())

    def test_rejects_existing_staging_path_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "out"
            target.mkdir()
            sentinel = target / "sentinel.txt"
            sentinel.write_text("keep", encoding="utf-8")
            with self.assertRaisesRegex(ExportRehearsalError, "already exists"):
                materialize_synthetic_export([entry("a.lua", "public_safe_addon", b"x")], target)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()
