local Guidance = {}

local function closed(value, allowed)
  if type(value) ~= "table" then return false end
  for key in pairs(value) do if allowed[key] ~= true then return false end end
  return true
end

function Guidance.Validate(value, role)
  if not closed(value, { schema_version=true, lifecycle=true, safety=true, synthetic=true, roles=true }) then return false, "advisor_fields_invalid" end
  if value.schema_version ~= "0.1" or value.synthetic ~= true then return false, "advisor_schema_invalid" end
  if not closed(value.lifecycle, { state=true }) or value.lifecycle.state ~= "synthetic_fixture" then return false, "advisor_lifecycle_invalid" end
  if not closed(value.safety, { actionable=true, no_automation=true }) or value.safety.actionable ~= false or value.safety.no_automation ~= true then return false, "advisor_safety_invalid" end
  if role ~= "damage" and role ~= "tank" and role ~= "healer" then return false, "advisor_role_invalid" end
  local entry = value.roles[role]
  if not closed(entry, { statistic_target=true, gear_priority=true, priority_display=true, safety_first=true }) then return false, "advisor_role_invalid" end
  if type(entry.statistic_target) ~= "string" or #entry.statistic_target > 80 or type(entry.gear_priority) ~= "string" or #entry.gear_priority > 120 or type(entry.priority_display) ~= "string" or #entry.priority_display > 160 then return false, "advisor_role_invalid" end
  if role == "tank" and entry.safety_first ~= "survival" then return false, "advisor_role_invalid" end
  if role == "healer" and entry.safety_first ~= "healing" then return false, "advisor_role_invalid" end
  if role == "damage" and entry.safety_first ~= "damage" then return false, "advisor_role_invalid" end
  return true, "validSyntheticAdvisorNonActionable"
end

DpsLabAdvisorSyntheticGuidance = { schema_version="0.1", synthetic=true, lifecycle={state="synthetic_fixture"}, safety={actionable=false,no_automation=true}, roles={ damage={statistic_target="synthetic_damage_stat",gear_priority="synthetic_gear_priority",priority_display="synthetic_damage_priority",safety_first="damage"}, tank={statistic_target="synthetic_tank_stat",gear_priority="synthetic_survival_priority",priority_display="synthetic_tank_priority",safety_first="survival"}, healer={statistic_target="synthetic_healer_stat",gear_priority="synthetic_healing_priority",priority_display="synthetic_healer_priority",safety_first="healing"} } }
DpsLabAdvisorGuidance = Guidance
