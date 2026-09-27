-- Foundry presentation only. No saved data, timers, transport or gameplay calls.
local Theme = {}
local WHITE = "Interface\\Buttons\\WHITE8X8"

local function surface(frame, inset, edge)
  frame:SetBackdrop({bgFile=WHITE, edgeFile=WHITE, edgeSize=edge or 1,
    insets={left=inset or 1, right=inset or 1, top=inset or 1, bottom=inset or 1}})
  frame:SetBackdropColor(0.031, 0.055, 0.071, 0.97)
  frame:SetBackdropBorderColor(0.27, 0.31, 0.32, 1)
end

function Theme.Frame(frame)
  if frame._foundryStyled then return end
  frame._foundryStyled = true
  surface(frame, 5, 4)
  frame:SetBackdropBorderColor(0.39, 0.38, 0.31, 1)
  for _, name in ipairs({"Bg", "Inset", "TitleBg", "TopTileStreaks", "TitleText", "NineSlice"}) do
    if frame[name] then frame[name]:Hide() end
  end
  local header = frame:CreateTexture(nil, "BACKGROUND")
  header:SetPoint("TOPLEFT", 6, -6); header:SetPoint("TOPRIGHT", -6, -6); header:SetHeight(72)
  header:SetColorTexture(0.02, 0.035, 0.043, 1)
  local rule = frame:CreateTexture(nil, "ARTWORK")
  rule:SetPoint("TOPLEFT", 12, -78); rule:SetPoint("TOPRIGHT", -12, -78); rule:SetHeight(1)
  rule:SetColorTexture(0.73, 0.36, 0.08, 0.8)
  local emblem = frame:CreateTexture(nil, "ARTWORK")
  emblem:SetTexture("Interface\\AddOns\\DpsLab\\Media\\foundry-brand-core.tga")
  emblem:SetTexCoord(90/4096, 602/4096, 75/1024, 587/1024)
  emblem:SetPoint("TOPLEFT", 12, -8); emblem:SetSize(68,68)
  frame.foundryBrand = frame:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
  frame.foundryBrand:SetPoint("TOPLEFT", 82, -25)
  frame.foundryBrand:SetText("|cffedf1f4DPSFOUNDRY|r |cffff8a00/ LINK|r")
  frame.foundryDescriptor = frame:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
  frame.foundryDescriptor:SetPoint("TOPLEFT", 83, -48)
  frame.foundryDescriptor:SetText("CHARACTER  /  GEAR INTELLIGENCE  /  SYNC")
  frame.foundryDescriptor:SetTextColor(0.64, 0.69, 0.71)
  frame:SetMovable(true); frame:EnableMouse(true); frame:RegisterForDrag("LeftButton")
  frame:SetScript("OnDragStart", frame.StartMoving); frame:SetScript("OnDragStop", frame.StopMovingOrSizing)
  local close = frame.CloseButton or CreateFrame("Button", nil, frame, "BackdropTemplate")
  close:ClearAllPoints(); close:SetPoint("TOPRIGHT", -12, -12); close:SetSize(24,24)
  if not frame.CloseButton then Theme.Button(close); frame.CloseButton = close end
  close:SetText("×"); close:SetScript("OnClick", function() frame:Hide() end)
end

function Theme.Button(button, primary)
  if button._foundryButton then return end
  button._foundryButton = true
  local label = button:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
  label:SetPoint("LEFT", button, "LEFT", 8, 0); label:SetPoint("RIGHT", button, "RIGHT", -8, 0)
  label:SetJustifyH("CENTER"); label:SetWordWrap(false)
  button:SetFontString(label)
  button:SetNormalTexture(""); button:SetPushedTexture(""); button:SetHighlightTexture(""); button:SetDisabledTexture("")
  surface(button)
  button:SetNormalFontObject("GameFontHighlightSmall"); button:SetDisabledFontObject("GameFontDisableSmall")
  local function paint(hover, pressed)
    local enabled = button:IsEnabled()
    button:SetBackdropColor(pressed and 0.04 or (hover and 0.16 or 0.09), hover and 0.12 or 0.12, 0.13, 1)
    if enabled and (hover or primary) then button:SetBackdropBorderColor(0.65, 0.36, 0.12, 1)
    else button:SetBackdropBorderColor(0.27, 0.31, 0.32, enabled and 1 or 0.35) end
  end
  button:HookScript("OnEnter", function() paint(true) end)
  button:HookScript("OnLeave", function() paint(false) end)
  button:HookScript("OnMouseDown", function() paint(true,true) end)
  button:HookScript("OnMouseUp", function() paint(false) end)
  button:HookScript("OnEnable", function() paint(false) end)
  button:HookScript("OnDisable", function() paint(false) end)
  paint(false)
end

function Theme.Field(field)
  if field._foundryField then return end
  field._foundryField = true
  for _, name in ipairs({"Left", "Middle", "Right"}) do if field[name] then field[name]:Hide() end end
  surface(field); field:SetTextInsets(8,8,0,0)
  field:HookScript("OnEditFocusGained", function() field:SetBackdropBorderColor(0.85,0.46,0.1,1) end)
  field:HookScript("OnEditFocusLost", function() field:SetBackdropBorderColor(0.27,0.31,0.32,1) end)
  field:HookScript("OnEscapePressed", function() field:ClearFocus() end)
end

function Theme.Choice(choice)
  if not choice._foundryRefresh then
    local fill = choice:CreateTexture(nil, "BACKGROUND")
    fill:SetPoint("TOPLEFT", 0, 0); fill:SetSize(490, 27)
    local mark = choice:CreateTexture(nil, "ARTWORK")
    mark:SetPoint("TOPLEFT", 0, 0); mark:SetSize(2, 27)
    mark:SetColorTexture(1, 0.54, 0.08, 0.9)
    choice._foundryRefresh = function(hover)
      local selected = choice:GetChecked()
      fill:SetColorTexture(selected and 0.20 or 0.09, 0.13, 0.13, hover and 0.95 or 0.65)
      mark:SetShown(selected and true or false)
    end
    choice:HookScript("OnEnter", function() choice._foundryRefresh(true) end)
    choice:HookScript("OnLeave", function() choice._foundryRefresh(false) end)
    choice:HookScript("OnClick", function() choice._foundryRefresh(false) end)
  end
  choice._foundryRefresh(false)
end

DpsLabLinkTheme = Theme
