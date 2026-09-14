from pathlib import Path
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build/lua-test-runtime"))
try:
    from lupa.lua51 import LuaRuntime
except ImportError:
    LuaRuntime = None


ROOT = Path(__file__).resolve().parents[2]
LUA = (ROOT / "addon/DpsLab/ItemScoreProfiles.lua").read_text(encoding="utf-8")
TOC = (ROOT / "addon/DpsLab/DpsLab.toc").read_text(encoding="utf-8")
DEFAULTS = (ROOT / "addon/DpsLab/DefaultItemScoreProfiles.lua").read_text(encoding="utf-8")


class AddonItemScoreProfilesTests(unittest.TestCase):
    def test_tooltip_hook_displays_each_selected_profile_score(self):
        self.assertIn('pcall(GameTooltip.HookScript, GameTooltip, "OnTooltipSetItem", addTooltipScores)', LUA)
        self.assertIn("Scores.ScoreItem(link, profile)", LUA)
        self.assertIn("tooltip:AddDoubleLine", LUA)
        self.assertIn('tooltip:AddLine("DpsLab Scores")', LUA)
        self.assertIn('GetSpecializationInfoByID(specID)', LUA)
        self.assertIn("local function displayName(profile)", LUA)
        self.assertIn("document.item_scores.profiles", LUA)
        self.assertIn("function Scores.Active()", LUA)
        self.assertIn("matchesPlayer(document)", LUA)
        self.assertIn("function defaultDocument()", LUA)
        self.assertIn("return chosenDocument(defaultDocument())", LUA)
        self.assertIn("TooltipDataProcessor.AddTooltipPostCall", LUA)
        self.assertIn("Enum.TooltipDataType.Item", LUA)
        self.assertIn("ShoppingTooltip1, ShoppingTooltip2", LUA)
        self.assertIn('hooksecurefunc(tooltip, "ProcessInfo"', LUA)
        self.assertIn("TooltipUtil.GetDisplayedItem(tooltip)", LUA)
        self.assertNotIn("DpsLabAwaitScore", LUA)
        self.assertNotIn("local function tooltipLink", LUA)
        self.assertIn('StaticPopupDialogs["DPSLAB_IMPORT_SCORES"]', LUA)
        self.assertIn('button1 = "Usar nuevos", button2 = "Conservar actuales", button3 = "Guardar actuales + usar nuevos"', LUA)
        self.assertIn('dialog:Hide()', LUA)
        self.assertIn('UIDropDownMenuTemplate', LUA)
        self.assertIn('function Scores.ExportString(profile)', LUA)
        self.assertIn('function Scores.ImportString(text)', LUA)
        self.assertIn('"N/D: efecto"', LUA)
        self.assertIn('frame.removeBuild = button("Eliminar build"', LUA)
        self.assertIn('frame.removeProfile = button("Eliminar perfil"', LUA)

    def test_visible_menu_persists_profile_selection_without_automation(self):
        self.assertIn("function Scores.ShowConfig()", LUA)
        self.assertIn("DpsLabItemScorePreferences.selected[document.character_id]", LUA)
        self.assertIn("DpsLabItemScorePreferences.enabled == false", LUA)
        self.assertNotIn("if index > 8 then break end", LUA)
        self.assertLess(TOC.index("DefaultItemScoreProfiles.lua"), TOC.index("ItemScoreProfiles.lua"))
        self.assertIn('id = "default:11:102:', DEFAULTS)
        self.assertGreaterEqual(DEFAULTS.count("specialization_id"), 31)
        self.assertIn("talent_string", DEFAULTS)
        self.assertIn("report_sha256", DEFAULTS)
        self.assertIn('frame.copy:SetText("Copiar")', LUA)
        self.assertIn("build sugerida para principiantes", LUA)
        self.assertIn('frame.saveProfile:SetText("Guardar perfil")', LUA)
        self.assertIn("Perfiles de pesos guardados", LUA)
        self.assertIn("(b) identifica una build sugerida para principiantes", LUA)
        self.assertIn("ItemScoreProfiles.lua", TOC)
        forbidden = ("C_Timer", "CastSpell", "RunMacro", "SendChatMessage", "http", "socket")
        self.assertTrue(all(token not in LUA for token in forbidden))


@unittest.skipIf(LuaRuntime is None, "Optional Lua 5.1 runtime not installed")
class AddonScoreRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute('''
            function CopyTable(t) local c = {}; for k,v in pairs(t) do c[k] = type(v)=="table" and CopyTable(v) or v end; return c end
            function UnitClass() return "Death Knight", "DEATHKNIGHT", 6 end
            function UnitFullName() return "Test", "Realm" end
            function GetSpecialization() return 1 end
            function GetSpecializationInfo() return 250 end
            function GetSpecializationInfoByID() return 250, "Blood", "", 135770 end
            C_Item = { GetItemStats = function(link) if link=="item:no-stats" then return {} end; return { ITEM_MOD_STRENGTH_SHORT = link=="item:equipped" and 70 or 50 } end }
            TooltipUtil = { GetDisplayedItem = function(t) return "item", t.link end }
            Enum = { TooltipDataType = { Item=1 } }
            TooltipDataProcessor = { AddTooltipPostCall = function(_, f) postCall=f end }
            function hooksecurefunc(t, method, callback)
                local original=t[method]; t[method]=function(...) original(...); callback(...) end
            end
            function tooltip(name, legacy)
                local t={lines={}, name=name, link="item:equipped"}
                function t:GetName() return self.name end
                function t:NumLines() return #self.lines end
                function t:AddLine(text)
                    self.lines[#self.lines+1]=text
                    _G[self.name.."TextLeft"..#self.lines]={GetText=function() return text end}
                end
                function t:AddDoubleLine(left,right) self:AddLine(left); self.score=right end
                function t:Show() end
                function t:HookScript() end
                function t:ProcessInfo() self.lines={}; postCall(self, {}) end
                if legacy then function t:GetItem() return "item", self.link end end
                return t
            end
            GameTooltip=tooltip("GameTooltip",true)
            ShoppingTooltip1=tooltip("ShoppingTooltip1",false)
            ShoppingTooltip2=tooltip("ShoppingTooltip2",false)
            ItemRefShoppingTooltip1=tooltip("ItemRefShoppingTooltip1",false)
            ItemRefShoppingTooltip2=tooltip("ItemRefShoppingTooltip2",false)
            DpsLabDefaultItemScoreProfiles={schema_version="0.1",profiles={{id="default:6:250:1",name="deathknight — blood sugerida",source="generic",class_id=6,specialization_id=250,weights={Strength=2}}}}
            StaticPopupDialogs={}; popupCount=0
            function StaticPopup_Show(_, _, _, data)
                popupCount=popupCount+1; popupData=data
                popupDialog=widget(); popupDialog.data=data; popupDialog.button1=widget(); popupDialog.button2=widget(); popupDialog.button3=widget()
                StaticPopupDialogs.DPSLAB_IMPORT_SCORES.OnShow(popupDialog)
                return popupDialog
            end
            function widget()
                return setmetatable({scripts={}, text="", shown=false}, {__index=function(t,k)
                    if k=="CreateFontString" then return widget end
                    if k=="SetText" then return function(self,v) self.text=v end end
                    if k=="GetText" then return function(self) return self.text end end
                    if k=="SetScript" then return function(self,event,f) self.scripts[event]=f end end
                    if k=="Show" then return function(self) self.shown=true end end
                    return function() end
                end})
            end
            function CreateFrame(_, name) local f=widget(); f.TitleText=widget(); if name then _G[name]=f end; return f end
            function UIDropDownMenu_SetWidth() end
            function UIDropDownMenu_CreateInfo() return {} end
            function UIDropDownMenu_AddButton() end
            function UIDropDownMenu_SetSelectedID(control,index) control.selected=index end
            function UIDropDownMenu_SetText(control,text) control.text=text end
            function UIDropDownMenu_Initialize(control,callback) control.initialize=callback; callback() end
            UIParent={}
        ''')
        self.lua.execute(LUA)

    def test_comparison_without_getitem_renders_once_and_survives_rebuild(self):
        self.lua.execute('''
            for _,t in ipairs({GameTooltip,ShoppingTooltip1,ShoppingTooltip2,ItemRefShoppingTooltip1,ItemRefShoppingTooltip2}) do
                t:ProcessInfo()
                assert(#t.lines==2 and t.score=="140.0")
                assert(t.lines[1]=="DpsLab Scores")
                assert(t.lines[2]=="|T135770:14:14:0:0|t Blood (b)")
                t:ProcessInfo(); assert(#t.lines==2)
            end
        ''')

    def test_weights_window_saves_edits_and_restores_active_snapshot(self):
        self.lua.execute('''
            DpsLabItemScores.ShowWeights()
            local f=DpsLabWeightsFrame
            assert(f.shown and f.fields.Strength:GetText()=="2")
            f.fields.Strength:SetText("3"); f.name:SetText("Mi perfil")
            f.save.scripts.OnClick()
            assert(DpsLabItemScores.Active().item_scores.profiles[1].weights.Strength==3)
            assert(DpsLabDefaultItemScoreProfiles.profiles[1].weights.Strength==2)
            f.fields.Strength:SetText("-1"); f.save.scripts.OnClick()
            assert(#DpsLabItemScorePreferences.saved_profiles["default:6:250"]==1)
        ''')
        # Reload addon code while preserving SavedVariables, as /reload does.
        self.lua.execute(LUA)
        self.lua.execute('assert(DpsLabItemScores.Active().item_scores.profiles[1].weights.Strength==3)')

    def test_same_loadout_new_weights_prompt_and_cancel_is_respected(self):
        self.lua.execute('''
            local id=string.rep("a",32)
            DpsLabRealRecommendation={schema_version="0.5",state="ready",character_id=id,character={name="Test",realm="Realm",class_id=6},item_scores={profiles={{id="250:1",name="Blood",source="personalized",weights={Strength=4}}}}}
            DpsLabItemScores.Refresh(); assert(popupCount==1)
            StaticPopupDialogs.DPSLAB_IMPORT_SCORES.OnAccept(popupDialog,popupData)
            DpsLabRealRecommendation.item_scores.profiles[1].weights.Strength=5
            DpsLabItemScores.Refresh(); assert(popupCount==2)
            StaticPopupDialogs.DPSLAB_IMPORT_SCORES.OnCancel(popupDialog,popupData)
            DpsLabItemScores.Refresh(); assert(popupCount==2)
            assert(DpsLabItemScores.Active().item_scores.profiles[1].weights.Strength==4)
            DpsLabRealRecommendation.item_scores.profiles[1].weights.Strength=6
            DpsLabItemScores.Refresh(); assert(popupCount==3)
            StaticPopupDialogs.DPSLAB_IMPORT_SCORES.OnAlt(popupDialog,popupData)
            assert(DpsLabItemScorePreferences.saved_profiles[id][1].document.item_scores.profiles[1].weights.Strength==4)
            assert(DpsLabItemScores.Active().item_scores.profiles[1].weights.Strength==6)
        ''')

    def test_manual_weight_string_round_trip(self):
        self.lua.execute('''
            local profile=DpsLabItemScores.Active().item_scores.profiles[1]
            local encoded=DpsLabItemScores.ExportString(profile)
            assert(encoded:match("^DPSLAB%-WEIGHTS%-0%.1|250|"))
            local decoded=DpsLabItemScores.ImportString(encoded)
            assert(decoded and decoded.weights.Strength==2 and decoded.name=="Blood")
            assert(DpsLabItemScores.ImportString(encoded:gsub("|250|", "|251|"))==nil)
        ''')

    def test_unscorable_effect_has_no_false_zero_and_saved_profile_can_be_deleted(self):
        self.lua.execute('''
            local profile=DpsLabItemScores.Active().item_scores.profiles[1]
            assert(DpsLabItemScores.ScoreItem("item:no-stats", profile)==nil)
            DpsLabItemScores.ShowWeights()
            local f=DpsLabWeightsFrame
            f.name:SetText("Temporal"); f.save.scripts.OnClick()
            DpsLabItemScores.ShowWeights(); f=DpsLabWeightsFrame
            f.removeProfile.scripts.OnClick()
            assert(#DpsLabItemScorePreferences.saved_profiles["default:6:250"]==0)
        ''')
