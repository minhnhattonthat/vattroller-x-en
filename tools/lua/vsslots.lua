-- vsslots.lua: the V Skills page lists the 5 equipped skill slots (signed bytes at *(0x03002A90)+0x73..+0x77,
-- read by 0x0802DEE8); its rows draw each record's +0 name (V Skill table ROM 0x7890, 128 records). This holds
-- the slots at ids 5g..5g+4 and moves to the next group g on each B press (KEYINPUT bit 1 edge), so a route that
-- reopens the page with B, A shows every name: scene vskills_names. FIRST (default 0) / LAST (default 127).
local M = emu.memType.gbaMemory
local first, last = FIRST or 0, LAST or 127
local g, was = 0, false
L.on_frame(function()
  local keys = emu.read16(0x04000130, M)
  local b = (keys & 2) == 0
  if WARP_PHASE ~= "post" then b = false end  -- count only presses of the scene's post route (warp.lua global)
  if b and not was then g = g + 1 end
  was = b
  local p = emu.read32(0x03002A90, M)
  if p < 0x02000000 or p >= 0x04000000 then return end
  for k = 0, 4 do
    local id = first + g * 5 + k
    if id > last then id = last end
    emu.write(p + 0x73 + k, id, M)
  end
end)
