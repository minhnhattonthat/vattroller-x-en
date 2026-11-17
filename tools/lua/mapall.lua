-- mapall.lua: world map (game mode 9) with every story flag set (64 bytes at *(0x03002AA0)+0x4EC, cond type 1),
-- so nine of the ten place labels show (G15; all but Kaiten Island). mapkaiten.lua shows Kaiten Island.
local M = emu.memType.gbaMemory
L.on_frame(function()
  local base = emu.read32(0x03002AA0, M) + 0x4EC
  for k = 0, 63 do emu.write(base + k, 0xFF, M) end
end)
