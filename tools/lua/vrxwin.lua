-- vrxwin.lua: force the VRX win screen at the end of a battle and draw every roster win quote there (text coverage).
-- The result step 0x08068F94 picks the DRAW screen when byte 0x03003557 == 1 (cmp at 0x08068FC2), else installs
-- the win handler 0x080693ED, which draws the winner's name and the "favourite word" (roster record +4, ROM 0xCE0
-- + id*0x58, copied at battle load to slot +0x8C; getter 0x0802DE6C returns at 0x0806943E, copy 0x08028714 (8
-- bytes), draw 0x08073064 returns at 0x08069458). This script sets r0 = 0 at the cmp (win), and at 0x0806943E
-- points r0 at record id's +4 string; at 0x08069458 it jumps back to 0x0806943E for the next id (N ids from FIRST,
-- logs "VRXWIN i"), so one win screen draws them all and leaves the last one shown.
--   warp.py vrx_fight --set "post=...;10500 -" --script tools/lua/vrxwin.lua --var N=95 \
--     --script $SKILL/scripts/lua/probes/textcover.lua --var "RANGES='8000000-91CBFC0'"
-- N=0: only force the win (the real winner's own word is drawn).
local M = emu.memType.gbaMemory
local n, first, i = N or 95, FIRST or 0, 0
local function setregs(t)
  local s = emu.getState()
  for k, v in pairs(t) do s[k] = v end
  emu.setState(s)
end
L.on_exec(0x08068FC2, 0x08068FC2, function()
  local s = emu.getState()
  if s["cpu.r0"] == 1 then
    setregs({ ["cpu.r0"] = 0 })
    L.log(string.format("VRXWIN forced f%d", L.frame))
  end
end)
L.on_exec(0x0806943E, 0x0806943E, function()
  if i >= n then return end
  local id = first + i
  setregs({ ["cpu.r0"] = emu.read32(0x08000CE4 + id * 0x58, M) })
  L.log(string.format("VRXWIN %d f%d", id, L.frame))
end)
L.on_exec(0x08069458, 0x08069458, function()
  if i >= n then return end
  i = i + 1
  if i >= n then L.log("VRXWIN DONE") return end
  setregs({ ["cpu.r15"] = 0x0806943E, ["cpu.pipeline.reloadRequested"] = true })
end)
