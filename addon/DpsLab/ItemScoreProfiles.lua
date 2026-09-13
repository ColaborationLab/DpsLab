-- Local score display. It never runs SimulationCraft or selects gameplay actions.
local Scores = {}
local ALLOWED = { Intellect=true, Agility=true, CritRating=true, HasteRating=true, MasteryRating=true, VersatilityRating=true }

local function validWeights(value)
  if type(value) ~= "table" or type(value.name) ~= "string" or type(value.source) ~= "string"
    or (value.source ~= "personalized" and value.source ~= "generic") or type(value.weights) ~= "table" then return false end
  for stat, weight in pairs(value.weights) do
    if ALLOWED[stat] ~= true or type(weight) ~= "number" or weight <= 0 or weight ~= weight or weight == math.huge then return false end
  end
  return next(value.weights) ~= nil
end

local function imported()
  local document = DpsLabRealRecommendation
  return type(document) == "table" and document.schema_version == "0.4" and type(document.item_scores) == "table" and document.item_scores or nil
end

function Scores.Refresh()
  local document = imported()
  if document == nil or type(document.character_id) ~= "string" or #document.character_id ~= 32 then return end
  DpsLabItemScoreProfiles = type(DpsLabItemScoreProfiles) == "table" and DpsLabItemScoreProfiles or {}
  DpsLabItemScoreProfiles[document.character_id] = document
end

function Scores.Visible()
  DpsLabItemScorePreferences = type(DpsLabItemScorePreferences) == "table" and DpsLabItemScorePreferences or { enabled=true, selected={} }
  if type(DpsLabItemScorePreferences.selected) ~= "table" then DpsLabItemScorePreferences.selected = {} end
  return DpsLabItemScorePreferences.enabled ~= false and DpsLabItemScorePreferences.selected or {}
end

function Scores.ScoreItem(link, selected)
  local getStats = type(C_Item) == "table" and C_Item.GetItemStats or GetItemStats
  if type(getStats) ~= "function" or type(link) ~= "string" or not validWeights(selected) then return nil end
  local ok, stats = pcall(getStats, link)
  if not ok or type(stats) ~= "table" then return nil end
  local names = { ITEM_MOD_INTELLECT_SHORT="Intellect", ITEM_MOD_AGILITY_SHORT="Agility", ITEM_MOD_CRIT_RATING_SHORT="CritRating", ITEM_MOD_HASTE_RATING_SHORT="HasteRating", ITEM_MOD_MASTERY_RATING_SHORT="MasteryRating", ITEM_MOD_VERSATILITY="VersatilityRating" }
  local score = 0
  for source, target in pairs(names) do
    local value = stats[source]
    if type(value) == "number" then score = score + value * (selected.weights[target] or 0) end
  end
  return score
end

function Scores.Show()
  local document = imported()
  local selected = Scores.Visible()
  if document == nil then print("[DpsLab] No hay pesos de item compatibles para este personaje."); return end
  local lines = {}
  for _, profile in ipairs(document.profiles or {}) do
    if selected[profile.id] ~= false and validWeights(profile) then lines[#lines + 1] = profile.name .. " (" .. profile.source .. ")" end
  end
  print("[DpsLab] Scores activos: " .. (#lines > 0 and table.concat(lines, ", ") or "ninguno"))
end

local function addTooltipScores(tooltip)
  if type(tooltip) ~= "table" or type(tooltip.GetItem) ~= "function" then return end
  local _, link = tooltip:GetItem()
  if type(link) ~= "string" then return end
  local document = imported()
  if document == nil then return end
  local selected = Scores.Visible()
  local added = false
  for _, profile in ipairs(document.profiles or {}) do
    if selected[profile.id] ~= false and validWeights(profile) then
      local score = Scores.ScoreItem(link, profile)
      if score ~= nil then
        if not added then tooltip:AddLine("DpsLab scores de equipo") end
        tooltip:AddDoubleLine(profile.name .. " (" .. profile.source .. ")", string.format("%.1f", score), 0.4, 0.8, 1, 1, 1, 1)
        added = true
      end
    end
  end
  if added and type(tooltip.Show) == "function" then tooltip:Show() end
end

function Scores.HookTooltips()
  if Scores._hooked or type(GameTooltip) ~= "table" or type(GameTooltip.HookScript) ~= "function" then return end
  Scores._hooked = pcall(GameTooltip.HookScript, GameTooltip, "OnTooltipSetItem", addTooltipScores)
end

function Scores.ShowConfig()
  local document = imported()
  local profiles = document and document.profiles or {}
  local frame = CreateFrame("Frame", "DpsLabItemScoreConfigFrame", UIParent, "BasicFrameTemplateWithInset")
  frame:SetSize(460, 170 + math.min(#profiles, 8) * 24); frame:SetPoint("CENTER"); frame:Show()
  frame.title = frame:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
  frame.title:SetPoint("TOP", 0, -34); frame.title:SetText("DpsLab — scores de equipo")
  frame.detail = frame:CreateFontString(nil, "OVERLAY", "GameFontNormal")
  frame.detail:SetPoint("TOP", 0, -62); frame.detail:SetWidth(410)
  frame.detail:SetText("/dpslab scores muestra las specs y builds elegidas. Los pesos personalizados provienen de SimC; los genéricos están identificados.")
  frame.toggle = CreateFrame("CheckButton", nil, frame, "UICheckButtonTemplate")
  frame.toggle:SetPoint("BOTTOMLEFT", 28, 22); frame.toggle.text = frame:CreateFontString(nil, "OVERLAY", "GameFontNormal")
  frame.toggle.text:SetPoint("LEFT", frame.toggle, "RIGHT", 4, 0); frame.toggle.text:SetText("Mostrar scores de item")
  frame.toggle:SetChecked(DpsLabItemScorePreferences == nil or DpsLabItemScorePreferences.enabled ~= false)
  frame.toggle:SetScript("OnClick", function(self) DpsLabItemScorePreferences = DpsLabItemScorePreferences or {}; DpsLabItemScorePreferences.enabled = self:GetChecked() and true or false end)
  DpsLabItemScorePreferences = type(DpsLabItemScorePreferences) == "table" and DpsLabItemScorePreferences or { enabled=true, selected={} }
  if type(DpsLabItemScorePreferences.selected) ~= "table" then DpsLabItemScorePreferences.selected = {} end
  for index, profile in ipairs(profiles) do
    if index > 8 then break end
    if validWeights(profile) then
      local choice = CreateFrame("CheckButton", nil, frame, "UICheckButtonTemplate")
      choice:SetPoint("TOPLEFT", 26, -86 - (index - 1) * 24)
      choice.text = choice:CreateFontString(nil, "OVERLAY", "GameFontNormal")
      choice.text:SetPoint("LEFT", choice, "RIGHT", 4, 0); choice.text:SetText(profile.name .. " — " .. profile.source)
      choice:SetChecked(DpsLabItemScorePreferences.selected[profile.id] ~= false)
      choice:SetScript("OnClick", function(self) DpsLabItemScorePreferences.selected[profile.id] = self:GetChecked() and true or false end)
    end
  end
end

Scores.Refresh()
DpsLabItemScores = Scores
Scores.HookTooltips()
