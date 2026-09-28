import unittest
from PySide6 import QtWidgets
from dpslab.foundry_gear import GearCards, percentage_label, item_name
from dpslab.addon_live_analysis_transport import LiveAnalysisItem
from dpslab.loadout_recommendation import LoadoutComparison


class GearTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def test_signed_colored_direction_and_missing_reference(self):
        for value, role, arrow in ((110, 'positive', '↑'), (90, 'negative', '↓')):
            label = percentage_label(value, 100)
            self.assertEqual(role, label.property('role'))
            self.assertIn(arrow, label.text())
        self.assertEqual('', percentage_label(100, 100).text())
        self.assertEqual('', percentage_label(100, 0).text())

    def test_equipment_and_recommendations_do_not_invent_item_deltas(self):
        item = LiveAnalysisItem(123, 250, '|h[Test Item]|h', 1, 'slot_1', 'equipped', stats=(('Intellect', 42),))
        self.assertEqual('Test Item', item_name(item))
        view = GearCards(lambda key, fallback: fallback)
        result = LoadoutComparison('Done', ((1, 100), (2, 110)), 2, 1, 71, 'damage')
        view.show_equipment((item,), result, {1: 'A', 2: 'B'})
        text = ' '.join(label.text() for label in view.widget().findChildren(QtWidgets.QLabel))
        self.assertIn('Test Item', text)
        self.assertIn('250', text)
        self.assertTrue(any('Intellect: 42' in frame.toolTip() for frame in view.findChildren(QtWidgets.QFrame)))
        self.assertIn('No item substitutions', text)
        equipment_cards = [frame for frame in view.findChildren(QtWidgets.QFrame) if 'Intellect: 42' in frame.toolTip()]
        self.assertEqual(68, equipment_cards[0].minimumHeight())
        view.show_recommendations(result, {1: 'A', 2: 'B'})
        text = ' '.join(label.text() for label in view.widget().findChildren(QtWidgets.QLabel))
        self.assertIn('1. A → B', text)
        self.assertIn('+10.00 %', text)
        view.show_equipment(())
        self.assertNotIn('Test Item', ' '.join(label.text() for label in view.widget().findChildren(QtWidgets.QLabel)))

    def test_full_equipment_scrolls_instead_of_overlapping(self):
        view = GearCards(lambda key, fallback: fallback)
        view.resize(600, 260)
        items = tuple(LiveAnalysisItem(i, 250, f'[Item {i}]', i, f'slot_{i}', 'equipped', stats=(('Intellect', 42),)) for i in range(1, 18))
        view.show_equipment(items)
        view.show()
        self.app.processEvents()
        self.assertGreater(view.verticalScrollBar().maximum(), 0)
        cards = [frame for frame in view.widget().findChildren(QtWidgets.QFrame) if frame.objectName() == 'card']
        self.assertEqual(17, len(cards))
        self.assertGreaterEqual(cards[2].y(), cards[0].y() + cards[0].height())
        view.close()
