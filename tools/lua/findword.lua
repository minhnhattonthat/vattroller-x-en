-- findword.lua: at frame AT_FRAME (default: every 600 frames), log every 4-byte-aligned EWRAM/IWRAM address
-- holding the 32-bit value WORD (e.g. a ROM string pointer, to find a table's RAM copy).
--   warp.py SCENE --script tools/lua/findword.lua --var WORD=0x08076A80
local M = emu.memType.gbaMemory
local word = assert(WORD, "WORD")
local done = {}
local function scan(lo, hi)
  for a = lo, hi - 4, 4 do
    if emu.read32(a, M) == word and not done[a] then
      done[a] = true
      L.log(string.format("f%d FOUND %08X at %08X", L.frame, word, a))
    end
  end
end
L.on_frame(function()
  if (AT_FRAME and L.frame == AT_FRAME) or (not AT_FRAME and L.frame % 600 == 0) then
    scan(0x02000000, 0x02040000)
    scan(0x03000000, 0x03008000)
  end
end)
