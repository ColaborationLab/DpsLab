-- Local score display. It never runs SimulationCraft or selects gameplay actions.
local Scores = {}
local ALLOWED = { Strength=true, Intellect=true, Agility=true, CritRating=true, HasteRating=true, MasteryRating=true, VersatilityRating=true }
local function T(key, fallback)
  local value = DpsLabLocalization and DpsLabLocalization.Get and DpsLabLocalization.Get(key)
  return value or fallback or key
end

local function notify(text)
  print("[DpsLab] " .. text)
  if type(UIErrorsFrame) == "table" and type(UIErrorsFrame.AddMessage) == "function" then
    UIErrorsFrame:AddMessage(text, 0.4, 0.8, 1)
  end
end

local function buttonTooltip(button, text)
  if type(button) ~= "table" or type(button.SetScript) ~= "function" then return end
  button:SetScript("OnEnter", function(self)
    if type(GameTooltip) == "table" then GameTooltip:SetOwner(self, "ANCHOR_TOP"); GameTooltip:SetText(text, 1, 1, 1, true); GameTooltip:Show() end
  end)
  button:SetScript("OnLeave", function() if type(GameTooltip) == "table" then GameTooltip:Hide() end end)
end

local function validWeights(value)
  if type(value) ~= "table" or type(value.name) ~= "string" or type(value.source) ~= "string"
    or (value.source ~= "personalized" and value.source ~= "generic" and value.source ~= "manual") or type(value.weights) ~= "table" then return false end
  for stat, weight in pairs(value.weights) do
    if ALLOWED[stat] ~= true or type(weight) ~= "number" or weight <= 0 or weight ~= weight or weight == math.huge then return false end
  end
  return next(value.weights) ~= nil
end

local function imported()
  local document = DpsLabRealRecommendation
  return type(document) == "table" and (document.schema_version == "0.4" or document.schema_version == "0.5")
    and document.state == "ready" and type(document.item_scores) == "table" and document or nil
end

local function matchesPlayer(document)
  local identity = document and document.character
  if type(identity) ~= "table" or type(identity.name) ~= "string" or type(identity.realm) ~= "string" or type(identity.class_id) ~= "number" then return false end
  if type(UnitFullName) ~= "function" or type(UnitClass) ~= "function" then return false end
  local name, realm = UnitFullName("player")
  local classID = select(3, UnitClass("player"))
  return name == identity.name and realm == identity.realm and classID == identity.class_id
end

local function currentSpecializationID()
  if type(GetSpecialization) ~= "function" or type(GetSpecializationInfo) ~= "function" then return nil end
  local specialization = GetSpecialization()
  return specialization and select(1, GetSpecializationInfo(specialization)) or nil
end

local function documentHasCurrentSpecialization(document)
  local specializationID = currentSpecializationID()
  if specializationID == nil or type(document) ~= "table" or type(document.item_scores) ~= "table"
    or type(document.item_scores.profiles) ~= "table" then return false end
  local prefix = tostring(specializationID) .. ":"
  for _, profile in ipairs(document.item_scores.profiles) do
    if validWeights(profile) and type(profile.id) == "string" and profile.id:sub(1, #prefix) == prefix then return true end
  end
  return false
end

local function defaultDocument()
  local defaults = DpsLabDefaultItemScoreProfiles
  if type(defaults) ~= "table" or defaults.schema_version ~= "0.1" or type(defaults.profiles) ~= "table"
    or type(UnitClass) ~= "function" or type(GetSpecialization) ~= "function" or type(GetSpecializationInfo) ~= "function" then return nil end
  local classID = select(3, UnitClass("player"))
  local specializationID = currentSpecializationID()
  for _, profile in ipairs(defaults.profiles) do
    if profile.class_id == classID and profile.specialization_id == specializationID and validWeights(profile) then
      return { character_id = "default:" .. classID .. ":" .. specializationID, item_scores = { profiles = { profile } } }
    end
  end
  return nil
end

local function sameData(left, right)
  if type(left) ~= type(right) then return false end
  if type(left) ~= "table" then return left == right end
  for key, value in pairs(left) do if not sameData(value, right[key]) then return false end end
  for key in pairs(right) do if left[key] == nil then return false end end
  return true
end

function Scores.Refresh()
  local document = imported()
  if document == nil or not matchesPlayer(document) or type(document.character_id) ~= "string" or #document.character_id ~= 32 then return end
  DpsLabItemScoreProfiles = type(DpsLabItemScoreProfiles) == "table" and DpsLabItemScoreProfiles or {}
  local current = DpsLabItemScoreProfiles[document.character_id]
  DpsLabItemScorePreferences = DpsLabItemScorePreferences or {}
  DpsLabItemScorePreferences.import_seen = DpsLabItemScorePreferences.import_seen or {}
  if sameData(current, document) or sameData(DpsLabItemScorePreferences.import_seen[document.character_id], document) then return end
  if Scores._pendingImport == document then return end
  Scores._pendingImport = document
  if type(StaticPopupDialogs) ~= "table" or type(StaticPopup_Show) ~= "function" then
    print("[DpsLab] " .. T("import_ready", "Hay nuevos pesos listos para importar; abre /dpslab config tras recargar."))
    return
  end
  StaticPopupDialogs["DPSLAB_IMPORT_SCORES"] = {
    text = T("import_prompt", "DpsLab recibió pesos simulados nuevos.\n\nUsar nuevos: sustituye el perfil activo.\nConservar actuales: ignora esta importación.\nGuardar actuales + usar nuevos: guarda una copia del perfil activo y activa los nuevos."),
    button1 = T("use_new", "Usar nuevos"), button2 = T("keep_current", "Conservar actuales"), button3 = T("save_current_new", "Guardar actuales + usar nuevos"),
    wide = true, buttonWidth = 175,
    OnShow = function(dialog)
      buttonTooltip(dialog.button1, T("replace_help", "Activa los pesos recién importados y sustituye el perfil activo actual."))
      buttonTooltip(dialog.button2, T("keep_help", "Mantiene el perfil activo actual e ignora los pesos recién importados."))
      buttonTooltip(dialog.button3, T("save_current_help", "Guarda una copia del perfil activo actual y después activa los pesos recién importados."))
    end,
    OnAccept = function(dialog, data)
      data = data or dialog.data
      DpsLabItemScoreProfiles[data.character_id] = CopyTable(data)
      DpsLabItemScorePreferences.import_seen[data.character_id] = CopyTable(data)
      if DpsLabItemScorePreferences.active_saved then DpsLabItemScorePreferences.active_saved[data.character_id] = nil end
      Scores._pendingImport = nil
      notify(T("import_activated", "Pesos nuevos activados. Los scores ya usan esta importación."))
      dialog:Hide()
    end,
    OnCancel = function(dialog, data)
      data = data or dialog.data
      DpsLabItemScorePreferences.import_seen[data.character_id] = CopyTable(data)
      Scores._pendingImport = nil
      notify(T("import_discarded", "Importación descartada. Se conservaron los pesos activos."))
      dialog:Hide()
    end,
    OnAlt = function(dialog, data)
      data = data or dialog.data
      DpsLabItemScorePreferences = type(DpsLabItemScorePreferences) == "table" and DpsLabItemScorePreferences or {}
      DpsLabItemScorePreferences.saved_profiles = type(DpsLabItemScorePreferences.saved_profiles) == "table" and DpsLabItemScorePreferences.saved_profiles or {}
      local saved = DpsLabItemScorePreferences.saved_profiles[data.character_id] or {}
      local prior = DpsLabItemScoreProfiles[data.character_id] or defaultDocument()
      if prior then
        local snapshot = CopyTable(prior)
        snapshot.character_id = data.character_id; snapshot.character = CopyTable(data.character)
        saved[#saved + 1] = { name = "Perfil guardado " .. tostring(#saved + 1), document = snapshot }
      end
      DpsLabItemScorePreferences.saved_profiles[data.character_id] = saved
      DpsLabItemScoreProfiles[data.character_id] = CopyTable(data)
      DpsLabItemScorePreferences.import_seen[data.character_id] = CopyTable(data)
      if DpsLabItemScorePreferences.active_saved then DpsLabItemScorePreferences.active_saved[data.character_id] = nil end
      Scores._pendingImport = nil
      notify(T("saved_current_activated", "Perfil anterior guardado y pesos nuevos activados."))
      dialog:Hide()
    end,
    timeout = 0, whileDead = true, hideOnEscape = true,
  }
  StaticPopup_Show("DPSLAB_IMPORT_SCORES", nil, nil, document)
end

local function chosenDocument(document)
  local prefs = DpsLabItemScorePreferences
  local index = document and prefs and prefs.active_saved and prefs.active_saved[document.character_id]
  local saved = index and prefs.saved_profiles and prefs.saved_profiles[document.character_id]
  return saved and saved[index] and saved[index].document or document
end

function Scores.Active()
  Scores.Refresh()
  if type(DpsLabItemScoreProfiles) == "table" then
    for _, document in pairs(DpsLabItemScoreProfiles) do
      if matchesPlayer(document) and documentHasCurrentSpecialization(document) then return chosenDocument(document) end
    end
  end
  return chosenDocument(defaultDocument())
end

function Scores.Visible(document)
  DpsLabItemScorePreferences = type(DpsLabItemScorePreferences) == "table" and DpsLabItemScorePreferences or { enabled=true, selected={} }
  if DpsLabItemScorePreferences.enabled == false or type(document) ~= "table" then return nil end
  if type(DpsLabItemScorePreferences.selected) ~= "table" then DpsLabItemScorePreferences.selected = {} end
  local selected = DpsLabItemScorePreferences.selected[document.character_id]
  if type(selected) ~= "table" then selected = {}; DpsLabItemScorePreferences.selected[document.character_id] = selected end
  return selected
end

function Scores.ScoreItem(link, selected)
  local getStats = type(C_Item) == "table" and C_Item.GetItemStats or GetItemStats
  if type(getStats) ~= "function" or type(link) ~= "string" or not validWeights(selected) then return nil end
  local ok, stats = pcall(getStats, link)
  if not ok or type(stats) ~= "table" then return nil end
  local names = { ITEM_MOD_STRENGTH_SHORT="Strength", ITEM_MOD_INTELLECT_SHORT="Intellect", ITEM_MOD_AGILITY_SHORT="Agility", ITEM_MOD_CRIT_RATING_SHORT="CritRating", ITEM_MOD_HASTE_RATING_SHORT="HasteRating", ITEM_MOD_MASTERY_RATING_SHORT="MasteryRating", ITEM_MOD_VERSATILITY="VersatilityRating" }
  local score, weighted = 0, false
  for source, target in pairs(names) do
    local value = stats[source]
    local weight = selected.weights[target]
    if type(value) == "number" and type(weight) == "number" then score = score + value * weight; weighted = true end
  end
  return weighted and score or nil
end

local function displayName(profile)
  local name = type(profile.name) == "string" and profile.name or "Pesos"
  name = name:gsub("^.-%s+—%s*", "")
  name = name:gsub("%s+sugerida", "")
  name = name:gsub("^%l", string.upper)
  return name .. (profile.source == "generic" and " (b)" or "") .. (profile.edited and " (ajustado)" or "")
end

local function profileLabel(profile)
  local specID = profile.specialization_id or tonumber((profile.id or ""):match("^(%d+):")) or currentSpecializationID()
  local icon
  if specID and type(GetSpecializationInfoByID) == "function" then
    icon = select(4, GetSpecializationInfoByID(specID))
  end
  return (icon and ("|T" .. tostring(icon) .. ":14:14:0:0|t ") or "") .. displayName(profile)
end

local WEIGHT_ORDER = { "Strength", "Agility", "Intellect", "CritRating", "HasteRating", "MasteryRating", "VersatilityRating" }

local function hex(text)
  return (text:gsub(".", function(character) return string.format("%02x", string.byte(character)) end))
end

local function unhex(text)
  if type(text) ~= "string" or #text % 2 ~= 0 or text:match("^[0-9a-f]+$") == nil then return nil end
  return (text:gsub("..", function(pair) return string.char(tonumber(pair, 16)) end))
end

function Scores.ExportString(profile)
  if not validWeights(profile) then return nil end
  local specID = profile.specialization_id or tonumber((profile.id or ""):match("^(%d+):")) or currentSpecializationID()
  if not specID then return nil end
  local name = displayName(profile):gsub(" %(ajustado%)$", ""):gsub(" %(b%)$", "")
  local values = {}
  for _, stat in ipairs(WEIGHT_ORDER) do
    if profile.weights[stat] then values[#values + 1] = stat .. "=" .. tostring(profile.weights[stat]) end
  end
  return "DPSLAB-WEIGHTS-0.1|" .. specID .. "|" .. hex(name) .. "|" .. table.concat(values, ",")
end

function Scores.ImportString(text)
  if type(text) ~= "string" or #text > 4096 then return nil end
  local spec, encodedName, values = text:match("^DPSLAB%-WEIGHTS%-0%.1|(%d+)|([0-9a-f]+)|(.+)$")
  local name, weights = unhex(encodedName), {}
  if tonumber(spec) ~= currentSpecializationID() or not name or #name > 80 then return nil end
  for pair in values:gmatch("[^,]+") do
    local stat, raw = pair:match("^(%a+)=([%d%.eE+-]+)$")
    local value = tonumber(raw)
    if ALLOWED[stat] ~= true or not value or value <= 0 or value ~= value or value == math.huge or weights[stat] then return nil end
    weights[stat] = value
  end
  return next(weights) and { name=name, weights=weights } or nil
end

local function initializeDropdown(control, values, selected, changed)
  if type(UIDropDownMenu_Initialize) ~= "function" then return end
  UIDropDownMenu_Initialize(control, function()
    for index, label in ipairs(values) do
      local info = UIDropDownMenu_CreateInfo()
      info.text = label; info.checked = index == selected
      info.func = function() UIDropDownMenu_SetSelectedID(control, index); UIDropDownMenu_SetText(control, label); changed(index) end
      UIDropDownMenu_AddButton(info)
    end
  end)
  UIDropDownMenu_SetText(control, values[selected] or "Seleccionar")
end

function Scores.Show()
  local document = Scores.Active()
  local selected = Scores.Visible(document)
  if document == nil or selected == nil then print("[DpsLab] No hay scores activos para este personaje."); return end
  local lines = {}
  for _, profile in ipairs(document.item_scores.profiles or {}) do
    if selected[profile.id] ~= false and validWeights(profile) then lines[#lines + 1] = displayName(profile) end
  end
  print("[DpsLab] Scores activos: " .. (#lines > 0 and table.concat(lines, ", ") or "ninguno"))
end

local function addTooltipScores(tooltip, suppliedLink)
  if type(tooltip) ~= "table" or type(tooltip.AddDoubleLine) ~= "function" then return end
  if type(tooltip.IsForbidden) == "function" and tooltip:IsForbidden() then return end
  local link = type(suppliedLink) == "string" and suppliedLink or nil
  if not link and type(TooltipUtil) == "table" and type(TooltipUtil.GetDisplayedItem) == "function" then
    local ok, _, displayed = pcall(TooltipUtil.GetDisplayedItem, tooltip)
    if ok then link = displayed end
  end
  if not link and type(tooltip.GetItem) == "function" then link = select(2, tooltip:GetItem()) end
  if type(link) ~= "string" then return end
  -- PostCall and ProcessInfo can both run for the same displayed item.
  -- Inspect actual lines, so ClearLines/rebuilds permit scores to be added again.
  if type(tooltip.GetName) == "function" and type(tooltip.NumLines) == "function" then
    local name = tooltip:GetName()
    if name then
      for index = 1, tooltip:NumLines() do
        local line = _G[name .. "TextLeft" .. index]
        if line and line:GetText() == "DpsLab Scores" then return end
      end
    end
  end
  local document = Scores.Active()
  local selected = Scores.Visible(document)
  if document == nil or selected == nil then return end
  local added = false
  for _, profile in ipairs(document.item_scores.profiles or {}) do
    if selected[profile.id] ~= false and validWeights(profile) then
      local score = Scores.ScoreItem(link, profile)
      if score ~= nil then
        if not added then tooltip:AddLine("DpsLab Scores") end
        tooltip:AddDoubleLine(profileLabel(profile), string.format("%.1f", score), 0.4, 0.8, 1, 1, 1, 1)
        added = true
      elseif not added then
        tooltip:AddLine("DpsLab Scores")
        tooltip:AddDoubleLine(profileLabel(profile), "N/D: efecto", 0.4, 0.8, 1, 1, 1, 1)
        added = true
      end
    end
  end
  if added and type(tooltip.Show) == "function" then tooltip:Show() end
end

function Scores.HookTooltips()
  if Scores._hooked then return end
  if type(TooltipDataProcessor) == "table" and type(TooltipDataProcessor.AddTooltipPostCall) == "function"
    and type(Enum) == "table" and type(Enum.TooltipDataType) == "table" and Enum.TooltipDataType.Item ~= nil then
    Scores._hooked = pcall(TooltipDataProcessor.AddTooltipPostCall, Enum.TooltipDataType.Item, addTooltipScores)
  elseif type(GameTooltip) == "table" and type(GameTooltip.HookScript) == "function" then
    Scores._hooked = pcall(GameTooltip.HookScript, GameTooltip, "OnTooltipSetItem", addTooltipScores)
  end
  for _, tooltip in pairs({ ShoppingTooltip1, ShoppingTooltip2, ItemRefShoppingTooltip1, ItemRefShoppingTooltip2 }) do
    if type(tooltip) == "table" and type(tooltip.HookScript) == "function" then
      pcall(tooltip.HookScript, tooltip, "OnTooltipSetItem", addTooltipScores)
      if type(hooksecurefunc) == "function" and type(TooltipUtil) == "table" and type(TooltipUtil.GetDisplayedItem) == "function" and type(tooltip.ProcessInfo) == "function" then
        hooksecurefunc(tooltip, "ProcessInfo", function()
          local _, link = TooltipUtil.GetDisplayedItem(tooltip)
          if type(link) == "string" then addTooltipScores(tooltip, link) end
        end)
      end
    end
  end
end

function Scores.ShowWeights()
  local document = Scores.Active()
  if not document or not document.item_scores.profiles[1] then print("[DpsLab] No hay pesos disponibles para esta especialización."); return end
  local frame = Scores._weightsFrame
  if not frame then
    frame = CreateFrame("Frame", "DpsLabWeightsFrame", UIParent, "BasicFrameTemplateWithInset")
    Scores._weightsFrame = frame
    frame:SetSize(560, 590); frame:SetPoint("CENTER"); frame:SetFrameStrata("DIALOG")
    frame:SetMovable(true); frame:EnableMouse(true); frame:RegisterForDrag("LeftButton")
    frame:SetScript("OnDragStart", frame.StartMoving); frame:SetScript("OnDragStop", frame.StopMovingOrSizing)
    frame.TitleText:SetText("DpsLab — " .. T("weights", "pesos estadísticos"))
    frame.heading = frame:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
    frame.heading:SetPoint("TOP", 0, -44); frame.heading:SetWidth(470)
    frame.help = frame:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    frame.help:SetPoint("TOP", 0, -77); frame.help:SetWidth(470)
    frame.help:SetText(T("weights_help", "(b): referencia beginner. Pesos simulados: estimación local para ese equipo y talentos; el score no equivale a DPS ni mide supervivencia."))
    frame.fields = {}
    local labels = { {"Strength", "Fuerza"}, {"Agility", "Agilidad"}, {"Intellect", "Intelecto"}, {"CritRating", "Crítico"}, {"HasteRating", "Celeridad"}, {"MasteryRating", "Maestría"}, {"VersatilityRating", "Versatilidad"} }
    for index, entry in ipairs(labels) do
      local label = frame:CreateFontString(nil, "OVERLAY", "GameFontNormal")
      label:SetPoint("TOPLEFT", 30, -116 - (index - 1) * 27); label:SetText(entry[2])
      local field = CreateFrame("EditBox", nil, frame, "InputBoxTemplate")
      field:SetSize(180, 22); field:SetPoint("TOPLEFT", 260, -112 - (index - 1) * 27); field:SetAutoFocus(false)
      frame.fields[entry[1]] = field
    end
    local function button(text, x, y, width)
      local control = CreateFrame("Button", nil, frame, "UIPanelButtonTemplate")
      control:SetSize(width, 24); control:SetPoint("TOPLEFT", x, y); control:SetText(text); return control
    end
    frame.buildLabel = frame:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    frame.buildLabel:SetPoint("TOPLEFT", 30, -309); frame.buildLabel:SetText(T("build", "Build consultada"))
    frame.buildDrop = CreateFrame("Frame", nil, frame, "UIDropDownMenuTemplate")
    frame.buildDrop:SetPoint("TOPLEFT", 190, -292); UIDropDownMenu_SetWidth(frame.buildDrop, 285)
    frame.nameLabel = frame:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    frame.nameLabel:SetPoint("TOPLEFT", 30, -352); frame.nameLabel:SetText(T("copy_name", "Nombre de la copia"))
    frame.name = CreateFrame("EditBox", nil, frame, "InputBoxTemplate")
    frame.name:SetSize(250, 22); frame.name:SetPoint("TOPLEFT", 190, -347); frame.name:SetAutoFocus(false)
    frame.save = button(T("save_activate", "Guardar y activar"), 410, -345, 125)
    buttonTooltip(frame.save, T("save_activate_help", "Crea una copia con el nombre y valores visibles y la deja como perfil activo. No modifica el perfil importado original."))
    frame.profileLabel = frame:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    frame.profileLabel:SetPoint("TOPLEFT", 30, -390); frame.profileLabel:SetText(T("active_profile", "Perfil de pesos activo"))
    frame.profileDrop = CreateFrame("Frame", nil, frame, "UIDropDownMenuTemplate")
    frame.profileDrop:SetPoint("TOPLEFT", 190, -373); UIDropDownMenu_SetWidth(frame.profileDrop, 285)
    buttonTooltip(frame.profileDrop, T("active_profile_help", "Elige qué perfil de pesos se usa ahora en los scores. Automático usa la importación de la app o, si no existe, la referencia beginner."))
    frame.transferLabel = frame:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    frame.transferLabel:SetPoint("TOPLEFT", 30, -432); frame.transferLabel:SetText(T("manual_transfer", "Intercambio manual"))
    frame.transfer = CreateFrame("EditBox", nil, frame, "InputBoxTemplate")
    frame.transfer:SetSize(300, 22); frame.transfer:SetPoint("TOPLEFT", 190, -427); frame.transfer:SetAutoFocus(false)
    frame.copyTransfer = button(T("copy", "Copiar"), 30, -466, 110)
    frame.importTransfer = button(T("paste_import", "Importar pegado"), 150, -466, 145)
    frame.removeBuild = button(T("delete_build", "Eliminar build"), 305, -466, 115)
    frame.removeProfile = button(T("delete_profile", "Eliminar perfil"), 430, -466, 105)
    buttonTooltip(frame.copyTransfer, T("copy_transfer_help", "Copia los pesos de la build visible para pegarlos en la app o guardarlos manualmente."))
    buttonTooltip(frame.importTransfer, T("import_transfer_help", "Lee una cadena DPSLAB-WEIGHTS pegada y la guarda como un perfil nuevo activo."))
    buttonTooltip(frame.removeBuild, T("delete_build_help", "Elimina la build visible solo del perfil de pesos guardado activo. No borra el loadout de talentos de WoW."))
    buttonTooltip(frame.removeProfile, T("delete_profile_help", "Elimina el perfil de pesos guardado activo. El perfil automático importado no se puede borrar desde aquí."))
    frame.status = frame:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    frame.status:SetPoint("BOTTOMLEFT", 30, 15); frame.status:SetWidth(500)
  end
  local profiles = document.item_scores.profiles
  local index = 1
  DpsLabItemScorePreferences = DpsLabItemScorePreferences or {}
  DpsLabItemScorePreferences.saved_profiles = DpsLabItemScorePreferences.saved_profiles or {}
  local saved = DpsLabItemScorePreferences.saved_profiles[document.character_id] or {}
  DpsLabItemScorePreferences.saved_profiles[document.character_id] = saved
  local savedIndex = DpsLabItemScorePreferences.active_saved and DpsLabItemScorePreferences.active_saved[document.character_id] or 0
  local function render()
    local profile = profiles[index]
    frame.heading:SetText(profileLabel(profile) .. "  (" .. index .. "/" .. #profiles .. ")")
    for stat, field in pairs(frame.fields) do field:SetText(profile.weights[stat] and tostring(profile.weights[stat]) or "") end
    frame.name:SetText(displayName(profile))
    frame.transfer:SetText(Scores.ExportString(profile) or "")
  end
  local buildNames = {}; for _, profile in ipairs(profiles) do buildNames[#buildNames + 1] = displayName(profile) end
  initializeDropdown(frame.buildDrop, buildNames, index, function(value) index = value; render() end)
  frame.save:SetScript("OnClick", function()
    local weights = {}
    for stat, field in pairs(frame.fields) do
      local text = field:GetText()
      if text ~= "" then
        local value = tonumber(text)
        if not value or value <= 0 or value ~= value or value == math.huge then frame.status:SetText(T("positive_weights", "Usa pesos positivos o deja la casilla vacía.")); return end
        weights[stat] = value
      end
    end
    if not next(weights) then frame.status:SetText(T("one_weight", "Introduce al menos un peso.")); return end
    local name = frame.name:GetText():match("^%s*(.-)%s*$")
    if name == "" then frame.status:SetText(T("name_profile", "Pon un nombre al perfil.")); return end
    local copy = CopyTable(document)
    copy.item_scores.profiles[index].weights = weights
    copy.item_scores.profiles[index].edited = true
    saved[#saved + 1] = { name = name, document = copy }
    savedIndex = #saved
    DpsLabItemScorePreferences.active_saved = DpsLabItemScorePreferences.active_saved or {}
    DpsLabItemScorePreferences.active_saved[document.character_id] = savedIndex
    notify(T("profile_saved_active", "Perfil de pesos guardado y activado: ") .. name)
    Scores.ShowWeights()
  end)
  local profileNames = { T("automatic_profile", "Automático: importado o beginner") }
  for _, entry in ipairs(saved) do profileNames[#profileNames + 1] = entry.name end
  local activeSaved = savedIndex
  initializeDropdown(frame.profileDrop, profileNames, activeSaved + 1, function(value)
    DpsLabItemScorePreferences.active_saved = DpsLabItemScorePreferences.active_saved or {}
    DpsLabItemScorePreferences.active_saved[document.character_id] = value > 1 and value - 1 or nil
    notify(T("profile_active", "Perfil de pesos activo: ") .. profileNames[value]); frame:Hide(); Scores.ShowWeights()
  end)
  frame.copyTransfer:SetScript("OnClick", function()
    local value = Scores.ExportString(profiles[index]) or ""
    frame.transfer:SetText(value); frame.transfer:SetFocus(); frame.transfer:HighlightText()
    if type(CopyToClipboard) == "function" then CopyToClipboard(value) end
    frame.status:SetText(T("transfer_ready", "Cadena preparada. Si no se copió automáticamente, usa Ctrl+C."))
  end)
  frame.importTransfer:SetScript("OnClick", function()
    local value = Scores.ImportString(frame.transfer:GetText())
    if not value then frame.status:SetText(T("invalid_transfer", "La cadena no es válida para la especialización actual.")); return end
    local copy = CopyTable(document); copy.item_scores.profiles[index].name = value.name
    copy.item_scores.profiles[index].weights = value.weights; copy.item_scores.profiles[index].edited = true
    saved[#saved + 1] = { name=value.name, document=copy }
    DpsLabItemScorePreferences.active_saved = DpsLabItemScorePreferences.active_saved or {}
    DpsLabItemScorePreferences.active_saved[document.character_id] = #saved
    notify(T("transfer_imported", "Cadena importada y activada como perfil: ") .. value.name); Scores.ShowWeights()
  end)
  frame.removeBuild:SetScript("OnClick", function()
    if savedIndex == 0 or not saved[savedIndex] then frame.status:SetText(T("save_before_delete", "Guarda y activa una copia antes de eliminar una build.")); return end
    local copy = saved[savedIndex].document
    local entries = copy and copy.item_scores and copy.item_scores.profiles
    if type(entries) ~= "table" or #entries < 2 then frame.status:SetText(T("keep_one_build", "El perfil debe conservar al menos una build. Elimina el perfil completo si no lo necesitas.")); return end
    table.remove(entries, index)
    notify(T("build_deleted", "Build eliminada del perfil guardado: ") .. saved[savedIndex].name); Scores.ShowWeights()
  end)
  frame.removeProfile:SetScript("OnClick", function()
    if savedIndex == 0 or not saved[savedIndex] then frame.status:SetText(T("auto_not_deleted", "El perfil automático no se borra. Elige un perfil guardado en la lista desplegable.")); return end
    local name = saved[savedIndex].name
    table.remove(saved, savedIndex)
    DpsLabItemScorePreferences.active_saved[document.character_id] = nil
    notify(T("profile_deleted", "Perfil de pesos eliminado: ") .. name); Scores.ShowWeights()
  end)
  frame.status:SetText(T("weights_hint", "Consulta cada build o guarda una copia con tus ajustes."))
  render(); frame:Show()
end

function Scores.ShowConfig()
  local document = Scores.Active()
  local profiles = document and document.item_scores and document.item_scores.profiles or {}
  DpsLabItemScorePreferences = type(DpsLabItemScorePreferences) == "table" and DpsLabItemScorePreferences or { enabled=true, selected={} }
  local frame = _G.DpsLabItemScoreConfigFrame or CreateFrame("Frame", "DpsLabItemScoreConfigFrame", UIParent, "BasicFrameTemplateWithInset")
  frame:SetSize(460, 258 + #profiles * 24); frame:SetPoint("CENTER"); frame:Show()
  frame.title = frame.title or frame:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
  frame.title:SetPoint("TOP", 0, -34); frame.title:SetText("DpsLab — " .. T("scores_title", "scores de equipo"))
  frame.localeLabel = frame.localeLabel or frame:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
  frame.localeLabel:SetPoint("TOPLEFT", 24, -38); frame.localeLabel:SetText(T("language", "Idioma"))
  frame.localeDrop = frame.localeDrop or CreateFrame("Frame", nil, frame, "UIDropDownMenuTemplate")
  frame.localeDrop:SetPoint("TOPLEFT", 70, -25); UIDropDownMenu_SetWidth(frame.localeDrop, 150)
  buttonTooltip(frame.localeDrop, T("language_help", "Elige Auto, español, inglés o portugués brasileño. La preferencia se conserva en este equipo."))
  local localeValues = { "auto", "es", "en", "pt" }
  local localeLabels = { T("language_auto", "Auto"), "ES", "EN", "PT-BR" }
  local selectedLocale = DpsLabItemScorePreferences.locale or "auto"
  local localeIndex = 1; for index, entry in ipairs(localeValues) do if entry == selectedLocale then localeIndex = index end end
  initializeDropdown(frame.localeDrop, localeLabels, localeIndex, function(index)
    local value = localeValues[index]
    if DpsLabLocalization and DpsLabLocalization.SetLocale then DpsLabLocalization.SetLocale(value) end
    UIDropDownMenu_SetText(frame.localeDrop, localeLabels[index]); notify(T("language_changed", "Idioma actualizado. Algunas ventanas se actualizarán al abrirlas de nuevo."))
  end)
  frame.weightsButton = frame.weightsButton or CreateFrame("Button", nil, frame, "UIPanelButtonTemplate")
  frame.weightsButton:SetSize(190, 22); frame.weightsButton:SetPoint("TOPLEFT", 18, -10); frame.weightsButton:SetText(T("view_edit", "Ver / editar pesos"))
  frame.weightsButton:SetScript("OnClick", Scores.ShowWeights)
  buttonTooltip(frame.weightsButton, T("weights_button_help", "Abre la lista de builds y perfiles de pesos. Aquí puedes consultar, nombrar, guardar, activar o transferir pesos."))
  frame.manualExport = frame.manualExport or CreateFrame("Button", nil, frame, "UIPanelButtonTemplate")
  frame.manualExport:SetSize(190, 22); frame.manualExport:SetPoint("TOPRIGHT", -18, -10); frame.manualExport:SetText(T("copy_export", "Copiar exportación"))
  frame.manualExport:SetScript("OnClick", function() if DpsLab and DpsLab.ShowManualAnalysisExport then DpsLab.ShowManualAnalysisExport() end end)
  buttonTooltip(frame.manualExport, T("manual_export_help", "Muestra la exportación completa para copiarla y pegarla en la app. La detección automática sigue disponible."))
  frame.detail = frame.detail or frame:CreateFontString(nil, "OVERLAY", "GameFontNormal")
  frame.detail:SetPoint("TOP", 0, -62); frame.detail:SetWidth(410)
  frame.detail:SetText(T("config_detail", "Los pesos personalizados provienen del loadout elegido en SimC; (b) identifica una build sugerida para principiantes."))
  frame.toggle = frame.toggle or CreateFrame("CheckButton", nil, frame, "UICheckButtonTemplate")
  frame.toggle:SetPoint("BOTTOMLEFT", 28, 106); frame.toggle.text = frame.toggle.text or frame:CreateFontString(nil, "OVERLAY", "GameFontNormal")
  frame.toggle.text:SetPoint("LEFT", frame.toggle, "RIGHT", 4, 0); frame.toggle.text:SetText(T("show_item_scores", "Mostrar scores de item"))
  frame.toggle:SetChecked(DpsLabItemScorePreferences.enabled ~= false)
  frame.toggle:SetScript("OnClick", function(self) DpsLabItemScorePreferences.enabled = self:GetChecked() and true or false end)
  local selected = Scores.Visible(document) or {}
  frame.choices = frame.choices or {}
  for _, choice in ipairs(frame.choices) do choice:Hide() end
  for index, profile in ipairs(profiles) do
    if validWeights(profile) then
      local choice = frame.choices[index] or CreateFrame("CheckButton", nil, frame, "UICheckButtonTemplate")
      frame.choices[index] = choice; choice:Show()
      choice:SetPoint("TOPLEFT", 26, -86 - (index - 1) * 24)
      choice.text = choice.text or choice:CreateFontString(nil, "OVERLAY", "GameFontNormal")
      choice.text:SetPoint("LEFT", choice, "RIGHT", 4, 0); choice.text:SetText(displayName(profile))
      choice:SetChecked(selected[profile.id] ~= false)
      choice:SetScript("OnClick", function(self) selected[profile.id] = self:GetChecked() and true or false end)
    end
  end
  local characterID = document and document.character_id
  DpsLabItemScorePreferences.saved_profiles = type(DpsLabItemScorePreferences.saved_profiles) == "table" and DpsLabItemScorePreferences.saved_profiles or {}
  local saved = characterID and DpsLabItemScorePreferences.saved_profiles[characterID] or {}
  frame.savedTitle = frame.savedTitle or frame:CreateFontString(nil, "OVERLAY", "GameFontNormal")
  frame.savedTitle:SetPoint("BOTTOMLEFT", 28, 80); frame.savedTitle:SetText(T("saved_profiles", "Perfiles de pesos guardados: ") .. tostring(#saved))
  frame.profileName = frame.profileName or CreateFrame("EditBox", nil, frame, "InputBoxTemplate")
  frame.profileName:SetAutoFocus(false); frame.profileName:SetSize(230, 20); frame.profileName:SetPoint("BOTTOMLEFT", 28, 52)
  frame.profileName:SetText(T("default_profile_name", "Perfil de pesos ") .. tostring(#saved + 1))
  frame.saveProfile = frame.saveProfile or CreateFrame("Button", nil, frame, "UIPanelButtonTemplate")
  frame.saveProfile:SetSize(110, 22); frame.saveProfile:SetPoint("LEFT", frame.profileName, "RIGHT", 8, 0); frame.saveProfile:SetText(T("save_profile", "Guardar perfil"))
  frame.saveProfile:SetScript("OnClick", function()
    if type(document) ~= "table" or type(characterID) ~= "string" then return end
    local name = frame.profileName:GetText()
    if type(name) ~= "string" or name == "" then name = T("default_profile_name", "Perfil de pesos ") .. tostring(#saved + 1) end
    saved[#saved + 1] = { name = name, document = CopyTable(document) }
    DpsLabItemScorePreferences.saved_profiles[characterID] = saved
    frame.savedTitle:SetText(T("saved_profiles", "Perfiles de pesos guardados: ") .. tostring(#saved))
  end)
  frame.savedList = frame.savedList or frame:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
  local names = {}; for _, entry in ipairs(saved) do names[#names + 1] = entry.name end
  frame.savedList:SetPoint("BOTTOMLEFT", 28, 28); frame.savedList:SetWidth(400); frame.savedList:SetJustifyH("LEFT")
  frame.savedList:SetText(#names > 0 and table.concat(names, ", ") or T("no_saved_profiles", "Aún no hay perfiles guardados."))
  local default = profiles[1]
  if frame.talent then frame.talent:Hide(); frame.copy:Hide() end
  if default and default.source == "generic" and type(default.talent_string) == "string" then
    frame.talent = frame.talent or CreateFrame("EditBox", nil, frame, "InputBoxTemplate")
    frame.talent:Show()
    frame.talent:SetAutoFocus(false); frame.talent:SetSize(330, 20); frame.talent:SetPoint("BOTTOMLEFT", 28, 4)
    frame.talent:SetText(default.talent_string); frame.talent:HighlightText()
    frame.copy = frame.copy or CreateFrame("Button", nil, frame, "UIPanelButtonTemplate")
    frame.copy:Show()
    frame.copy:SetSize(78, 22); frame.copy:SetPoint("LEFT", frame.talent, "RIGHT", 8, 0); frame.copy:SetText(T("copy", "Copiar"))
    frame.copy:SetScript("OnClick", function() frame.talent:SetFocus(); frame.talent:HighlightText() end)
  end
end

Scores.Refresh()
DpsLabItemScores = Scores
Scores.HookTooltips()
