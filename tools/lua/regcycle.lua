-- regcycle.lua: at every exec of HOOK set register rREG to BASE + (k mod N), k = hit count, so a list or page
-- that loads an id there draws a different record on each call (text coverage with textcover.lua).
--   warp.py shop_vrxdata --script tools/lua/regcycle.lua --var HOOK=0x0806B102 --var REG=2 --var BASE=0x5F --var N=20
-- Shop VRX Data tab: the item-name getter 0x0806B0BC, type 3, compares the id (r2) with the roster count at
-- 0x0806B102; ids >= 0x5F index the VRX stage-name table (EWRAM 0x0200C618), so BASE=0x5F N=20 = the 20 stages.
-- START: first frame to act (default 0). Logs "REGCYCLE id f<frame>" for the first N hits.
local k, start = 0, START or 0
L.on_exec(HOOK, HOOK, function()
  if L.frame < start then return end
  local id = (BASE or 0) + (k % N)
  local s = emu.getState()
  s["cpu.r" .. REG] = id
  emu.setState(s)
  if k < N then L.log(string.format("REGCYCLE %d f%d", id, L.frame)) end
  k = k + 1
end)
