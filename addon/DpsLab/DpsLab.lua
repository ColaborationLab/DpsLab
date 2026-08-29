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

local function syntheticDetail(role)
  local package = DpsLabSyntheticGuidance
  if package == nil or package.schema_version ~= "0.1" or package.safety.actionable ~= false then
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

SLASH_DPSLAB1 = "/dpslab"
SlashCmdList["DPSLAB"] = function(message)
  local command, role = message:match("^(%S*)%s*(%S*)$")
  local view = DpsLab.RenderRole(command == "synthetic" and "synthetic" or nil, role)
  print("[DpsLab] " .. view.title .. ": " .. view.detail)
end

_G.DpsLab = DpsLab
