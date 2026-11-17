-- shopall.lua: shop screens (warp scene field "mode": 10, docs/re/debug.md §Shops) with every VRX Data entry owned
-- and VP to spare. Save struct = *(0x03002AA0): +0x54C u32 bits = owned VRX Data (bit = record byte 1, test at
-- 0x0806B5FA), +0x584 u32 = VP (price compare at 0x0806B346). Set every frame from START (default 1).
-- PROFILE=1: id sweep of the VRX profile panel: at its draw call (0x0806A4C8, bl 0x0806A2F4 with r0 = roster id)
-- r0 is replaced by FIRST+i, i = 0..N-1, one per A press (A opens the panel from the VRX Data tab, B closes it):
-- every profile's lines are drawn for text coverage. Logs "PROFILE id f<frame>" and "PROFILE DONE".
local M = emu.memType.gbaMemory
local BITS = OWN_BYTES or 8
L.on_frame(function(f)
  if f < (START or 1) then return end
  local s = emu.read32(0x03002AA0, M)
  if s < 0x02000000 or s > 0x0203FFFF then return end
  for k = 0, BITS - 1 do emu.write(s + 0x54C + k, 0xFF, M) end
  emu.write32(s + 0x584, VP or 999999, M)
end)
if PROFILE then
  local i, n, first = 0, assert(N, "N"), FIRST or 0
  -- HOOK/REG: another detail draw in the same buy prompt, e.g. the Tools tab: HOOK=0x0806A484 REG=2 (str r2,[sp]:
  -- the item id passed to 0x0803F608); Arms tab: HOOK=0x0806A40E REG=3
  local hook, reg = HOOK or 0x0806A4C8, REG or 0
  L.on_exec(hook, hook, function()
    if i >= n then return end
    local st = emu.getState()
    st["cpu.r" .. reg] = first + i
    emu.setState(st)
    L.log(string.format("PROFILE %d f%d", first + i, L.frame))
    if SHOT then L.log("shot") end
    i = i + 1
    if i >= n then L.log("PROFILE DONE") end
  end)
end
