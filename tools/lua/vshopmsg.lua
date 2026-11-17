-- vshopmsg.lua: on the PC menu's Password screen (tick 0x0804EDC4), show the V Shop unlock messages
-- "<item> now sold / at the V Shop!!" (table *0x02009D94 = ROM 0x1D5F0, records 0x14, +0xC/+0x10 = the two
-- lines, r01d900..; docs/re/debug.md §PC menu) for text coverage. The screen keeps a struct at *(0x03003648):
-- state byte +0x29 (table ROM 0xEEE18, 16 states), record index s8 +0x2A. State 0xA (0x0804FE58) prints line
-- +0xC and goes to 0xB; 0xB (0x0804FE9C) prints +0x10 and goes to 0xC (wait for A). State 9 (0x0804FE3C) opens
-- the message box first (0xA waits on it). This probe waits for warp phase "hold", forces state 9 with index i,
-- and once the screen has left states 9-0xC moves to i+1. Open the screen with pcmenu.lua:
--   warp.py rpg_town --script tools/lua/pcmenu.lua --script tools/lua/vshopmsg.lua \
--     --set "post=60 -;8 down;8 -;8 down;8 -;8 down;8 -;8 a;120 -" --set hold=4000 --set frames=20000 \
--     --script $SKILL/scripts/lua/probes/textcover.lua --var "RANGES='8000000-91CBFC0'"
-- N (default 38) records from FIRST (0); SHOT=1 saves id###.png at each step; A is pressed every PAGE (30) frames.
local M = emu.memType.gbaMemory
local n, i = N or 38, FIRST or 0
local started = false
local last, shot, t12 = -1, false, 0
L.on_frame(function(f)
  if WARP_PHASE ~= "hold" and not started then return end
  local st = emu.read32(0x03003648, M)
  if st < 0x02000000 or st >= 0x04000000 then return end
  local state = emu.read(st + 0x29, M)
  if not started then
    started = true
    emu.write(st + 0x2A, i, M)
    emu.write(st + 0x29, 9, M)
    L.log(string.format("VSU %d f%d (state was %d)", i, f, state))
    return
  end
  if f % (PAGE or 30) == 0 then L.press("a", 6) end   -- page the message box
  if state ~= last then L.log(string.format("VSU state %d (rec %d) f%d", state, i, f)) end
  if state == 0xC and last ~= 0xC then t12 = f end
  if state == 0xC and SHOT and not shot and f - t12 >= (WAIT or 40) then shot = true; L.shot(string.format("id%03d.png", i)) end
  last = state
  if state < 9 or state > 0xC then
    i = i + 1
    shot = false
    if i >= n then L.log("VSU DONE"); L.finish(0); return end
    emu.write(st + 0x2A, i, M)
    emu.write(st + 0x29, 9, M)
  end
end)
