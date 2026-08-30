local Identity = {}

local API_NAMES = {
  "GetBuildInfo",
  "UnitClass",
  "GetSpecialization",
  "GetSpecializationInfo",
  "UnitLevel",
  "UnitRace",
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
    GetSpecialization = GetSpecialization,
    GetSpecializationInfo = GetSpecializationInfo,
    UnitLevel = UnitLevel,
    UnitRace = UnitRace,
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
  return '{"capture":{"captured_at":' .. tostring(value.captured_at)
    .. ',"mode":"manual_command"},"compatibility":{"build":' .. tostring(value.build)
    .. ',"interface_version":' .. tostring(value.interface_version)
    .. ',"wow_product":"retail"},"observation_type":"character_identity_snapshot"'
    .. ',"safety":{"actionable":false,"contains_character_data":true'
    .. ',"contains_direct_identifiers":false,"executable":false,"no_automation":true}'
    .. ',"schema_version":"0.1","subject":{"class_id":' .. tostring(value.class_id)
    .. ',"level":' .. tostring(value.level) .. ',"race_id":' .. tostring(value.race_id)
    .. ',"role":"' .. value.role .. '","specialization_id":'
    .. tostring(value.specialization_id) .. '}}\n'
end

function Identity.Capture(api)
  api = api == nil and runtimeApi() or api
  if not apiAvailable(api) then return nil, "identity_api_unavailable" end

  local buildOk, _, buildValue, _, interfaceValue = pcall(api.GetBuildInfo)
  local classOk, _, _, classValue = pcall(api.UnitClass, "player")
  local specializationOk, specializationIndex = pcall(api.GetSpecialization)
  local levelOk, levelValue = pcall(api.UnitLevel, "player")
  local raceOk, _, _, raceValue = pcall(api.UnitRace, "player")
  local timeOk, capturedAtValue = pcall(api.GetServerTime)
  if not (buildOk and classOk and specializationOk and levelOk and raceOk and timeOk) then
    return nil, "identity_api_failed"
  end

  local specializationIndexValue = boundedInteger(specializationIndex, 1, 16, false)
  if specializationIndexValue == nil then return nil, "identity_context_invalid" end
  local specializationInfoOk, specializationValue, _, _, _, roleValue =
    pcall(api.GetSpecializationInfo, specializationIndexValue)
  if not specializationInfoOk then return nil, "identity_api_failed" end

  local candidate = {
    build = boundedInteger(buildValue, 1, 9999999, true),
    interface_version = boundedInteger(interfaceValue, 1, 9999999, false),
    class_id = boundedInteger(classValue, 1, 1000, false),
    specialization_id = boundedInteger(specializationValue, 1, 100000, false),
    role = ROLE_MAP[roleValue],
    level = boundedInteger(levelValue, 1, 1000, false),
    race_id = boundedInteger(raceValue, 1, 1000, false),
    captured_at = boundedInteger(capturedAtValue, 1, 9999999999, false),
  }
  for _, name in ipairs({ "build", "interface_version", "class_id", "specialization_id", "level", "race_id", "captured_at" }) do
    if candidate[name] == nil then return nil, "identity_context_invalid" end
  end
  if candidate.role == nil then return nil, "identity_role_unsupported" end

  local payload = canonicalPayload(candidate)
  if #payload < 1 or #payload > 4096 then return nil, "identity_payload_invalid" end
  local encoded = lowerHex(payload)
  if #encoded < 2 or #encoded > 8192 or #encoded % 2 ~= 0 then
    return nil, "identity_payload_invalid"
  end
  return encoded, "identity_snapshot_valid_nonactionable"
end

DpsLabCharacterIdentityObservation = Identity
