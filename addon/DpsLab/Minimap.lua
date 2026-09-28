-- Entry points only: reuse Link's existing actions and its own preferences.
local function T(key)
  return DpsLabLocalization.Get(key) or key
end

local function initialize()
  if _G.DpsFoundryMinimapButton then return end
  DpsLabItemScorePreferences = DpsLabItemScorePreferences or {}
  local preferences = DpsLabItemScorePreferences
  local button = CreateFrame("Button", "DpsFoundryMinimapButton", Minimap, "BackdropTemplate")
  button:SetSize(34,34); button:SetFrameStrata("MEDIUM"); button:SetFrameLevel(Minimap:GetFrameLevel()+8)
  local function round(texture)
    local mask = button:CreateMaskTexture()
    mask:SetTexture("Interface\\CHARACTERFRAME\\TempPortraitAlphaMask")
    mask:SetAllPoints(texture); texture:AddMaskTexture(mask)
  end
  local rim = button:CreateTexture(nil,"BACKGROUND",nil,0)
  rim:SetAllPoints(button); rim:SetColorTexture(0.67,0.45,0.15,1); round(rim)
  local inner = button:CreateTexture(nil,"BACKGROUND",nil,1)
  inner:SetPoint("TOPLEFT",1,-1); inner:SetPoint("BOTTOMRIGHT",-1,1)
  inner:SetColorTexture(0.025,0.04,0.05,1); round(inner)
  local icon = button:CreateTexture(nil, "ARTWORK")
  icon:SetTexture("Interface\\AddOns\\DpsLab\\Media\\foundry-brand-core.tga")
  icon:SetTexCoord(90/4096,602/4096,75/1024,587/1024)
  icon:SetPoint("TOPLEFT",3,-3); icon:SetPoint("BOTTOMRIGHT",-3,3); round(icon)
  button:HookScript("OnEnter",function() rim:SetColorTexture(1,0.65,0.2,1) end)
  button:HookScript("OnLeave",function() rim:SetColorTexture(0.67,0.45,0.15,1) end)
  local function position(angle)
    if type(angle) ~= "number" or angle ~= angle or math.abs(angle)==math.huge then angle=225 end
    preferences.minimap_angle = angle % 360
    local radians = math.rad(preferences.minimap_angle)
    button:ClearAllPoints()
    button:SetPoint("CENTER",Minimap,"CENTER",math.cos(radians)*(Minimap:GetWidth()/2+8),math.sin(radians)*(Minimap:GetHeight()/2+8))
  end
  position(preferences.minimap_angle)
  local menu = CreateFrame("Frame", "DpsFoundryMinimapMenu", UIParent, "BackdropTemplate")
  menu:SetSize(216,146); menu:SetFrameStrata("DIALOG"); menu:SetClampedToScreen(true); menu:EnableMouse(true)
  menu:SetBackdrop({bgFile="Interface\\Buttons\\WHITE8X8",edgeFile="Interface\\Buttons\\WHITE8X8",edgeSize=1})
  menu:SetBackdropColor(0.031,0.055,0.071,0.98); menu:SetBackdropBorderColor(0.65,0.36,0.12,1)
  if UISpecialFrames then table.insert(UISpecialFrames,"DpsFoundryMinimapMenu") end
  local actions = {
    {"link_open",function() DpsLabItemScores.ShowConfig() end},
    {"view_edit",function() DpsLabItemScores.ShowWeights() end},
    {"link_export_core",function() SlashCmdList.DPSLAB("export app") end},
    {"copy_export",function() DpsLab.ShowManualAnalysisExport() end},
    {"show_item_scores",function() preferences.enabled = preferences.enabled == false end},
  }
  menu.controls = {}
  for index, action in ipairs(actions) do
    local control = CreateFrame("Button",nil,menu,"BackdropTemplate")
    control:SetSize(204,24); control:SetPoint("TOPLEFT",6,-6-(index-1)*28)
    DpsLabLinkTheme.Button(control,index==1)
    control:SetScript("OnClick",function() menu:Hide(); action[2]() end)
    menu.controls[index]=control
  end
  menu:Hide()
  button:RegisterForClicks("LeftButtonUp","RightButtonUp","MiddleButtonUp")
  button:SetScript("OnClick",function(_,mouse)
    if mouse=="RightButton" then
      if menu:IsShown() then menu:Hide(); return end
      for index,action in ipairs(actions) do menu.controls[index]:SetText(T(action[1])) end
      menu.controls[5]:SetText(T(preferences.enabled==false and "show_item_scores" or "link_hide_scores"))
      -- Anchor to UIParent coordinates: a minimap collector can hide/reparent the button.
      local left,bottom=button:GetLeft(),button:GetBottom()
      local ratio=button:GetEffectiveScale()/UIParent:GetEffectiveScale()
      menu:ClearAllPoints(); menu:SetPoint("TOPRIGHT",UIParent,"BOTTOMLEFT",left*ratio,bottom*ratio-2)
      GameTooltip:Hide(); menu:Show()
    else
      menu:Hide()
      if mouse=="MiddleButton" then DpsLabItemScores.ShowWeights() else DpsLabItemScores.ShowConfig() end
    end
  end)
  button:RegisterForDrag("LeftButton")
  button:SetScript("OnDragStart",function()
    menu:Hide(); GameTooltip:Hide()
    button:SetScript("OnUpdate",function()
      local x,y=GetCursorPosition(); local cx,cy=Minimap:GetCenter(); local scale=Minimap:GetEffectiveScale()
      if cx and cy then position(math.deg(math.atan2(y/scale-cy,x/scale-cx))) end
    end)
  end)
  button:SetScript("OnDragStop",function() button:SetScript("OnUpdate",nil) end)
  button:HookScript("OnHide",function() button:SetScript("OnUpdate",nil); GameTooltip:Hide() end)
  button:HookScript("OnEnter",function()
    GameTooltip:SetOwner(button,"ANCHOR_LEFT"); GameTooltip:SetText("DpsFoundry Link")
    GameTooltip:AddLine(T("link_minimap_help"),0.78,0.81,0.84,true); GameTooltip:Show()
  end)
  button:HookScript("OnLeave",function() GameTooltip:Hide() end)
end

local loader = CreateFrame("Frame")
loader:RegisterEvent("ADDON_LOADED")
loader:SetScript("OnEvent",function(self,_,name)
  if name~="DpsLab" then return end
  self:UnregisterEvent("ADDON_LOADED"); initialize()
end)
