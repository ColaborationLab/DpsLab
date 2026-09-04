import unittest
from pathlib import Path
ROOT=Path(__file__).parents[2]
class TrainingDummyCaptureTests(unittest.TestCase):
 def test_synthetic_module_is_loaded_and_bounded(self):
  text=(ROOT/'addon/DpsLab/TrainingDummySession.lua').read_text(); toc=(ROOT/'addon/DpsLab/DpsLab.toc').read_text()
  self.assertIn('TrainingDummySession.lua',toc); self.assertIn('function Session.Start',text); self.assertIn('function Session.Finish',text); self.assertIn('synthetic_training_dummy',text); self.assertIn('integer(config.duration_seconds, 60, 900)',text)
 def test_no_real_api_or_automation_surface(self):
  text=(ROOT/'addon/DpsLab/TrainingDummySession.lua').read_text().lower()
  for token in ('registerevent','c_timer','onupdate','combat_log','sendchatmessage','unitname','unitguid','savedvariables','http','socket'):
   self.assertNotIn(token,text)
