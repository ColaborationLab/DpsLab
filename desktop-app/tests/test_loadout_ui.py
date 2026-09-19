from __future__ import annotations

import unittest

from dpslab.loadout_ui import _simulation_selection


class LoadoutWorkspaceSelectionTests(unittest.TestCase):
    def test_live_selected_loadouts_do_not_require_a_saved_profile(self):
        selected, imported = _simulation_selection((101, 102), {}, None, 250)
        self.assertEqual((101, 102), selected)
        self.assertEqual((), imported)

    def test_unavailable_live_loadout_is_excluded_without_losing_the_rest(self):
        selected, imported = _simulation_selection((101, 102), {102: "talents_unassigned"}, None, 250)
        self.assertEqual((101,), selected)
        self.assertEqual((), imported)


if __name__ == "__main__":
    unittest.main()
