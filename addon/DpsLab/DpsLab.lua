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

function DpsLab.Render(state)
  if state == "synthetic" then
    return SYNTHETIC
  end
  return UNAVAILABLE
end

function DpsLab.IsActionable(view)
  return view ~= nil and view.status == "approved"
end

SLASH_DPSLAB1 = "/dpslab"
SlashCmdList["DPSLAB"] = function(message)
  local view = DpsLab.Render(message == "synthetic" and "synthetic" or nil)
  print("[DpsLab] " .. view.title .. ": " .. view.detail)
end

_G.DpsLab = DpsLab
