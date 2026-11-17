-- setbytes.lua: hold N bytes at *(PTR)+OFF (or at ADDR when PTR is unset) to VAL on every frame from FROM on,
-- e.g. every owned bit of a list, so a page opened afterwards lists every record (text coverage).
--   emu.py BUILD --state-in work/states/menu_vskills.mss --route r.txt --script tools/lua/setbytes.lua \
--     --var PTR=0x03002AA0 --var OFF=0x53C --var N=16   # all 128 V Skills owned; reopen the page in the route
local M = emu.memType.gbaMemory
-- SB_N overrides N when another probe in the same run also reads N (e.g. shopall.lua PROFILE=1).
local n, val, from = assert(SB_N or N, "N"), VAL or 0xFF, FROM or 0
-- UNTIL: last frame to write (default: hold forever), e.g. FROM=250 UNTIL=250 pokes a state byte once.
L.on_frame(function(f)
  if f < from or (UNTIL and f > UNTIL) then return end
  local base = PTR and (emu.read32(PTR, M) + (OFF or 0)) or assert(ADDR, "PTR or ADDR")
  for k = 0, n - 1 do emu.write(base + k, val, M) end
end)
