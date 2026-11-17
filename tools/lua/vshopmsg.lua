-- vshopmsg.lua: open the PC menu's Password screen (0x0804EDC4) from the Arm Set screen (game mode 15) and show
-- the V Shop unlock messages "<item> now sold / at the V Shop!!" (table *0x02009D94 = ROM 0x1D5F0, records 0x14,
-- +0xC/+0x10 = the two lines, r01d900..; docs/re/debug.md §V Shop unlock messages), for text coverage.
-- Mode 15's first state callback 0x080502C8 is sent to 0x0804EDC4 (same r0), which sets up the password machine:
-- struct *(0x03003648), state byte +0x29 (table ROM 0xEEE18, 16 states), record index s8 +0x2A. State 0xA
-- (0x0804FE58) prints line +0xC and goes to 0xB; 0xB (0x0804FE9C) prints +0x10 when the box is free. This probe
-- forces state 0xA with index i, and after state 0xB has printed (its exit 0x0804FED2..) moves to i+1.
--   warp.py md15 --set mode=15 --set mode_arg=0 --set "post=3000 a" --script tools/lua/vshopmsg.lua \
--     --script $SKILL/scripts/lua/probes/textcover.lua --var "RANGES='8000000-91CBFC0'"
-- OPEN_ONLY=1: just open the Password screen.  N (default 38) records from FIRST (0).
local M = emu.memType.gbaMemory
local n, i = N or 38, FIRST or 0
local opened, started = false, false
local function setregs(t)
  local s = emu.getState()
  for k, v in pairs(t) do s[k] = v end
  emu.setState(s)
end
L.on_exec(0x080502C8, 0x080502C8, function()
  if opened then return end
  opened = true
  L.log(string.format("VSU open f%d", L.frame))
  setregs({ ["cpu.r15"] = 0x0804EDC4, ["cpu.pipeline.reloadRequested"] = true })
end)
local last = -1
L.on_frame(function(f)
  if OPEN_ONLY or not opened then return end
  local st = emu.read32(0x03003648, M)
  if st < 0x02000000 or st >= 0x04000000 then return end
  local state = emu.read(st + 0x29, M)
  if not started and f > (START or 120) then
    started = true
    emu.write(st + 0x2A, i, M)
    emu.write(st + 0x29, 0xA, M)
    L.log(string.format("VSU %d f%d", i, f))
    return
  end
  if started and state ~= 0xA and state ~= 0xB and state ~= last then
    L.log(string.format("VSU state %d after %d f%d", state, i, f))
  end
  last = state
  if started and state ~= 0xA and state ~= 0xB then
    if SHOT then L.shot(string.format("id%03d.png", i)) end
    i = i + 1
    if i >= n then L.log("VSU DONE"); L.finish(0); return end
    emu.write(st + 0x2A, i, M)
    emu.write(st + 0x29, 0xA, M)
    L.log(string.format("VSU %d f%d", i, f))
  end
end)
