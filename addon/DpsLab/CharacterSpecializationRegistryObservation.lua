local Registry = {}

local API_NAMES = {
  "GetBuildInfo",
  "UnitClass",
  "UnitSex",
  "GetNumSpecializationsForClassID",
  "GetSpecializationInfoForClassID",
  "GetServerTime",
}

local ROLE_MAP = {
  DAMAGER = "damage",
  TANK = "tank",
  HEALER = "healer",
}

local function runtimeApi()
  return {
    GetBuildInfo = GetBuildInfo,
    UnitClass = UnitClass,
    UnitSex = UnitSex,
    GetNumSpecializationsForClassID = C_SpecializationInfo
      and C_SpecializationInfo.GetNumSpecializationsForClassID,
    GetSpecializationInfoForClassID = GetSpecializationInfoForClassID,
    GetServerTime = GetServerTime,
  }
end

local function apiAvailable(api)
  if type(api) ~= "table" then return false end
  for _, name in ipairs(API_NAMES) do
    if type(api[name]) ~= "function" then return false end
  end
  return true
end

local function boundedInteger(value, minimum, maximum, allowNumericString)
  if allowNumericString and type(value) == "string" and value:match("^%d+$") then
    value = tonumber(value)
  end
  return type(value) == "number"
    and value == math.floor(value)
    and value >= minimum
    and value <= maximum
    and value or nil
end

local function lowerHex(value)
  return (value:gsub(".", function(character)
    return string.format("%02x", string.byte(character))
  end))
end

local function canonicalPayload(value)
  local entries = {}
  for index, specialization in ipairs(value.specializations) do
    entries[index] = '{"role":"' .. specialization.role
      .. '","specialization_id":' .. tostring(specialization.specialization_id) .. '}'
  end
  return '{"capture":{"captured_at":' .. tostring(value.captured_at)
    .. ',"mode":"manual_command"},"compatibility":{"build":' .. tostring(value.build)
    .. ',"interface_version":' .. tostring(value.interface_version)
    .. ',"wow_product":"retail"},"observation_type":"class_specialization_registry_snapshot"'
    .. ',"safety":{"actionable":false,"contains_character_data":true'
    .. ',"contains_direct_identifiers":false,"executable":false,"no_automation":true}'
    .. ',"schema_version":"0.1","specializations":[' .. table.concat(entries, ",")
    .. '],"subject":{"class_id":' .. tostring(value.class_id) .. '}}\n'
end

function Registry.Capture(api)
  api = api == nil and runtimeApi() or api
  if not apiAvailable(api) then return nil, "registry_api_unavailable" end

  local buildOk, _, buildValue, _, interfaceValue = pcall(api.GetBuildInfo)
  local classOk, _, _, classValue = pcall(api.UnitClass, "player")
  local sexOk, sexValue = pcall(api.UnitSex, "player")
  local timeOk, capturedAtValue = pcall(api.GetServerTime)
  if not (buildOk and classOk and sexOk and timeOk) then
    return nil, "registry_api_failed"
  end

  local classId = boundedInteger(classValue, 1, 1000, false)
  local sex = boundedInteger(sexValue, 1, 3, false)
  if classId == nil or sex == nil then return nil, "registry_context_invalid" end
  local countOk, countValue = pcall(api.GetNumSpecializationsForClassID, classId)
  if not countOk then return nil, "registry_api_failed" end
  local count = boundedInteger(countValue, 1, 16, false)
  if count ~= 4 then return nil, "registry_shape_unsupported" end

  local specializations = {}
  local seen = {}
  local roleCounts = { damage = 0, tank = 0, healer = 0 }
  for index = 1, count do
    local infoOk, specializationValue, _, _, _, roleValue =
      pcall(api.GetSpecializationInfoForClassID, classId, index, sex)
    if not infoOk then return nil, "registry_api_failed" end
    local specializationId = boundedInteger(specializationValue, 1, 100000, false)
    local role = ROLE_MAP[roleValue]
    if specializationId == nil or seen[specializationId] then
      return nil, "registry_context_invalid"
    end
    if role == nil then return nil, "registry_role_unsupported" end
    seen[specializationId] = true
    roleCounts[role] = roleCounts[role] + 1
    specializations[index] = { specialization_id = specializationId, role = role }
  end
  if roleCounts.damage ~= 2 or roleCounts.tank ~= 1 or roleCounts.healer ~= 1 then
    return nil, "registry_shape_unsupported"
  end

  local candidate = {
    build = boundedInteger(buildValue, 1, 9999999, true),
    interface_version = boundedInteger(interfaceValue, 1, 9999999, false),
    class_id = classId,
    captured_at = boundedInteger(capturedAtValue, 1, 9999999999, false),
    specializations = specializations,
  }
  for _, name in ipairs({ "build", "interface_version", "class_id", "captured_at" }) do
    if candidate[name] == nil then return nil, "registry_context_invalid" end
  end

  local payload = canonicalPayload(candidate)
  if #payload < 1 or #payload > 4096 then return nil, "registry_payload_invalid" end
  local encoded = lowerHex(payload)
  if #encoded < 2 or #encoded > 8192 or #encoded % 2 ~= 0 then
    return nil, "registry_payload_invalid"
  end
  return encoded, "specialization_registry_valid_nonactionable"
end

DpsLabCharacterSpecializationRegistryObservation = Registry
