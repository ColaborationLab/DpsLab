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
LOCALIZATION = (ROOT / "addon/DpsLab/Localization.lua").read_text(encoding="utf-8")
TOC = (ROOT / "addon/DpsLab/DpsLab.toc").read_text(encoding="utf-8")
DEFAULTS = (ROOT / "addon/DpsLab/DefaultItemScoreProfiles.lua").read_text(encoding="utf-8")
THEME = (ROOT / "addon/DpsLab/LinkTheme.lua").read_text(encoding="utf-8")


class AddonItemScoreProfilesTests(unittest.TestCase):
    def test_link_reuses_core_brand_and_avoids_blizzard_button_art(self):
        import struct
        texture = (ROOT / "addon/DpsLab/Media/foundry-brand-core.tga").read_bytes()
        self.assertEqual((4096, 1024, 32, 0x28), struct.unpack_from("<HHBB", texture, 12))
        self.assertEqual(18 + 4096 * 1024 * 4, len(texture))
        self.assertIn('Media\\\\foundry-brand-core.tga', THEME)
        self.assertNotIn('CreateLine', THEME)
        self.assertNotIn('BasicFrameTemplateWithInset', LUA)
        self.assertNotIn('UIPanelButtonTemplate', LUA)

    def test_weight_management_text_has_all_supported_catalogs(self):
        for text in (
            'en = {', 'es = {', 'pt = {', 'import_prompt =', 'positive_weights =',
            'automatic_profile =', 'weights_button_help =', 'delete_profile_help =',
        ):
            self.assertIn(text, LOCALIZATION)

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
        self.assertIn('button1 = T("use_new", "Usar nuevos")', LUA)
        self.assertIn('button2 = T("keep_current", "Conservar actuales")', LUA)
        self.assertIn('button3 = T("save_current_new", "Guardar actuales + usar nuevos")', LUA)
        self.assertIn('dialog:Hide()', LUA)
        self.assertIn('UIDropDownMenuTemplate', LUA)
        self.assertIn('function Scores.ExportString(profile)', LUA)
        self.assertIn('function Scores.ImportString(text)', LUA)
        self.assertIn('"N/D: efecto"', LUA)
        self.assertIn('frame.removeBuild = button(T("delete_build", "Eliminar build")', LUA)
        self.assertIn('frame.removeProfile = button(T("delete_profile", "Eliminar perfil")', LUA)
        self.assertIn('local function T(key, fallback)', LUA)
        self.assertIn('DpsLabLocalization.Get', LUA)

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
        self.assertIn('frame.copy:SetText(T("copy", "Copiar"))', LUA)
        self.assertIn("build sugerida para principiantes", LUA)
        self.assertIn('frame.saveProfile:SetText(T("save_profile", "Guardar perfil"))', LUA)
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
                return setmetatable({scripts={}, _text="", shown=false}, {__index=function(t,k)
                    if k=="CreateFontString" or k=="CreateTexture" or k=="CreateLine" or k=="CreateMaskTexture" then return widget end
                    if k=="IsEnabled" then return function() return true end end
                    if k=="SetSize" then return function(self,w,h) self.width=w; self.height=h end end
                    if k=="SetWidth" then return function(self,w) self.width=w end end
                    if k=="SetHeight" then return function(self,h) self.height=h end end
                    if k=="SetPoint" then return function(self,...) self.point={...} end end
                    if k=="HookScript" then return function(self,event,f)
                        local previous=self.scripts[event]
                        self.scripts[event]=function(...) if previous then previous(...) end; f(...) end
                    end end
                    if k=="SetText" then return function(self,v) self._text=v end end
                    if k=="GetText" then return function(self) return self._text end end
                    if k=="SetScript" then return function(self,event,f) self.scripts[event]=f end end
                    if k=="Show" then return function(self) self.shown=true end end
                    if k=="IsShown" then return function(self) return self.shown end end
                    if k=="Hide" then return function(self) self.shown=false end end
                    if not k:match("^[A-Z]") or k=="Bg" or k=="Inset" or k=="NineSlice" or k=="CloseButton"
                        or k=="TitleBg" or k=="TopTileStreaks" or k=="Left" or k=="Middle" or k=="Right" then return nil end
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
        self.lua.execute(THEME)
        self.lua.execute(LUA)

    def test_minimap_actions_reuse_existing_functions_and_stop_drag_updates(self):
        self.lua.execute('''
            GameTooltip=widget(); UISpecialFrames={}
            Minimap=widget()
            function Minimap:GetFrameLevel() return 1 end
            function Minimap:GetWidth() return 160 end
            function Minimap:GetHeight() return 160 end
            function Minimap:GetCenter() return 100,100 end
            function Minimap:GetEffectiveScale() return 1 end
            function UIParent:GetEffectiveScale() return 1 end
            function GetCursorPosition() return 180,100 end
            DpsLabLocalization={Get=function(key) return key end}
            opened=0; weightsOpened=0; exportsOpened=0; exportCommand=nil
            DpsLabItemScores.ShowConfig=function() opened=opened+1 end
            DpsLabItemScores.ShowWeights=function() weightsOpened=weightsOpened+1 end
            DpsLab={ShowManualAnalysisExport=function() exportsOpened=exportsOpened+1 end}
            SlashCmdList={DPSLAB=function(command) exportCommand=command end}
            local original=CreateFrame
            function CreateFrame(...)
                local frame=original(...); lastCreated=frame
                function frame:GetEffectiveScale() return 1 end
                function frame:GetLeft() return 800 end
                function frame:GetBottom() return 600 end
                return frame
            end
        ''')
        self.lua.execute((ROOT / "addon/DpsLab/Minimap.lua").read_text(encoding="utf-8"))
        self.lua.execute('''
            local loader=lastCreated
            loader.scripts.OnEvent(loader,"ADDON_LOADED","OtherAddon")
            assert(DpsFoundryMinimapButton==nil)
            loader.scripts.OnEvent(loader,"ADDON_LOADED","DpsLab")
            local button=DpsFoundryMinimapButton; local menu=DpsFoundryMinimapMenu
            button.scripts.OnClick(button,"LeftButton"); assert(opened==1)
            button.scripts.OnClick(button,"MiddleButton"); assert(weightsOpened==1)
            button.scripts.OnClick(button,"RightButton"); assert(menu.shown)
            assert(menu.width==216 and menu.height==146)
            assert(menu.point[2]==UIParent)
            button.scripts.OnHide(); assert(menu.shown)
            button.scripts.OnLeave(); assert(menu.shown)
            menu.controls[3].scripts.OnClick(); assert(exportCommand=="export app" and not menu.shown)
            menu.controls[4].scripts.OnClick(); assert(exportsOpened==1)
            menu.controls[5].scripts.OnClick(); assert(DpsLabItemScorePreferences.enabled==false)
            menu.controls[5].scripts.OnClick(); assert(DpsLabItemScorePreferences.enabled==true)
            button.scripts.OnDragStart(); assert(button.scripts.OnUpdate)
            button.scripts.OnUpdate(); assert(DpsLabItemScorePreferences.minimap_angle==0)
            button.scripts.OnDragStop(); assert(button.scripts.OnUpdate==nil)
            button.scripts.OnDragStart(); button.scripts.OnHide(); assert(button.scripts.OnUpdate==nil)
            assert(#UISpecialFrames==1)
        ''')

    def test_foundry_windows_keep_actions_and_bounded_build_list(self):
        self.assertLess(TOC.index("LinkTheme.lua"), TOC.index("DpsLab.lua"))
        self.lua.execute('''
            DpsLabItemScores.ShowWeights()
            local f=DpsLabWeightsFrame
            assert(f._foundryStyled and f.save._foundryButton and f.name._foundryField)
            assert(f.fields.Strength.weightBar.width==240)
            assert(f.name.point[2]+f.name.width < f.save.point[2])
            GameTooltip=widget()
            f.save.scripts.OnEnter(f.save); f.save.scripts.OnLeave(f.save)
            f.CloseButton.scripts.OnClick(); assert(not f.shown)
            local document=DpsLabItemScores.Active()
            local profiles=document.item_scores.profiles
            for i=2,20 do local p=CopyTable(profiles[1]); p.id="default:6:250:"..i; profiles[i]=p end
            DpsLabItemScores.Active=function() return document end
            DpsLabItemScores.ShowConfig()
            local config=DpsLabItemScoreConfigFrame
            assert(config.height==684 and config.buildScroll.height==224)
            assert(config.buildList.height==560 and #config.choices==20)
            config.weightsButton.scripts.OnClick(); assert(f.shown and not config.shown)
            f.fields.Strength:SetText("9.25")
            f.back.scripts.OnClick(); assert(config.shown and not f.shown)
            config.weightsButton.scripts.OnClick()
            assert(f.shown and not config.shown and f.fields.Strength:GetText()=="9.25")
            f.back.scripts.OnClick()
            document.item_scores.profiles[1].weights.Strength=4
            config.weightsButton.scripts.OnClick()
            assert(f.fields.Strength:GetText()=="4")
            assert(f.foundryBrand:GetText():find("DPSFOUNDRY"))
        ''')

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
