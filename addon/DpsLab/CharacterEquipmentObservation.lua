local Equipment = {}

local DRUID_CLASS_ID = 11
local SUPPORTED_SPECS = {
  [105] = { role = "HEALER", subject_role = "healer" },
  [102] = { role = "DAMAGER", subject_role = "damage" },
}

local function api()
  return {
    GetBuildInfo = GetBuildInfo, UnitClass = UnitClass,
    GetSpecialization = GetSpecialization, GetSpecializationInfo = GetSpecializationInfo,
    UnitLevel = UnitLevel, UnitRace = UnitRace,
    GetInventoryItemLink = GetInventoryItemLink,
    GetDetailedItemLevelInfo = GetDetailedItemLevelInfo,
    GetItemStats = GetItemStats, C_Item = C_Item,
    C_ClassTalents = C_ClassTalents, C_Traits = C_Traits,
  }
end

local function number(value, minimum, maximum)
  return type(value) == "number" and value == math.floor(value)
    and value >= minimum and value <= maximum and value or nil
end

local function buildNumber(value)
  if type(value) == "string" and value:match("^[1-9][0-9]*$") then value = tonumber(value) end
  return number(value, 1, 9999999)
end

local function json(value)
  return value:gsub("\\", "\\\\"):gsub('"', '\\"')
    :gsub("\n", "\\n"):gsub("\r", "\\r"):gsub("\t", "\\t")
end

local function item(a, link, location, includeStats)
  if type(link) ~= "string" or #link < 1 or #link > 2048 then return nil end
  local itemId = tonumber(link:match("item:(%d+)"))
  if not number(itemId, 1, 9999999) then return nil end
  local ok, itemLevel = pcall(a.GetDetailedItemLevelInfo, link)
  if not ok or not number(itemLevel, 1, 9999) then return nil, "analysis_item_info_unavailable" end
  local suffix = ""
  if includeStats then
    local getStats = type(a.C_Item) == "table" and a.C_Item.GetItemStats or a.GetItemStats
    if type(getStats) ~= "function" then return nil, "analysis_api_unavailable" end
    local statsOk, rawStats = pcall(getStats, link)
    if not statsOk or type(rawStats) ~= "table" then return nil, "analysis_item_info_unavailable" end
    local names = { ITEM_MOD_INTELLECT_SHORT="Intellect", ITEM_MOD_AGILITY_SHORT="Agility", ITEM_MOD_CRIT_RATING_SHORT="CritRating", ITEM_MOD_HASTE_RATING_SHORT="HasteRating", ITEM_MOD_MASTERY_RATING_SHORT="MasteryRating", ITEM_MOD_VERSATILITY="VersatilityRating" }
    local stats = {}
    for source, target in pairs(names) do
      local value = rawStats[source]
      if value ~= nil then
        if not number(value, 0, 999999) then return nil, "analysis_item_info_unavailable" end
        stats[#stats + 1] = '"' .. target .. '":' .. value
      end
    end
    table.sort(stats)
    suffix = ',"stats":{' .. table.concat(stats, ",") .. '}'
  end
  return '{"item_id":' .. itemId .. ',"item_level":' .. itemLevel
    .. ',"item_link":"' .. json(link) .. '","location":' .. location
    .. ',"slot":"slot_' .. location .. '","source":"equipped"' .. suffix .. '}'
end

local function loadout(a, configId, includeName)
  local ok, value = pcall(a.C_Traits.GenerateImportString, configId)
  if not ok or type(value) ~= "string" or #value < 1 or #value > 2048
    or value:match("^[A-Za-z0-9+/=]+$") == nil then return nil end
  if not includeName then return '{"config_id":' .. configId .. ',"talent_string":"' .. json(value) .. '"}' end
  local name = "Loadout " .. configId
  if type(a.C_Traits.GetConfigInfo) == "function" then
    local infoOk, info = pcall(a.C_Traits.GetConfigInfo, configId)
    if infoOk and type(info) == "table" and type(info.name) == "string" and #info.name > 0 and #info.name <= 80 then name = info.name end
  end
  return '{"config_id":' .. configId .. ',"name":"' .. json(name) .. '","talent_string":"' .. json(value) .. '"}'
end

local function loadouts(a, specializationId, selected)
  local classes, traits = a.C_ClassTalents, a.C_Traits
  if type(classes) ~= "table" or type(traits) ~= "table"
    or type(classes.GetActiveConfigID) ~= "function"
    or type(classes.GetConfigIDsBySpecID) ~= "function"
    or type(traits.GenerateImportString) ~= "function" then
    return nil, "analysis_talents_unavailable"
  end
  local activeOk, activeId = pcall(classes.GetActiveConfigID)
  local configsOk, configIds = pcall(classes.GetConfigIDsBySpecID, specializationId)
  if not activeOk or not configsOk or not number(activeId, 1, 2147483647)
    or type(configIds) ~= "table" then return nil, "analysis_talents_unavailable" end
  local alternatives, seen = {}, {}
  for _, configId in ipairs(configIds) do
    if not number(configId, 1, 2147483647) or seen[configId] then
      return nil, "analysis_talents_unavailable"
    end
    seen[configId] = true
    if configId ~= activeId then alternatives[#alternatives + 1] = configId end
  end
  table.sort(alternatives)
  local active = loadout(a, activeId, selected == nil)
  if active == nil then return nil, "analysis_talents_unavailable" end
  if selected ~= nil then
    if not number(selected, 1, #alternatives) then return nil, "analysis_comparison_loadout_unavailable" end
    local comparison = loadout(a, alternatives[selected], false)
    if comparison == nil then return nil, "analysis_talents_unavailable" end
    return '{"talent_loadouts":{"active":' .. active .. ',"comparison":' .. comparison .. '}}', "0.4"
  end
  local values = { active }
  for index = 1, #alternatives do
    local value = loadout(a, alternatives[index], true)
    if value == nil then return nil, "analysis_talents_unavailable" end
    values[#values + 1] = value
  end
  if #values < 2 then return nil, "analysis_comparison_loadout_unavailable" end
  return '{"talent_loadouts":[' .. table.concat(values, ",") .. ']}', "0.5"
end

function Equipment.Capture(selectedLoadout, injected)
  local a = injected or api()
  for _, name in ipairs({ "GetBuildInfo", "UnitClass", "GetSpecialization",
    "GetSpecializationInfo", "UnitLevel", "UnitRace", "GetInventoryItemLink",
    "GetDetailedItemLevelInfo" }) do
    if type(a[name]) ~= "function" then return nil, "analysis_api_unavailable" end
  end
  local buildOk, _, build, _, interface = pcall(a.GetBuildInfo)
  local classOk, _, _, classId = pcall(a.UnitClass, "player")
  local specOk, specIndex = pcall(a.GetSpecialization)
  local levelOk, level = pcall(a.UnitLevel, "player")
  local raceOk, _, _, raceId = pcall(a.UnitRace, "player")
  if not (buildOk and classOk and specOk and levelOk and raceOk) then return nil, "analysis_api_failed" end
  local infoOk, specializationId, _, _, _, role = pcall(a.GetSpecializationInfo, specIndex)
  if not infoOk then return nil, "analysis_api_failed" end
  build = buildNumber(build)
  if not (build and number(interface, 1, 9999999) and number(classId, 1, 1000)
    and number(specializationId, 1, 100000) and number(level, 1, 1000)
    and number(raceId, 1, 1000)) then return nil, "analysis_context_invalid" end
  local supported = SUPPORTED_SPECS[specializationId]
  if classId ~= DRUID_CLASS_ID or supported == nil or role ~= supported.role then
    return nil, "analysis_druid_specialization_required"
  end
  local talentContext, talentSchema = loadouts(a, specializationId, selectedLoadout)
  if talentContext == nil then return nil, talentSchema end
  local includeStats = talentSchema == "0.5"
  local equipped = {}
  for location = 1, 19 do
    local entry, reason = item(a, a.GetInventoryItemLink("player", location), location, includeStats)
    if reason then return nil, reason end
    if entry then equipped[#equipped + 1] = entry end
  end
  if #equipped == 0 then return nil, "analysis_items_unavailable" end
  local text = '{"analysis_context":' .. talentContext
    .. ',"compatibility":{"build":' .. build .. ',"interface_version":' .. interface
    .. ',"wow_product":"retail"},"equipment":{"equipped":[' .. table.concat(equipped, ",")
    .. ']},"observation_type":"live_manual_analysis_export","safety":{"contains_direct_identifiers":false,"executable":false,"no_automation":true},"schema_version":"0.4","subject":{"class_id":'
    .. classId .. ',"level":' .. level .. ',"race_id":' .. raceId
    .. ',"role":"' .. supported.subject_role .. '","specialization_id":' .. specializationId .. '}}\n'
  text = text:gsub('"schema_version":"0.4"', '"schema_version":"' .. (talentSchema == "0.5" and "0.7" or talentSchema) .. '"')
  if #text > 65536 then return nil, "analysis_payload_invalid" end
  return "DPSLAB-LIVE-ANALYSIS-0.1\n" .. text, "analysis_export_ready"
end

DpsLabCharacterEquipmentObservation = Equipment
