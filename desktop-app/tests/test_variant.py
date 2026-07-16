from __future__ import annotations

import tempfile
import unittest
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch

from dpslab.variant import VariantError, create_effective_profile, load_variant


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SOUL_SHARDS_VARIANT_SHA256 = "9bce78ef272626a1b1bec04b3a72cd21cb217ed7a780d34383c8326b1f8e390b"


VALID = '''[variant]
id = "test_v1"
name = "Test"
description = "Test variant"

[[overrides]]
key = "warlock.soul_shards"
value = "0"
'''


class VariantTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.source = self.root / "variant.toml"
        self.source.write_text(VALID, encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_valid_variant_and_byte_hash(self) -> None:
        loaded = load_variant(self.source)
        self.assertEqual(loaded.variant.id, "test_v1")
        self.assertEqual(loaded.source_sha256, sha256(self.source.read_bytes()).hexdigest())

    def test_repository_soul_shards_variant_hash(self) -> None:
        source = REPOSITORY_ROOT / "variants" / "flasil_soul_shards_0_v1.toml"
        self.assertEqual(sha256(source.read_bytes()).hexdigest(), SOUL_SHARDS_VARIANT_SHA256)

    def test_invalid_and_missing_variant(self) -> None:
        with self.assertRaisesRegex(VariantError, "No existe"):
            load_variant(self.root / "missing.toml")
        self.source.write_text("not toml = [", encoding="utf-8")
        with self.assertRaisesRegex(VariantError, "inválido"):
            load_variant(self.source)

    def test_restricted_and_malformed_keys(self) -> None:
        for key in ("warlock..soul_shards", "warlock.soul_shards=0", "warlock.#x", "global_option"):
            with self.subTest(key=key):
                self.source.write_text(VALID.replace("warlock.soul_shards", key), encoding="utf-8")
                with self.assertRaises(VariantError):
                    load_variant(self.source)

    def test_duplicate_key_is_rejected(self) -> None:
        self.source.write_text(VALID + '\n[[overrides]]\nkey="warlock.soul_shards"\nvalue="1"\n', encoding="utf-8")
        with self.assertRaisesRegex(VariantError, "duplicada"):
            load_variant(self.source)

    def test_effective_profile_preserves_exact_prefix_lf_and_previous_occurrence(self) -> None:
        loaded = load_variant(self.source)
        base = b'warlock="Tester"\nwarlock.soul_shards=3\n# Checksum: abc\n'
        output = self.root / "effective.simc"
        digest, applied = create_effective_profile(base, loaded, output)
        data = output.read_bytes()
        self.assertTrue(data.startswith(base))
        self.assertIn(b"\n# DpsLab Effective Profile\n", data)
        self.assertIn(b"Base SimC addon checksum applies only to the original profile prefix.", data)
        self.assertEqual(applied[0].previous_occurrences, 1)
        self.assertEqual(applied[0].effective_line, "warlock.soul_shards=0")
        self.assertEqual(digest, sha256(data).hexdigest())

    def test_crlf_and_missing_final_newline_are_preserved(self) -> None:
        loaded = load_variant(self.source)
        for base, separator in ((b'a=1\r\nb=2\r\n', b'\r\n'), (b'a=1\nb=2', b'\n')):
            with self.subTest(base=base):
                output = self.root / "effective.simc"
                create_effective_profile(base, loaded, output)
                data = output.read_bytes()
                self.assertTrue(data.startswith(base))
                self.assertIn(separator + b"# DpsLab Effective Profile" + separator, data)

    def test_override_order_is_stable(self) -> None:
        # The restricted first release has one allowed key; ordering is still explicitly recorded.
        loaded = load_variant(self.source)
        _, applied = create_effective_profile(b'a=1\n', loaded, self.root / "effective.simc")
        self.assertEqual([item.order for item in applied], [1])
        self.assertEqual(applied[0].status, "applied")

    def test_effective_profile_uses_atomic_replace(self) -> None:
        loaded = load_variant(self.source)
        destination = self.root / "effective.simc"
        import os
        with patch("dpslab.variant.os.replace", wraps=os.replace) as replace:
            create_effective_profile(b'a=1\n', loaded, destination)
        replace.assert_called_once()
        self.assertEqual(list(self.root.glob(".effective_profile.*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
