local Exchange = {}

local function closed(value, allowed)
  if type(value) ~= "table" then return false end
  for key in pairs(value) do if allowed[key] ~= true then return false end end
  return true
end

local function lowerSha256(value)
  return type(value) == "string" and #value == 64 and value:match("^[0-9a-f]+$") ~= nil
end

function Exchange.Validate(value)
  if not closed(value, { schema_version=true, identity=true, producer=true, compatibility=true, payload=true, integrity=true, safety=true }) then return false, "envelopeFieldsInvalid" end
  if value.schema_version ~= "0.1" then return false, "schemaIncompatible" end
  if not closed(value.identity, { exchange_id=true, created_at=true }) or type(value.identity.exchange_id) ~= "string" or #value.identity.exchange_id > 80 or type(value.identity.created_at) ~= "string" then return false, "identityInvalid" end
  if not closed(value.producer, { producer_id=true, producer_version=true }) or value.producer.producer_id ~= "dpslab.desktop.synthetic" or type(value.producer.producer_version) ~= "string" then return false, "producerUnsupported" end
  if not closed(value.compatibility, { addon_min=true, addon_max=true, guidance_schema=true }) or value.compatibility.guidance_schema ~= "0.1" or type(value.compatibility.addon_min) ~= "string" or type(value.compatibility.addon_max) ~= "string" then return false, "compatibilityInvalid" end
  if not closed(value.payload, { guidance_package_id=true, guidance_content_version=true, role_count=true, byte_count=true }) then return false, "payloadInvalid" end
  if type(value.payload.guidance_package_id) ~= "string" or #value.payload.guidance_package_id > 96 or type(value.payload.guidance_content_version) ~= "string" or type(value.payload.role_count) ~= "number" or value.payload.role_count < 1 or value.payload.role_count > 3 or type(value.payload.byte_count) ~= "number" or value.payload.byte_count < 1 or value.payload.byte_count > 8192 then return false, "payloadInvalid" end
  if not closed(value.integrity, { algorithm=true, payload_sha256=true }) or value.integrity.algorithm ~= "sha256" or not lowerSha256(value.integrity.payload_sha256) then return false, "integrityInvalid" end
  if not closed(value.safety, { synthetic=true, executable=true, contains_credentials=true, actionable=true }) or value.safety.synthetic ~= true or value.safety.executable ~= false or value.safety.contains_credentials ~= false or value.safety.actionable ~= false then return false, "safetyInvalid" end
  return true, "validSyntheticExchangeNonActionable"
end

local function guidanceRoleCount(value)
  if type(value) ~= "table" then return nil end
  local count = 0
  for role in pairs(value) do
    if role ~= "damage" and role ~= "tank" and role ~= "healer" then return nil end
    count = count + 1
  end
  return count
end

function Exchange.ValidateBinding(envelope, package)
  local envelopeValid, envelopeReason = Exchange.Validate(envelope)
  if not envelopeValid then return false, envelopeReason end
  if type(package) ~= "table" or type(package.identity) ~= "table" then return false, "bindingPackageMissing" end
  if package.identity.package_id ~= envelope.payload.guidance_package_id then return false, "bindingPackageIdMismatch" end
  if package.identity.content_version ~= envelope.payload.guidance_content_version then return false, "bindingContentVersionMismatch" end
  if package.schema_version ~= envelope.compatibility.guidance_schema then return false, "bindingSchemaMismatch" end
  if type(package.lifecycle) ~= "table" or package.lifecycle.state ~= "pending_review" then return false, "bindingLifecycleInvalid" end
  if type(package.evidence) ~= "table" or package.evidence.tier ~= "synthetic_fixture" then return false, "bindingEvidenceInvalid" end
  if type(package.safety) ~= "table" or package.safety.no_automation ~= true or package.safety.actionable ~= false or package.safety.degradation_policy ~= "fail_closed" then return false, "bindingSafetyInvalid" end
  local roleCount = guidanceRoleCount(package.guidance)
  if roleCount == nil or roleCount ~= envelope.payload.role_count then return false, "bindingRoleCountMismatch" end
  return true, "validSyntheticBindingNonActionable"
end

DpsLabSyntheticExchange = {
  schema_version = "0.1",
  identity = { exchange_id = "synthetic.exchange.001", created_at = "2026-08-29T00:00:00Z" },
  producer = { producer_id = "dpslab.desktop.synthetic", producer_version = "0.1.0" },
  compatibility = { addon_min = "0.1.0", addon_max = "0.1.99", guidance_schema = "0.1" },
  payload = { guidance_package_id = "synthetic.addon.guidance.001", guidance_content_version = "0.1.0", role_count = 3, byte_count = 512 },
  integrity = { algorithm = "sha256", payload_sha256 = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" },
  safety = { synthetic = true, executable = false, contains_credentials = false, actionable = false },
}

DpsLabExchange = Exchange
