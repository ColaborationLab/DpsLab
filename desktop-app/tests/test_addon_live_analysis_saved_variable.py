from __future__ import annotations

import unittest

from dpslab.addon_live_analysis_saved_variable import LiveAnalysisSavedVariableError, parse_live_analysis_saved_variable
from dpslab.addon_live_analysis_transport import canonical_live_analysis_bytes


def transport() -> bytes:
    value = {
        "analysis_context": {"talent_loadouts": {"active": {"config_id": 1, "talent_string": "AA"}, "comparison": {"config_id": 2, "talent_string": "BB"}}},
        "compatibility": {"build": 1, "interface_version": 1, "wow_product": "retail"},
        "equipment": {"equipped": [{"item_id": 1, "item_level": 1, "item_link": "item:1", "location": 1, "slot": "slot_1", "source": "equipped"}]},
        "observation_type": "live_manual_analysis_export",
        "safety": {"contains_direct_identifiers": False, "executable": False, "no_automation": True},
        "schema_version": "0.4",
        "subject": {"class_id": 11, "level": 80, "race_id": 4, "role": "damage", "specialization_id": 102},
    }
    payload = b"DPSLAB-LIVE-ANALYSIS-0.1\n" + canonical_live_analysis_bytes(value)
    return b'DpsLabObservationExport = "live_analysis:' + payload.hex().encode() + b'"\n'


class SavedVariableTests(unittest.TestCase):
    def test_valid_export_is_decoded(self) -> None:
        self.assertEqual(parse_live_analysis_saved_variable(transport()).specialization_id, 102)

    def test_unexpected_assignment_is_rejected(self) -> None:
        with self.assertRaises(LiveAnalysisSavedVariableError):
            parse_live_analysis_saved_variable(b'DpsLabObservationExport = "other"\n')
