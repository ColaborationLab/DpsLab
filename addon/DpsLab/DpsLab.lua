local DpsLab = {}

local UNAVAILABLE = {
  status = "unavailable",
  title = "DpsLab guidance unavailable",
  detail = "No approved compatible local guidance is available.",
}

local SYNTHETIC = {
  status = "synthetic",
  title = "DpsLab synthetic guidance",
  detail = "Synthetic example only. It is not personalized advice.",
  limitations = "No live balance, simulation, automation, or desktop exchange.",
}

local function hasOnlyFields(value, allowed)
  if type(value) ~= "table" then return false end
  for key in pairs(value) do
    if allowed[key] ~= true then return false end
  end
  return true
end

function DpsLab.ValidatePackage(package, build, interfaceVersion, role)
  if type(package) ~= "table" then return false, "package_missing" end
  if not hasOnlyFields(package, { schema_version=true, identity=true, compatibility=true, lifecycle=true, evidence=true, safety=true, guidance=true }) then
    return false, "package_fields_invalid"
  end
  if package.schema_version ~= "0.1" then return false, "schema_incompatible" end
  if not hasOnlyFields(package.identity, { package_id=true, content_version=true }) then return false, "identity_invalid" end
  if type(package.identity.package_id) ~= "string" or type(package.identity.content_version) ~= "string" then return false, "identity_invalid" end
  local compatibility = package.compatibility
  if not hasOnlyFields(compatibility, { wow_product=true, build_min=true, build_max=true, interface_min=true, interface_max=true }) then return false, "compatibility_invalid" end
  if type(compatibility.wow_product) ~= "string" or type(compatibility.build_min) ~= "number" or type(compatibility.build_max) ~= "number" or type(compatibility.interface_min) ~= "number" or type(compatibility.interface_max) ~= "number" then return false, "compatibility_invalid" end
  if compatibility.build_min > compatibility.build_max or compatibility.interface_min > compatibility.interface_max then return false, "compatibility_invalid" end
  if type(build) ~= "number" or type(interfaceVersion) ~= "number" then return false, "context_unknown" end
  if build < compatibility.build_min or build > compatibility.build_max or interfaceVersion < compatibility.interface_min or interfaceVersion > compatibility.interface_max then
    return false, "context_incompatible"
  end
  if not hasOnlyFields(package.lifecycle, { state=true }) or package.lifecycle.state ~= "pending_review" then return false, "lifecycle_invalid" end
  if not hasOnlyFields(package.evidence, { tier=true, source_ids=true, limitations=true }) or type(package.evidence.tier) ~= "string" or type(package.evidence.source_ids) ~= "table" or type(package.evidence.limitations) ~= "table" or #package.evidence.source_ids > 8 or #package.evidence.limitations > 8 then return false, "evidence_invalid" end
  if not hasOnlyFields(package.safety, { no_automation=true, actionable=true, degradation_policy=true }) then return false, "safety_invalid" end
  if package.safety.no_automation ~= true or package.safety.actionable ~= false or package.safety.degradation_policy ~= "fail_closed" then
    return false, "safety_invalid"
  end
  if not hasOnlyFields(package.guidance, { damage=true, tank=true, healer=true }) then return false, "guidance_invalid" end
  if role ~= "damage" and role ~= "tank" and role ~= "healer" then return false, "role_unsupported" end
  if not hasOnlyFields(package.guidance[role], { priority=true }) or type(package.guidance[role].priority) ~= "string" or #package.guidance[role].priority > 240 then
    return false, "guidance_invalid"
  end
  return true, "validSyntheticNonActionable"
end

local function syntheticDetail(role)
  local package = DpsLabSyntheticGuidance
  local valid = DpsLab.ValidatePackage(package, 120000, 120000, role)
  if not valid then
    return SYNTHETIC.detail
  end
  local roleGuidance = package.guidance[role]
  return roleGuidance and roleGuidance.priority or SYNTHETIC.detail
end

function DpsLab.RenderRole(state, role)
  if state == "synthetic" then
    return { status = SYNTHETIC.status, title = SYNTHETIC.title, detail = syntheticDetail(role), limitations = SYNTHETIC.limitations }
  end
  return UNAVAILABLE
end

function DpsLab.Render(state)
  return DpsLab.RenderRole(state, nil)
end

function DpsLab.IsActionable(view)
  return view ~= nil and view.status == "approved"
end

local SYNTHETIC_EXPORT_REASON = "validSyntheticObservationTransportNonActionable"
local EXPORT_STATUS = {
  retained = "Synthetic export retained for WoW-managed persistence.",
  identity_retained = "Identity snapshot retained for WoW-managed persistence.",
  identity_api_unavailable = "Identity snapshot unavailable: required API unavailable.",
  identity_api_failed = "Identity snapshot unavailable: API call failed.",
  identity_context_invalid = "Identity snapshot unavailable: context invalid.",
  identity_role_unsupported = "Identity snapshot unavailable: role unsupported.",
  identity_payload_invalid = "Identity snapshot unavailable: payload invalid.",
  registry_retained = "Specialization registry snapshot retained for WoW-managed persistence.",
  registry_api_unavailable = "Specialization registry unavailable: required API unavailable.",
  registry_api_failed = "Specialization registry unavailable: API call failed.",
  registry_context_invalid = "Specialization registry unavailable: context invalid.",
  registry_shape_unsupported = "Specialization registry unavailable: class shape unsupported.",
  registry_role_unsupported = "Specialization registry unavailable: role unsupported.",
  registry_payload_invalid = "Specialization registry unavailable: payload invalid.",
  cleared = "Synthetic export cleared.",
  unavailable = "Synthetic export unavailable.",
  unsupported = "Synthetic export command unavailable.",
  analysis_export_ready = "Manual analysis export is ready to copy.",
  analysis_api_unavailable = "Manual analysis export unavailable: required API unavailable.",
  analysis_api_failed = "Manual analysis export unavailable: API call failed.",
  analysis_context_invalid = "Manual analysis export unavailable: context invalid.",
  analysis_items_unavailable = "Manual analysis export unavailable: equipment unavailable.",
  analysis_bag_invalid = "Manual analysis export unavailable: selected bag invalid.",
  analysis_payload_invalid = "Manual analysis export unavailable: payload invalid.",
}

local function handleAnalysisExport(bag)
  local module = DpsLabCharacterEquipmentObservation
  if type(module) ~= "table" or type(module.Capture) ~= "function" then return nil, "analysis_api_unavailable" end
  return module.Capture(bag)
end

function DpsLab.StartSyntheticTraining(config, injected)
  local module = DpsLabTrainingDummySession
  if type(module) ~= "table" or type(module.Start) ~= "function" then return nil, "training_synthetic_input_unavailable" end
  return module.Start(config, injected)
end

function DpsLab.FinishSyntheticTraining(active, metrics, injected, cancelled)
  local module = DpsLabTrainingDummySession
  if type(module) ~= "table" or type(module.Finish) ~= "function" then return nil, "training_synthetic_input_unavailable" end
  return module.Finish(active, metrics, injected, cancelled)
end

local function showManualAnalysisExport(payload)
  local frame = CreateFrame("Frame", "DpsLabManualAnalysisExportFrame", UIParent, "BackdropTemplate")
  frame:SetSize(700, 180); frame:SetPoint("CENTER"); frame:SetFrameStrata("DIALOG")
  local box = CreateFrame("EditBox", nil, frame, "InputBoxTemplate")
  box:SetMultiLine(true); box:SetAutoFocus(false); box:SetSize(660, 140); box:SetPoint("CENTER")
  box:SetText(payload); box:HighlightText(); box:SetFocus(); frame:Show()
end

local function syntheticExportCandidate()
  if type(DpsLabSyntheticObservationExport) ~= "string" then return nil end
  if DpsLabSyntheticObservationExportReason ~= SYNTHETIC_EXPORT_REASON then return nil end
  local candidate = DpsLabSyntheticObservationExport:match('^DpsLabObservationExport = "([0-9a-f]+)"\n$')
  if candidate == nil or #candidate == 0 or #candidate > 8192 or #candidate % 2 ~= 0 then return nil end
  return candidate
end

local function handleIdentityExport()
  local module = DpsLabCharacterIdentityObservation
  if type(module) ~= "table" or type(module.Capture) ~= "function" then
    return "identity_api_unavailable"
  end
  local candidate, reason = module.Capture()
  if candidate == nil then
    if EXPORT_STATUS[reason] ~= nil then return reason end
    return "identity_payload_invalid"
  end
  _G.DpsLabObservationExport = candidate
  return "identity_retained"
end

local function handleSpecializationRegistryExport()
  local module = DpsLabCharacterSpecializationRegistryObservation
  if type(module) ~= "table" or type(module.Capture) ~= "function" then
    return "registry_api_unavailable"
  end
  local candidate, reason = module.Capture()
  if candidate == nil then
    if EXPORT_STATUS[reason] ~= nil then return reason end
    return "registry_payload_invalid"
  end
  _G.DpsLabObservationExport = candidate
  return "registry_retained"
end

local function handleSyntheticExport(action)
  if action == "clear" then
    _G.DpsLabObservationExport = nil
    return "cleared"
  end
  if action ~= "synthetic" then return "unsupported" end
  local candidate = syntheticExportCandidate()
  if candidate == nil then return "unavailable" end
  _G.DpsLabObservationExport = candidate
  return "retained"
end

SLASH_DPSLAB1 = "/dpslab"
SlashCmdList["DPSLAB"] = function(message)
  local command, role, argument = message:match("^(%S*)%s*(%S*)%s*(%S*)$")
  if command == "export" then
    if role == "analysis" then
      local payload, status = handleAnalysisExport(argument == "" and nil or tonumber(argument))
      if payload ~= nil then showManualAnalysisExport(payload) end
      print("[DpsLab] " .. EXPORT_STATUS[status])
      return
    end
    local status = role == "identity" and handleIdentityExport()
      or role == "specialization-registry" and handleSpecializationRegistryExport()
      or handleSyntheticExport(role)
    print("[DpsLab] " .. EXPORT_STATUS[status])
    return
  end
  local view = DpsLab.RenderRole(command == "synthetic" and "synthetic" or nil, role)
  print("[DpsLab] " .. view.title .. ": " .. view.detail)
end

_G.DpsLab = DpsLab
