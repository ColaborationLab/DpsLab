from dataclasses import replace
import ctypes
from io import BytesIO
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image
from PySide6 import QtGui, QtWidgets
from dpslab.local_item_icons import LocalCasc, LocalIconError, decode_blp, wow_root, read_icons, ItemIcons
from dpslab.foundry_gear import GearCards
from dpslab.addon_live_analysis_transport import LiveAnalysisItem


class LocalItemIconTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def test_blp_decode_is_bounded(self):
        data = BytesIO()
        Image.new('P', (4, 4)).save(data, format='BLP')
        self.assertEqual(4, decode_blp(data.getvalue()).width())
        for invalid in (b'bad', b'BLP2' + bytes(8) + struct.pack('<II', 999999, 1) + bytes(200)):
            with self.assertRaises(LocalIconError):
                decode_blp(invalid)

    def test_only_local_retail_layout_is_accepted(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'Data/data').mkdir(parents=True)
            (root / '.build.info').touch()
            addon = root / '_retail_/Interface/AddOns/DpsLab'
            addon.mkdir(parents=True)
            self.assertEqual(root, wow_root(addon))
            for invalid in (Path('relative'), root / 'other', Path('//server/share/_retail_/Interface/AddOns/DpsLab')):
                with self.assertRaises(LocalIconError):
                    wow_root(invalid)

    def test_missing_local_file_is_not_downloaded_and_storage_closes(self):
        with patch('dpslab.local_item_icons.LocalCasc') as storage:
            storage.return_value.read.side_effect = LocalIconError('icon_file_unavailable')
            self.assertEqual({}, read_icons(Path('local'), (123,)))
            storage.return_value.close.assert_called_once()
        with self.assertRaises(LocalIconError):
            read_icons(Path('local'), tuple(range(20)))

    @unittest.skipUnless(hasattr(ctypes, 'WinDLL'), 'Windows native API')
    def test_native_open_is_offline_and_download_callbacks_cancel(self):
        with patch('dpslab.local_item_icons.ctypes.WinDLL') as dll, patch.object(Path, 'is_file', return_value=True):
            storage = LocalCasc(Path('local'))
            call = dll.return_value.CascOpenStorageEx.call_args.args
            self.assertFalse(call[2])
            self.assertEqual('wow', call[1]._obj.product)
            for message in range(5):
                self.assertEqual(message in (2, 4), storage._progress(None, message, None, 0, 0))
            storage.close()

    def test_cards_replace_and_clear_placeholder(self):
        card = GearCards(lambda key, fallback: fallback)
        item = LiveAnalysisItem(1, 100, 'item:1', 1, 'slot_1', 'equipped', icon_file_data_id=123)
        card.show_equipment((item,))
        label = card._icon_labels[0][1]
        self.assertEqual('◇', label.text())
        image = QtGui.QImage(4, 4, QtGui.QImage.Format.Format_RGBA8888)
        image.fill(QtGui.QColor('red'))
        card.set_icons({123: image})
        self.assertFalse(label.pixmap().isNull())
        card.show_equipment((replace(item, icon_file_data_id=None),))
        self.assertEqual('◇', card._icon_labels[0][1].text())
        card.close()

    def test_stale_completion_cannot_repopulate_cleared_profile(self):
        loader = ItemIcons()
        received = []
        loader.changed.connect(received.append)
        loader._active = ('old',)
        loader._results.put((('old',), {123: 'old'}))
        loader._poll()
        self.assertEqual([], received)
        self.assertIsNone(loader._active)
