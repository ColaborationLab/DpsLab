import unittest
from pathlib import Path
ROOT=Path(__file__).parents[2]
class AdvisorSyntheticGuidanceTests(unittest.TestCase):
 def test_loaded_and_role_safety_is_explicit(self):
  text=(ROOT/'addon/DpsLab/AdvisorSyntheticGuidance.lua').read_text();toc=(ROOT/'addon/DpsLab/DpsLab.toc').read_text()
  self.assertIn('AdvisorSyntheticGuidance.lua',toc);self.assertIn('safety_first ~= "survival"',text);self.assertIn('safety_first ~= "healing"',text)
 def test_no_live_or_automation_surface(self):
  text=(ROOT/'addon/DpsLab/AdvisorSyntheticGuidance.lua').read_text().lower()
  for token in ('registerevent','c_timer','onupdate','castspell','useaction','sendchatmessage','unitguid','getcontainer','http','socket','savedvariables'):
   self.assertNotIn(token,text)
