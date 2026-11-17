-- idsweep.lua: make a detail page show every record of a table, for text coverage (textcover.lua logs the reads).
-- Presses KEY every EVERY frames so the page redraws; at the redraw's id load (exec HOOK) the id byte at
-- *(PTR)+OFF is overwritten with the next id 0..N-1. Logs "IDSWEEP i f<frame>" and "IDSWEEP DONE".
--   emu.py BUILD --state-in work/states/menu_armdata.mss --script tools/lua/idsweep.lua \
--     --var HOOK=0x0804D2E0 --var PTR=0x03002BF4 --var OFF=0x4D --var N=134 --var "KEY='right'" \
--     --script $SKILL/scripts/lua/probes/textcover.lua --var "RANGES='8000000-91CBFC0'"
-- Arm Data (menu_armdata): HOOK 0x0804D2E0 (ldrb r1,[r0,#1] with r0 = *0x03002BF4 + 0x4C), record = *0x02009D58 + id*0x78.
-- V Skills (menu_vskills): HOOK 0x0802DEF8 PTR 0x03002A90 OFF 0x73 FILL 5 (the 5 equipped slots, signed ids),
--   KEY 'down'; record = *0x02009D48 + id*0x28 (desc lines), names list at ROM 0x7890.
-- FILL=k: write the id into k bytes from OFF (every slot of a list). SHOT=1: a shot WAIT frames after each press.
local M = emu.memType.gbaMemory
local every, wait, n, key = EVERY or 40, WAIT or 30, assert(N, "N"), KEY or "right"
local i, pending, start = -1, false, START or 30
L.on_exec(HOOK, HOOK, function()
  if not pending then return end
  pending = false
  local base = emu.read32(PTR, M)
  local id = i + (FIRST or 0)
  for k = 0, (FILL or 1) - 1 do emu.write(base + OFF + k, id, M) end
  L.log(string.format("IDSWEEP %d f%d", id, L.frame))
end)
L.on_frame(function(f)
  if f < start or (f - start) % every ~= 0 then
    if SHOT and i >= 0 and (f - start) % every == wait then L.shot(string.format("id%03d.png", i)) end
    return
  end
  i = i + 1
  if i >= n then
    L.log(string.format("IDSWEEP DONE f%d", f))
    L.finish(0)
    return
  end
  pending = true
  L.press(key, 2)
end)
