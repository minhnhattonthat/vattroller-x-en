-- namebuf.lua: log the player name buffer (*(0x03002A90)+0x78, 12 bytes; docs/re/font.md) every 60 frames.
-- python -X utf8 $SKILL/scripts/emu.py ROM --out DIR --state-in work/states/<scene>.mss --frames 120 --script tools/lua/namebuf.lua
local M = emu.memType.gbaMemory
local n = 0
emu.addEventCallback(function()
  n = n + 1
  if n % 60 ~= 0 then return end
  local base = emu.read32(0x03002A90, M) + 0x78
  local s = ""
  for i = 0, 15 do s = s .. string.format("%02X ", emu.read(base + i, M)) end
  L.log(string.format("f%d name@%08X: %s", n, base, s))
end, emu.eventType.endFrame)
