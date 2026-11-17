-- keyall.lua: own every Key Item (13 items, names at ROM 0xEEBD8: bit i of the word at *(0x03002A90)+0x1E0, tested by the list drawer
-- 0x080410BC before it reads the name table copy at EWRAM 0x0200B494; unowned items show "??????????").
-- Scene key_items_all: menu_keyitems + this script + a cursor walk, so every name and description is drawn.
local M = emu.memType.gbaMemory
local bits = KEYBITS or 0x1FFF
L.on_frame(function()
  local p = emu.read32(0x03002A90, M)
  if p >= 0x02000000 and p < 0x04000000 then
    local a = p + 0x1E0
    local v = emu.read32(a, M)
    if (v & bits) ~= bits then emu.write32(a, v | bits, M) end
  end
end)
