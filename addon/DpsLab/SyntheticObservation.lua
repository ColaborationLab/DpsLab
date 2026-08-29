local Observation = {}

local function closed(value, allowed)
  if type(value) ~= "table" then return false end
  for key in pairs(value) do if allowed[key] ~= true then return false end end
  return true
end

local function boundedInteger(value, minimum, maximum)
  return type(value) == "number" and value == math.floor(value) and value >= minimum and value <= maximum
end

local function boundedToken(value, maximum)
  return type(value) == "string" and #value >= 1 and #value <= maximum and value:match("^[a-z0-9_.-]+$") ~= nil
end

function Observation.Validate(value)
  if not closed(value, { schema_version=true, identity=true, producer=true, compatibility=true, subject=true, observation=true, safety=true }) then return false, "observationFieldsInvalid" end
  if value.schema_version ~= "0.1" then return false, "observationSchemaIncompatible" end
  if not closed(value.identity, { observation_id=true, captured_at=true }) or not boundedToken(value.identity.observation_id, 80) or type(value.identity.captured_at) ~= "string" or value.identity.captured_at:match("^%d%d%d%d%-%d%d%-%d%dT%d%d:%d%d:%d%dZ$") == nil then return false, "observationIdentityInvalid" end
  if not closed(value.producer, { producer_id=true, producer_version=true }) or value.producer.producer_id ~= "dpslab.addon.synthetic" or not boundedToken(value.producer.producer_version, 24) then return false, "observationProducerUnsupported" end
  if not closed(value.compatibility, { wow_product=true, build=true, interface_version=true }) or value.compatibility.wow_product ~= "retail" or not boundedInteger(value.compatibility.build, 1, 999999) or not boundedInteger(value.compatibility.interface_version, 1, 999999) then return false, "observationCompatibilityInvalid" end
  if not closed(value.subject, { synthetic=true, class_token=true, specialization_token=true, role=true }) or value.subject.synthetic ~= true or not boundedToken(value.subject.class_token, 40) or not boundedToken(value.subject.specialization_token, 48) or (value.subject.role ~= "damage" and value.subject.role ~= "tank" and value.subject.role ~= "healer") then return false, "observationSubjectInvalid" end
  if not closed(value.observation, { state=true, sample_window_seconds=true, event_count=true, byte_count=true, signals=true }) or value.observation.state ~= "synthetic_fixture" or not boundedInteger(value.observation.sample_window_seconds, 0, 3600) or not boundedInteger(value.observation.event_count, 0, 100000) or not boundedInteger(value.observation.byte_count, 1, 4096) then return false, "observationPayloadInvalid" end
  local signals = value.observation.signals
  if not closed(signals, { damage_events=true, incoming_damage_events=true, healing_events=true }) or not boundedInteger(signals.damage_events, 0, 100000) or not boundedInteger(signals.incoming_damage_events, 0, 100000) or not boundedInteger(signals.healing_events, 0, 100000) then return false, "observationSignalsInvalid" end
  if signals.damage_events + signals.incoming_damage_events + signals.healing_events ~= value.observation.event_count then return false, "observationEventCountMismatch" end
  if not closed(value.safety, { synthetic=true, contains_personal_data=true, executable=true, actionable=true, no_automation=true }) or value.safety.synthetic ~= true or value.safety.contains_personal_data ~= false or value.safety.executable ~= false or value.safety.actionable ~= false or value.safety.no_automation ~= true then return false, "observationSafetyInvalid" end
  return true, "validSyntheticObservationNonActionable"
end

local function canonicalPayload(value)
  local signals = value.observation.signals
  return '{"compatibility":{"build":' .. tostring(value.compatibility.build)
    .. ',"interface_version":' .. tostring(value.compatibility.interface_version)
    .. ',"wow_product":"retail"},"identity":{"captured_at":"' .. value.identity.captured_at
    .. '","observation_id":"' .. value.identity.observation_id
    .. '"},"observation":{"byte_count":' .. tostring(value.observation.byte_count)
    .. ',"event_count":' .. tostring(value.observation.event_count)
    .. ',"sample_window_seconds":' .. tostring(value.observation.sample_window_seconds)
    .. ',"signals":{"damage_events":' .. tostring(signals.damage_events)
    .. ',"healing_events":' .. tostring(signals.healing_events)
    .. ',"incoming_damage_events":' .. tostring(signals.incoming_damage_events)
    .. '},"state":"synthetic_fixture"},"producer":{"producer_id":"dpslab.addon.synthetic","producer_version":"'
    .. value.producer.producer_version
    .. '"},"safety":{"actionable":false,"contains_personal_data":false,"executable":false,"no_automation":true,"synthetic":true},"schema_version":"0.1","subject":{"class_token":"'
    .. value.subject.class_token .. '","role":"' .. value.subject.role
    .. '","specialization_token":"' .. value.subject.specialization_token
    .. '","synthetic":true}}\n'
end

local function lowerHex(value)
  return (value:gsub(".", function(character) return string.format("%02x", string.byte(character)) end))
end

function Observation.Serialize(value)
  local valid, reason = Observation.Validate(value)
  if not valid then return nil, reason end
  local payload = canonicalPayload(value)
  if #payload ~= value.observation.byte_count then return nil, "observationSerializedByteCountMismatch" end
  if #payload > 4096 then return nil, "observationSerializedPayloadTooLarge" end
  return 'DpsLabObservationExport = "' .. lowerHex(payload) .. '"\n', "validSyntheticObservationTransportNonActionable"
end

DpsLabSyntheticObservation = {
  schema_version = "0.1",
  identity = { observation_id = "synthetic.observation.001", captured_at = "2026-08-29T00:00:00Z" },
  producer = { producer_id = "dpslab.addon.synthetic", producer_version = "0.1.0" },
  compatibility = { wow_product = "retail", build = 120000, interface_version = 120000 },
  subject = { synthetic = true, class_token = "synthetic_class", specialization_token = "synthetic_specialization", role = "damage" },
  observation = { state = "synthetic_fixture", sample_window_seconds = 0, event_count = 0, byte_count = 706, signals = { damage_events = 0, incoming_damage_events = 0, healing_events = 0 } },
  safety = { synthetic = true, contains_personal_data = false, executable = false, actionable = false, no_automation = true },
}

DpsLabObservation = Observation
DpsLabSyntheticObservationExport, DpsLabSyntheticObservationExportReason = Observation.Serialize(DpsLabSyntheticObservation)
