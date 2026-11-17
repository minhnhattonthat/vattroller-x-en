-- mapkaiten.lua: with mapall.lua, also sets 8 bytes at *(0x03002A90)+0x1E0 (cond type 2/4 flags): the world map
-- then shows the Kaiten Island label (and hides most others: a late-story map state). G15 check only.
local M = emu.memType.gbaMemory
L.on_frame(function()
  local base = emu.read32(0x03002A90, M) + 0x1E0
  for k = 0, 7 do emu.write(base + k, 0xFF, M) end
end)
