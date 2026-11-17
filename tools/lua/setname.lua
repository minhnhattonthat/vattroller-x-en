-- setname.lua: overwrite the player name (*(0x03002A90)+0x78, 12 bytes; docs/re/font.md) at frame AT (default 2),
-- to measure the speaker tag and any line that inserts the name (∴) with a chosen name.
--   emu.py ROM --state-in work/states/<scene>.mss --script tools/lua/setname.lua --var NAME='"827682768276827682768276"'
-- NAME: hex bytes (spaces ignored), up to 12; the rest is zero-filled. Default: ＷＷＷＷＷＷ (widest fullwidth letter).
local M = emu.memType.gbaMemory
local hex = (NAME or "827682768276827682768276"):gsub("%s", "")
local at = AT or 2
L.on_frame(function(f)
  if f ~= at then return end
  local base = emu.read32(0x03002A90, M) + 0x78
  for i = 0, 11 do
    local b = tonumber(hex:sub(i * 2 + 1, i * 2 + 2), 16) or 0
    emu.write(base + i, b, M)
  end
  L.log(string.format("f%d name@%08X set to %s", f, base, hex))
end)
