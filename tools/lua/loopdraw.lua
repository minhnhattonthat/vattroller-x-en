-- loopdraw.lua: replay one draw call N times with a different index each time (text coverage of a lookup table
-- drawn once per screen). At SET_AT set rREG = BASE + i; at BACK_AT (the instruction after the draw call) jump
-- to LOOP_FROM (the start of the draw's argument setup) until i reaches N. Logs "LOOPDRAW i f<frame>" and
-- "LOOPDRAW DONE". (Not FROM: setbytes.lua reads FROM as a frame number in the same run.)
--   warp.py menu_armalet --script tools/lua/loopdraw.lua --var LOOP_FROM=0x0804E8D6 --var SET_AT=0x0804E8DC \
--     --var BACK_AT=0x0804E8EA --var REG=1 --var N=16      # Armalet Size numbers 0-15 (table EWRAM 0x0200B1A4)
local i, n, base = 0, assert(N, "N"), BASE or 0
local function set(t)
  local s = emu.getState()
  for k, v in pairs(t) do s[k] = v end
  emu.setState(s)
end
L.on_exec(SET_AT, SET_AT, function()
  if i >= n then return end
  set({ ["cpu.r" .. REG] = base + i })
  L.log(string.format("LOOPDRAW %d f%d", base + i, L.frame))
end)
L.on_exec(BACK_AT, BACK_AT, function()
  if i >= n then return end
  i = i + 1
  if i >= n then L.log("LOOPDRAW DONE") return end
  set({ ["cpu.r15"] = LOOP_FROM, ["cpu.pipeline.reloadRequested"] = true })
end)
