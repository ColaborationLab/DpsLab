import unittest
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build/lua-test-runtime"))
try:
    from lupa.lua51 import LuaRuntime
except ImportError:
    LuaRuntime = None


class LiveAnalysisExportAddonTests(unittest.TestCase):
    @unittest.skipIf(LuaRuntime is None, "Lua runtime unavailable")
    def test_client_identity_export_is_canonical_and_keeps_actual_faction(self):
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute((Path(__file__).parents[2] / 'addon/DpsLab/CharacterEquipmentObservation.lua').read_text())
        exported, status = lua.eval('''function()
          return DpsLabCharacterEquipmentObservation.Capture(nil, {
            GetBuildInfo=function() return "12.1", "69933", "", 120100 end,
            UnitClass=function() return "Monk", "MONK", 10 end,
            UnitRace=function() return "Pandaren", "Pandaren", 26 end,
            UnitFactionGroup=function() return "Horde" end,
            GetSpecialization=function() return 1 end,
            GetSpecializationInfo=function() return 269, "", "", "", "DAMAGER" end,
            UnitLevel=function() return 90 end, GetMaxLevelForPlayerExpansion=function() return 90 end,
            UnitFullName=function() return "Test", "Realm" end, GetRealmName=function() return "Realm" end,
            GetInventoryItemLink=function(_,slot) if slot==1 then return "item:123" end end,
            GetDetailedItemLevelInfo=function() return 100 end, GetItemStats=function() return {} end,
            C_ClassTalents={GetActiveConfigID=function() return 1 end, GetConfigIDsBySpecID=function() return {1} end, IsConfigPopulated=function() return true end},
            C_Traits={GenerateImportString=function() return "ABCD" end},
          })
        end''')()
        self.assertEqual('analysis_export_ready', status)
        from dpslab.addon_live_analysis_transport import parse_live_analysis_export
        self.assertEqual(('Pandaren', 'Monk', 'Horde'), parse_live_analysis_export(exported).visual_identity)

    @unittest.skipIf(LuaRuntime is None, "Lua runtime unavailable")
    def test_copy_export_uses_scroll_child_preserves_payload_and_returns_to_link(self):
        root = Path(__file__).parents[2]
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute('''
          frames = {}; UIParent = {}; SlashCmdList = {}; returned = false
          function CreateFrame(kind, name, parent, template)
            local f = {kind=kind, scripts={}}
            setmetatable(f, {__index=function(_, key) return function(self, ...)
              if key == "SetScript" then local event, fn = ...; self.scripts[event]=fn
              elseif key == "SetScrollChild" then self.child = ...
              elseif key == "SetText" then self.text = ...
              elseif key == "Hide" then self.hidden = true
              elseif key == "CreateFontString" then return CreateFrame("FontString") end
            end end})
            frames[#frames+1] = f; if name then _G[name]=f end; return f
          end
          DpsLabItemScoreConfigFrame = CreateFrame("Frame")
          DpsLabItemScores = {ShowConfig=function() returned=true end}
          payload = string.rep("abc", 20000)
          DpsLabCharacterEquipmentObservation = {Capture=function() return payload, "analysis_export_ready" end}
        ''')
        source = (root / "addon/DpsLab/DpsLab.lua").read_text()
        start = source.index("local function showManualAnalysisExport(payload)")
        end = source.index("function DpsLab.ShowManualAnalysisExport()", start)
        lua.execute('local function T(_, fallback) return fallback end\n' + source[start:end] + '\nshowManualAnalysisExport(payload)')
        lua.execute('''
          assert(DpsLabItemScoreConfigFrame.hidden)
          local scroll, box, back
          for _, frame in ipairs(frames) do
            if frame.kind == "ScrollFrame" then scroll=frame end
            if frame.kind == "EditBox" then box=frame end
            if frame.kind == "Button" then back=frame end
          end
          assert(scroll.child == box and box.text == payload)
          back.scripts.OnClick(); assert(returned and DpsLabManualAnalysisExportFrame.hidden)
        ''')
        start = source.index("local function confirmAppExport(payload)")
        end = source.index("local function syntheticExportCandidate()", start)
        lua.execute('''
          returned=false; reloads=0
          function ReloadUI() reloads=reloads+1 end
          DpsLabLinkTheme={Frame=function(f) f.CloseButton=CreateFrame("Button") end, Button=function() end}
          DpsLabItemScoreConfigFrame.hidden=false
        ''')
        lua.execute('local function T(_, fallback) return fallback end\nlocal function lowerHex(value) return value end\n' + source[start:end] + '\nconfirmAppExport(payload)')
        lua.execute('''
          assert(DpsLabItemScoreConfigFrame.hidden and reloads==0)
          DpsLabAppExportFrame.cancel.scripts.OnClick()
          assert(returned and DpsLabAppExportFrame.hidden)
          returned=false; DpsLabAppExportFrame.CloseButton.scripts.OnClick(); assert(returned)
        ''')

    @unittest.skipIf(LuaRuntime is None, "Lua runtime unavailable")
    def test_icon_capture_is_optional_bounded_and_only_reads_existing_item(self):
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute((Path(__file__).parents[2] / "addon/DpsLab/CharacterEquipmentObservation.lua").read_text())
        capture_item = lua.eval('''function(icon)
          local item
          for i=1,40 do
            local name, value = debug.getupvalue(DpsLabCharacterEquipmentObservation.Capture, i)
            if name == "item" then item = value; break end
          end
          local a = {GetDetailedItemLevelInfo=function() return 100 end,
            C_Item={GetItemStats=function() return {} end}}
          if icon ~= nil then a.C_Item.GetItemIconByID=function(id)
            assert(id == "item:123"); return icon end end
          return item(a, "item:123", 1, true)
        end''')
        for supplied, expected in ((134400, 134400), (None, None), (True, None), (-1, None), (1.5, None), (2147483648, None)):
            result = json.loads(capture_item(supplied))
            self.assertEqual(expected, result["icon_file_data_id"])
            self.assertEqual(123, result["item_id"])
    def test_export_app_requires_confirmation_and_keeps_no_network_surface(self):
        root = Path(__file__).parents[2]
        lua = (root / "addon/DpsLab/DpsLab.lua").read_text()
        module = (root / "addon/DpsLab/CharacterEquipmentObservation.lua").read_text()
        toc = (root / "addon/DpsLab/DpsLab.toc").read_text()
        self.assertIn("CharacterEquipmentObservation.lua", toc)
        self.assertIn("showManualAnalysisExport(payload)", lua)
        self.assertIn("DPSLAB-LIVE-ANALYSIS-0.1", module)
        self.assertIn('role == "app"', lua)
        self.assertIn('"Exportar y /reload"', lua)
        self.assertIn('_G.DpsLabObservationExport = "live_analysis:" .. lowerHex(payload)', lua)
        self.assertIn("ReloadUI()", lua)
        for fragment in ("RegisterEvent", "C_Timer", "OnUpdate", "SendChatMessage", "http"):
            self.assertNotIn(fragment, lua + module)

    def test_multiclass_export_uses_client_role_real_equipment_and_up_to_four_loadouts(self):
        root = Path(__file__).parents[2]
        module = (root / "addon/DpsLab/CharacterEquipmentObservation.lua").read_text()
        for fragment in (
            "ROLE_MAP", "analysis_role_unsupported", "GetDetailedItemLevelInfo",
            "GetActiveConfigID", "GetConfigIDsBySpecID", "GenerateImportString",
            'for index = 1, #alternatives do', 'if #values < 1', 'GetConfigInfo', '"0.11"', 'GetItemStats', 'UnitFullName', 'realm_name', 'IsConfigPopulated', 'GetMaxLevelForPlayerExpansion', 'GetItemIconByID', 'icon_file_data_id', 'visual_identity', 'UnitFactionGroup',
        ):
            self.assertIn(fragment, module)
        self.assertNotIn("C_Container", module)

    def test_real_result_file_is_loaded_and_rendered_only_as_bounded_text(self):
        root = Path(__file__).parents[2]
        toc = (root / "addon/DpsLab/DpsLab.toc").read_text()
        lua = (root / "addon/DpsLab/DpsLab.lua").read_text()
        self.assertIn("DpsLabRealRecommendation.lua", toc)
        self.assertIn('command == "result"', lua)
        self.assertIn("realRecommendation", lua)
