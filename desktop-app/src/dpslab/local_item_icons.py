"""Read explicitly imported item icons from the local WoW CASC, never a CDN."""
from __future__ import annotations

import ctypes
from io import BytesIO
from pathlib import Path
import queue
import struct
import threading

from PIL import Image
from PySide6 import QtCore, QtGui


class LocalIconError(ValueError):
    pass


def wow_root(addon: Path) -> Path:
    """Accept only the existing retail addon layout, not URLs or CASC parameters."""
    if not addon.is_absolute() or str(addon).startswith(('\\\\', '//')) or '*' in str(addon):
        raise LocalIconError('icon_path_invalid')
    if tuple(p.lower() for p in addon.parts[-4:]) != ('_retail_', 'interface', 'addons', 'dpslab'):
        raise LocalIconError('icon_path_invalid')
    root = addon.parents[3]
    for path in (addon, *addon.parents, root / 'Data', root / 'Data' / 'data', root / '.build.info'):
        if path.is_symlink() or getattr(path, 'is_junction', lambda: False)():
            raise LocalIconError('icon_path_invalid')
    if not (root / '.build.info').is_file() or not (root / 'Data' / 'data').is_dir():
        raise LocalIconError('icon_storage_unavailable')
    return root


def decode_blp(data: bytes) -> QtGui.QImage:
    if not 148 <= len(data) <= 4 * 1024 * 1024 or data[:4] != b'BLP2':
        raise LocalIconError('icon_format_invalid')
    width, height = struct.unpack_from('<II', data, 12)
    if not (1 <= width <= 512 and 1 <= height <= 512):
        raise LocalIconError('icon_dimensions_invalid')
    with Image.open(BytesIO(data), formats=['BLP']) as source:
        if not (1 <= source.width <= 512 and 1 <= source.height <= 512):
            raise LocalIconError('icon_dimensions_invalid')
        rgba = source.convert('RGBA')
        return QtGui.QImage(rgba.tobytes(), rgba.width, rgba.height,
                           QtGui.QImage.Format.Format_RGBA8888).copy()


class LocalCasc:
    def __init__(self, root: Path):
        dll_path = Path(__file__).parent / 'native' / 'CascLib.dll'
        if not dll_path.is_file() or not hasattr(ctypes, 'WinDLL'):
            raise LocalIconError('icon_reader_unavailable')
        self.dll = ctypes.WinDLL(str(dll_path.resolve()))
        handle, u32 = ctypes.c_void_p, ctypes.c_uint32
        callback = ctypes.WINFUNCTYPE(ctypes.c_bool, handle, ctypes.c_int, ctypes.c_char_p, u32, u32)
        class OpenArgs(ctypes.Structure):
            _fields_ = [('size', ctypes.c_size_t), ('local', ctypes.c_wchar_p),
                        ('product', ctypes.c_wchar_p), ('region', ctypes.c_wchar_p),
                        ('progress', callback), ('progress_context', handle),
                        ('product_callback', handle), ('product_context', handle),
                        ('locale', u32), ('flags', u32), ('build', ctypes.c_wchar_p),
                        ('cdn', ctypes.c_wchar_p)]
        # Keep the callback alive until the storage closes. Cancel before any
        # download, including a manifest fallback if the installation changes.
        self._progress = callback(lambda _context, message, _object, _current, _total: message in (2, 4))
        arguments = OpenArgs(size=ctypes.sizeof(OpenArgs), product='wow', progress=self._progress)
        signatures = {
            'CascOpenStorageEx': [ctypes.c_wchar_p, ctypes.POINTER(OpenArgs), ctypes.c_bool, ctypes.POINTER(handle)],
            'CascCloseStorage': [handle],
            'CascOpenFile': [handle, handle, u32, u32, ctypes.POINTER(handle)],
            'CascGetFileSize64': [handle, ctypes.POINTER(ctypes.c_uint64)],
            'CascReadFile': [handle, handle, u32, ctypes.POINTER(u32)],
            'CascCloseFile': [handle],
            'CascGetStorageInfo': [handle, ctypes.c_int, handle, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)],
        }
        for name, args in signatures.items():
            function = getattr(self.dll, name)
            function.argtypes, function.restype = args, ctypes.c_bool
        self.handle = handle()
        # An exact .build.info path avoids fallback to an online "versions" cache.
        if not self.dll.CascOpenStorageEx(str(root / '.build.info'), ctypes.byref(arguments), False, ctypes.byref(self.handle)):
            raise LocalIconError('icon_storage_unavailable')
        features = u32()
        if not self.dll.CascGetStorageInfo(self.handle, 2, ctypes.byref(features), 4, None) or features.value & 0x400:
            self.close()
            raise LocalIconError('icon_online_storage_rejected')

    def read(self, file_id: int) -> bytes:
        if type(file_id) is not int or not 1 <= file_id <= 2147483647:
            raise LocalIconError('icon_id_invalid')
        handle = ctypes.c_void_p()
        # FILEID + strict data checks; no bypass for missing encryption keys.
        if not self.dll.CascOpenFile(self.handle, ctypes.c_void_p(file_id), 0, 0x13, ctypes.byref(handle)):
            raise LocalIconError('icon_file_unavailable')
        try:
            size = ctypes.c_uint64()
            if not self.dll.CascGetFileSize64(handle, ctypes.byref(size)) or not 148 <= size.value <= 4 * 1024 * 1024:
                raise LocalIconError('icon_size_invalid')
            buffer, read = ctypes.create_string_buffer(size.value), ctypes.c_uint32()
            if not self.dll.CascReadFile(handle, buffer, size.value, ctypes.byref(read)) or read.value != size.value:
                raise LocalIconError('icon_read_failed')
            return buffer.raw
        finally:
            self.dll.CascCloseFile(handle)

    def close(self):
        if self.handle:
            self.dll.CascCloseStorage(self.handle)
            self.handle = ctypes.c_void_p()


def read_icons(root: Path, identifiers: tuple[int, ...]) -> dict[int, QtGui.QImage]:
    if len(identifiers) > 19:
        raise LocalIconError('icon_count_invalid')
    images = {}
    storage = LocalCasc(root)
    try:
        for identifier in identifiers:
            try:
                images[identifier] = decode_blp(storage.read(identifier))
            except (LocalIconError, OSError, ValueError, SyntaxError):
                continue  # Missing local files stay explicit placeholders, never download.
    finally:
        storage.close()
    return images


class ItemIcons(QtCore.QObject):
    changed = QtCore.Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._desired = self._active = None
        self._results = queue.Queue()
        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(100)
        self._timer.timeout.connect(self._poll)

    def request(self, addon: Path, equipment):
        identifiers = tuple(sorted({item.icon_file_data_id for item in equipment if item.icon_file_data_id is not None}))
        try:
            root = wow_root(addon) if identifiers else None
            key = (root, (root / '.build.info').stat().st_mtime_ns, identifiers) if root else None
        except (OSError, LocalIconError):
            key = None
        if key == self._desired:
            return
        self._desired = key
        self.changed.emit({})
        if key and not self._active:
            self._start()

    def _start(self):
        key = self._active = self._desired
        results = self._results
        def work():
            try:
                images = read_icons(key[0], key[2])
            except (OSError, LocalIconError, AttributeError):
                images = {}
            results.put((key, images))
        threading.Thread(target=work, daemon=True).start()
        self._timer.start()

    def _poll(self):
        try:
            key, images = self._results.get_nowait()
        except queue.Empty:
            return
        self._active = None
        self._timer.stop()
        if key == self._desired:
            self.changed.emit(images)
        elif self._desired:
            self._start()
