import unittest
from pathlib import Path

class LiveAnalysisExportAddonTests(unittest.TestCase):
 def test_manual_export_has_no_chat_network_or_savedvariable_surface(self):
  root=Path(__file__).parents[2]; lua=(root/'addon/DpsLab/DpsLab.lua').read_text(); module=(root/'addon/DpsLab/CharacterEquipmentObservation.lua').read_text(); toc=(root/'addon/DpsLab/DpsLab.toc').read_text()
  self.assertIn('CharacterEquipmentObservation.lua',toc); self.assertIn('showManualAnalysisExport(payload)',lua); self.assertIn('DPSLAB-LIVE-ANALYSIS-0.1',module)
  self.assertNotIn('SendChatMessage',lua+module); self.assertNotIn('DpsLabObservationExport = payload',lua+module); self.assertNotIn('http',lua+module)
