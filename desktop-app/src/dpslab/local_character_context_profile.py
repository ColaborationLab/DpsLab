"""Protected, local-only storage for one explicitly selected character profile."""

from __future__ import annotations

import base64
import ctypes
import json
import os
import re
import secrets
import stat as stat_module
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Protocol


class CharacterContextProfileError(ValueError):
    """The requested profile operation is unavailable or unsafe."""


@dataclass(frozen=True, repr=False)
class CharacterContextProfileInput:
    display_name: str
    realm: str
    class_id: int
    specialization_id: int
    role: str
    level: int
    race_id: int
    client_build: str
    captured_at: str


@dataclass(frozen=True, repr=False)
class StoredCharacterContextProfile:
    state: str
    profile_id: str | None
    context: CharacterContextProfileInput | None


class DataProtector(Protocol):
    def protect(self, plaintext: bytes) -> bytes: ...
    def unprotect(self, ciphertext: bytes) -> bytes: ...


class _DataBlob(ctypes.Structure):
    _fields_ = [("cbData", ctypes.c_ulong), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]


class WindowsProfileProtector:
    """A DPAPI adapter specifically scoped to a local character profile."""

    flags = 0x01
    description = "DpsLab local character context profile 0.1"

    def __init__(self, crypt32: Any = None, kernel32: Any = None):
        if os.name != "nt" and crypt32 is None:
            _fail("character_context_profile_windows_required")
        self._crypt32 = crypt32 or ctypes.WinDLL("crypt32", use_last_error=True)
        self._kernel32 = kernel32 or ctypes.WinDLL("kernel32", use_last_error=True)

    @staticmethod
    def _input(value: bytes) -> tuple[_DataBlob, Any]:
        keepalive = (ctypes.c_ubyte * len(value)).from_buffer_copy(value)
        return _DataBlob(len(value), ctypes.cast(keepalive, ctypes.POINTER(ctypes.c_ubyte))), keepalive

    def _output(self, blob: _DataBlob) -> bytes:
        try:
            return ctypes.string_at(blob.pbData, blob.cbData)
        finally:
            self._kernel32.LocalFree(blob.pbData)

    def protect(self, plaintext: bytes) -> bytes:
        if not isinstance(plaintext, bytes) or not plaintext:
            _fail("character_context_profile_plaintext_invalid")
        source, _ = self._input(plaintext)
        output = _DataBlob()
        if not self._crypt32.CryptProtectData(
            ctypes.byref(source), self.description, None, None, None, self.flags, ctypes.byref(output)
        ):
            _fail("character_context_profile_protection_failed")
        return self._output(output)

    def unprotect(self, ciphertext: bytes) -> bytes:
        if not isinstance(ciphertext, bytes) or not ciphertext:
            _fail("character_context_profile_ciphertext_invalid")
        source, _ = self._input(ciphertext)
        output = _DataBlob()
        if not self._crypt32.CryptUnprotectData(
            ctypes.byref(source), None, None, None, None, self.flags, ctypes.byref(output)
        ):
            _fail("character_context_profile_protection_failed")
        return self._output(output)


DOCUMENT_NAME = "character_context_profile_0_1.json"
MAX_DOCUMENT_BYTES = 8192
MAX_VALUE_LENGTH = 128
_PROFILE_ID = re.compile(r"^[a-f0-9]{32}$")
_BUILD = re.compile(r"^[0-9]{1,10}$")
_ROLES = frozenset({"damage", "healer", "tank"})
_REPARSE_ATTRIBUTE = getattr(stat_module, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
_ENVELOPE_FIELDS = {"schema_version", "profile_id", "protection", "ciphertext_base64"}
_INNER_FIELDS = {
    "schema_version", "profile_id", "display_name", "realm", "class_id", "specialization_id",
    "role", "level", "race_id", "client_build", "captured_at",
}


def _fail(reason: str) -> None:
    raise CharacterContextProfileError(reason)


def _canonical(document: Mapping[str, Any]) -> bytes:
    return (json.dumps(document, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _fail("character_context_profile_duplicate_key")
        result[key] = value
    return result


def _lstat(path: Path, reason: str) -> os.stat_result:
    try:
        value = path.lstat()
    except OSError as exc:
        raise CharacterContextProfileError(reason) from exc
    if stat_module.S_ISLNK(value.st_mode) or bool(getattr(value, "st_file_attributes", 0) & _REPARSE_ATTRIBUTE):
        _fail("character_context_profile_reparse_rejected")
    return value


def _root(path: Path) -> None:
    if not isinstance(path, Path) or not path.is_absolute():
        _fail("character_context_profile_root_invalid")
    value = _lstat(path, "character_context_profile_root_invalid")
    if not stat_module.S_ISDIR(value.st_mode):
        _fail("character_context_profile_root_invalid")


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not 1 <= len(value) <= MAX_VALUE_LENGTH or "\x00" in value:
        _fail(f"character_context_profile_{field}_invalid")
    return value


def _integer(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 2_147_483_647:
        _fail(f"character_context_profile_{field}_invalid")
    return value


def _time(value: Any) -> str:
    if not isinstance(value, str) or not value.endswith("Z"):
        _fail("character_context_profile_captured_at_invalid")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise CharacterContextProfileError("character_context_profile_captured_at_invalid") from exc
    if parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        _fail("character_context_profile_captured_at_invalid")
    return value


def _validated_input(value: CharacterContextProfileInput) -> CharacterContextProfileInput:
    if not isinstance(value, CharacterContextProfileInput):
        _fail("character_context_profile_input_invalid")
    role = _text(value.role, "role")
    if role not in _ROLES:
        _fail("character_context_profile_role_invalid")
    build = _text(value.client_build, "client_build")
    if _BUILD.fullmatch(build) is None:
        _fail("character_context_profile_client_build_invalid")
    return CharacterContextProfileInput(
        _text(value.display_name, "display_name"), _text(value.realm, "realm"),
        _integer(value.class_id, "class_id"), _integer(value.specialization_id, "specialization_id"),
        role, _integer(value.level, "level"), _integer(value.race_id, "race_id"), build, _time(value.captured_at),
    )


def _inner(profile_id: str, value: CharacterContextProfileInput) -> dict[str, Any]:
    if not isinstance(profile_id, str) or _PROFILE_ID.fullmatch(profile_id) is None:
        _fail("character_context_profile_id_invalid")
    current = _validated_input(value)
    return {
        "schema_version": "0.1", "profile_id": profile_id, "display_name": current.display_name,
        "realm": current.realm, "class_id": current.class_id, "specialization_id": current.specialization_id,
        "role": current.role, "level": current.level, "race_id": current.race_id,
        "client_build": current.client_build, "captured_at": current.captured_at,
    }


def _decode_inner(raw: bytes, expected_profile_id: str) -> CharacterContextProfileInput:
    if not isinstance(raw, bytes) or not 1 <= len(raw) <= MAX_DOCUMENT_BYTES:
        _fail("character_context_profile_plaintext_invalid")
    try:
        document = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CharacterContextProfileError("character_context_profile_plaintext_invalid") from exc
    if not isinstance(document, dict) or set(document) != _INNER_FIELDS or document.get("schema_version") != "0.1":
        _fail("character_context_profile_plaintext_invalid")
    if document.get("profile_id") != expected_profile_id or raw != _canonical(document):
        _fail("character_context_profile_profile_mismatch")
    return _validated_input(CharacterContextProfileInput(
        document["display_name"], document["realm"], document["class_id"], document["specialization_id"],
        document["role"], document["level"], document["race_id"], document["client_build"], document["captured_at"],
    ))


def _target(root: Path) -> Path:
    _root(root)
    return root / DOCUMENT_NAME


def _read_document(target: Path) -> bytes:
    value = _lstat(target, "character_context_profile_file_invalid")
    if not stat_module.S_ISREG(value.st_mode) or not 1 <= value.st_size <= MAX_DOCUMENT_BYTES:
        _fail("character_context_profile_file_invalid")
    try:
        raw = target.read_bytes()
    except OSError as exc:
        raise CharacterContextProfileError("character_context_profile_file_unreadable") from exc
    if len(raw) != value.st_size or _lstat(target, "character_context_profile_file_invalid").st_size != value.st_size:
        _fail("character_context_profile_file_changed")
    return raw


def _load(root: Path, protector: DataProtector) -> tuple[str, CharacterContextProfileInput] | None:
    target = _target(root)
    if not os.path.lexists(target):
        return None
    raw = _read_document(target)
    try:
        envelope = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CharacterContextProfileError("character_context_profile_document_invalid") from exc
    if not isinstance(envelope, dict) or set(envelope) != _ENVELOPE_FIELDS or envelope.get("schema_version") != "0.1":
        _fail("character_context_profile_document_invalid")
    profile_id = envelope.get("profile_id")
    if not isinstance(profile_id, str) or _PROFILE_ID.fullmatch(profile_id) is None:
        _fail("character_context_profile_document_invalid")
    if envelope.get("protection") != {"provider": "windows_dpapi", "scope": "current_user", "ui_forbidden": True}:
        _fail("character_context_profile_document_invalid")
    try:
        ciphertext = base64.b64decode(envelope["ciphertext_base64"], validate=True)
    except (TypeError, ValueError) as exc:
        raise CharacterContextProfileError("character_context_profile_document_invalid") from exc
    if not ciphertext or raw != _canonical(envelope):
        _fail("character_context_profile_document_invalid")
    return profile_id, _decode_inner(protector.unprotect(ciphertext), profile_id)


def inspect_profile(root: Path, protector: DataProtector) -> StoredCharacterContextProfile:
    loaded = _load(root, protector)
    return StoredCharacterContextProfile("absent", None, None) if loaded is None else StoredCharacterContextProfile("selected", loaded[0], loaded[1])


def _write(root: Path, profile_id: str, value: CharacterContextProfileInput, protector: DataProtector) -> None:
    target = _target(root)
    plaintext = _canonical(_inner(profile_id, value))
    ciphertext = protector.protect(plaintext)
    if not isinstance(ciphertext, bytes) or not ciphertext:
        _fail("character_context_profile_protection_failed")
    envelope = {"schema_version": "0.1", "profile_id": profile_id, "protection": {"provider": "windows_dpapi", "scope": "current_user", "ui_forbidden": True}, "ciphertext_base64": base64.b64encode(ciphertext).decode("ascii")}
    raw = _canonical(envelope)
    if len(raw) > MAX_DOCUMENT_BYTES:
        _fail("character_context_profile_document_too_large")
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=root, prefix=".character-context-", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name); stream.write(raw); stream.flush(); os.fsync(stream.fileno())
        if not stat_module.S_ISREG(_lstat(temporary, "character_context_profile_temporary_invalid").st_mode):
            _fail("character_context_profile_temporary_invalid")
        os.replace(temporary, target); temporary = None
        if _read_document(target) != raw:
            _fail("character_context_profile_commit_mismatch")
    except CharacterContextProfileError:
        raise
    except OSError as exc:
        raise CharacterContextProfileError("character_context_profile_write_failed") from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def create_profile(root: Path, value: CharacterContextProfileInput, protector: DataProtector) -> StoredCharacterContextProfile:
    if _load(root, protector) is not None:
        _fail("character_context_profile_already_selected")
    profile_id = secrets.token_hex(16)
    _write(root, profile_id, value, protector)
    return inspect_profile(root, protector)


def replace_selected_profile(root: Path, profile_id: str, value: CharacterContextProfileInput, protector: DataProtector) -> StoredCharacterContextProfile:
    loaded = _load(root, protector)
    if loaded is None or loaded[0] != profile_id:
        _fail("character_context_profile_profile_mismatch")
    _write(root, profile_id, value, protector)
    return inspect_profile(root, protector)


def delete_selected_profile(root: Path, profile_id: str, protector: DataProtector) -> None:
    loaded = _load(root, protector)
    if loaded is None or loaded[0] != profile_id:
        _fail("character_context_profile_profile_mismatch")
    target = _target(root)
    try:
        target.unlink()
    except OSError as exc:
        raise CharacterContextProfileError("character_context_profile_delete_failed") from exc


def clear_all_profiles(root: Path, confirmation: str) -> None:
    if confirmation != "CLEAR_LOCAL_CHARACTER_CONTEXT_PROFILE":
        _fail("character_context_profile_clear_not_confirmed")
    target = _target(root)
    if os.path.lexists(target):
        try:
            target.unlink()
        except OSError as exc:
            raise CharacterContextProfileError("character_context_profile_delete_failed") from exc
