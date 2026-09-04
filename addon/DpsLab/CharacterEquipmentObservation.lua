local Equipment = {}
local function api() return { GetBuildInfo=GetBuildInfo,UnitClass=UnitClass,GetSpecialization=GetSpecialization,GetSpecializationInfo=GetSpecializationInfo,UnitLevel=UnitLevel,UnitRace=UnitRace,GetInventoryItemLink=GetInventoryItemLink,C_Container=C_Container } end
local function num(v,a,b) return type(v)=="number" and v==math.floor(v) and v>=a and v<=b and v or nil end
local function esc(v) return v:gsub('\\','\\\\'):gsub('"','\\"') end
local function item(link,location,slot,source)
 if type(link)~="string" or #link<1 or #link>2048 then return nil end
 local id=tonumber(link:match("item:(%d+)")); if not num(id,1,9999999) then return nil end
 return '{"item_id":'..id..',"item_level":1,"item_link":"'..esc(link)..'","location":'..location..',"slot":"'..slot..'","source":"'..source..'"}'
end
function Equipment.Capture(bag, injected)
 local a=injected or api(); if type(a.GetBuildInfo)~="function" or type(a.UnitClass)~="function" or type(a.GetSpecialization)~="function" or type(a.GetSpecializationInfo)~="function" or type(a.UnitLevel)~="function" or type(a.UnitRace)~="function" then return nil,"analysis_api_unavailable" end
 local ok,_,build,_,interface=pcall(a.GetBuildInfo); local cok,_,_,class=pcall(a.UnitClass,"player"); local sok,index=pcall(a.GetSpecialization); local lok,level=pcall(a.UnitLevel,"player"); local rok,_,_,race=pcall(a.UnitRace,"player")
 if not(ok and cok and sok and lok and rok) then return nil,"analysis_api_failed" end
 local iok,spec,_,_,_,role=pcall(a.GetSpecializationInfo,index); if not iok then return nil,"analysis_api_failed" end
 local roles={DAMAGER="damage",TANK="tank",HEALER="healer"}; if not(num(build,1,9999999) and num(interface,1,9999999) and num(class,1,1000) and num(spec,1,100000) and num(level,1,1000) and num(race,1,1000) and roles[role]) then return nil,"analysis_context_invalid" end
 local equipped={}; for slot=1,19 do local entry=item(a.GetInventoryItemLink("player",slot),slot,"slot_"..slot,"equipped"); if entry then equipped[#equipped+1]=entry end end
 if #equipped==0 then return nil,"analysis_items_unavailable" end
 local entries={}; if bag ~= nil then
  bag=num(bag,0,4); if bag==nil then return nil,"analysis_bag_invalid" end
  if not(a.C_Container and type(a.C_Container.GetContainerNumSlots)=="function" and type(a.C_Container.GetContainerItemLink)=="function") then return nil,"analysis_api_unavailable" end
  local count=a.C_Container.GetContainerNumSlots(bag); if not num(count,0,40) then return nil,"analysis_bag_invalid" end
  for pos=1,count do local entry=item(a.C_Container.GetContainerItemLink(bag,pos),pos,"bag_"..pos,"designated_bag"); if entry then entries[#entries+1]=entry end end
 end
 local text='{"compatibility":{"build":'..build..',"interface_version":'..interface..',"wow_product":"retail"},"equipment":{"bag":['..table.concat(entries,',')..'],"equipped":['..table.concat(equipped,',')..']},"observation_type":"live_manual_analysis_export","safety":{"contains_direct_identifiers":false,"executable":false,"no_automation":true},"schema_version":"0.1","subject":{"class_id":'..class..',"level":'..level..',"race_id":'..race..',"role":"'..roles[role]..'","specialization_id":'..spec..'}}\n'
 if #text>65536 then return nil,"analysis_payload_invalid" end; return "DPSLAB-LIVE-ANALYSIS-0.1\n"..text,"analysis_export_ready"
end
DpsLabCharacterEquipmentObservation=Equipment
