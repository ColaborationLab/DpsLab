local Session = {}

local PRESETS = { [120] = true, [180] = true, [300] = true }
local function integer(value, low, high)
  return type(value) == "number" and value == math.floor(value) and value >= low and value <= high
end
local function closed(value, allowed)
  if type(value) ~= "table" then return false end
  for key in pairs(value) do if allowed[key] ~= true then return false end end
  return true
end

function Session.Start(config, injected)
  if type(injected) ~= "table" or type(injected.Now) ~= "function" or type(injected.Target) ~= "function" then return nil, "training_synthetic_input_unavailable" end
  if not closed(config, { duration_seconds = true }) or not integer(config.duration_seconds, 60, 900) then return nil, "training_duration_invalid" end
  local nowOk, started = pcall(injected.Now)
  local targetOk, target = pcall(injected.Target)
  if not nowOk or not integer(started, 1, 9999999999) then return nil, "training_clock_invalid" end
  local classification = targetOk and target == "synthetic_training_dummy" and "confirmed" or "unconfirmed_target"
  return { state = "active", started_at = started, duration_seconds = config.duration_seconds, target_classification = classification }, "training_started"
end

function Session.Finish(active, metrics, injected, cancelled)
  if type(injected) ~= "table" or type(injected.Now) ~= "function" then return nil, "training_synthetic_input_unavailable" end
  if not closed(active, { state=true, started_at=true, duration_seconds=true, target_classification=true }) or active.state ~= "active" then return nil, "training_state_invalid" end
  if not closed(metrics, { action_count=true, resource_cap_count=true, inactivity_seconds=true }) then return nil, "training_metrics_invalid" end
  for _, key in ipairs({ "action_count", "resource_cap_count", "inactivity_seconds" }) do if not integer(metrics[key], 0, 100000) then return nil, "training_metrics_invalid" end end
  local nowOk, finished = pcall(injected.Now)
  if not nowOk or not integer(finished, active.started_at, 9999999999) then return nil, "training_clock_invalid" end
  local elapsed = finished - active.started_at
  if elapsed > 900 then return nil, "training_elapsed_invalid" end
  local state = cancelled == true and "cancelled" or (elapsed < active.duration_seconds and "incomplete" or "completed")
  return { schema_version="0.1", observation_type="synthetic_training_dummy_session", state=state, duration_seconds=elapsed, target_classification=active.target_classification, metrics=metrics, safety={ synthetic=true, executable=false, no_automation=true } }, "training_finished"
end

Session.PRESETS = PRESETS
DpsLabTrainingDummySession = Session
