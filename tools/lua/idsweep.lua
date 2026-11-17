-- idsweep.lua: make a detail page show every record of a table, for text coverage (textcover.lua logs the reads).
-- Presses KEY every EVERY frames so the page redraws; at the redraw's id load (exec HOOK) the id byte at
-- *(PTR)+OFF is overwritten with the next id 0..N-1. Logs "IDSWEEP i f<frame>" and "IDSWEEP DONE".
--   emu.py BUILD --state-in work/states/menu_armdata.mss --script tools/lua/idsweep.lua \
--     --var HOOK=0x0804D2E0 --var PTR=0x03002BF4 --var OFF=0x4D --var N=134 --var "KEY='right'" \
--     --script $SKILL/scripts/lua/probes/textcover.lua --var "RANGES='8000000-91CBFC0'"
-- Arm Data (menu_armdata): HOOK 0x0804D2E0 (ldrb r1,[r0,#1] with r0 = *0x03002BF4 + 0x4C), record = *0x02009D58 + id*0x78.
-- V Skills (menu_vskills): HOOK 0x0803FB8E REG 0 N 103 KEY 'down' OWN_PTR 0x03002AA0 OWN_OFF 0x53C OWN_N 16;
--   record = *0x02009D48 + id*0x28 (name + 5 desc lines).
-- REG=n: set register rn = id at HOOK instead of a RAM byte. OWN_*: fill an owned-bits field with 0xFF.
-- FILL=k: write the id into k bytes from OFF (every slot of a list). SHOT=1: a shot WAIT frames after each press.
local M = emu.memType.gbaMemory
local every, wait, n, key = EVERY or 40, WAIT or 30, assert(N, "N"), KEY or "right"
local i, pending, start = -1, false, START or 30
L.on_exec(HOOK, HOOK, function()
  if not pending and not (REG and i >= 0) then return end
  local id = i + (FIRST or 0)
  if REG then
    -- REG=n: the id is a register value at HOOK (e.g. a call's return), not a RAM byte; set it on every hit
    local s = emu.getState()
    s["cpu.r" .. REG] = id
    emu.setState(s)
    if pending then L.log(string.format("IDSWEEP %d f%d", id, L.frame)) end
    pending = false
    return
  end
  pending = false
  local base = emu.read32(PTR, M)
  for k = 0, (FILL or 1) - 1 do emu.write(base + OFF + k, id, M) end
  L.log(string.format("IDSWEEP %d f%d", id, L.frame))
end)
L.on_frame(function(f)
  if f < start or (f - start) % every ~= 0 then
    if SHOT and i >= 0 and (f - start) % every == wait then L.shot(string.format("id%03d.png", i)) end
    return
  end
  if OWN_PTR then
    -- OWN_PTR/OWN_OFF/OWN_N: set OWN_N bytes of an "owned" bitfield at *(OWN_PTR)+OWN_OFF to 0xFF before each
    -- press, so a page that blanks unowned records draws them all
    local b = emu.read32(OWN_PTR, M)
    for k = 0, OWN_N - 1 do emu.write(b + OWN_OFF + k, 0xFF, M) end
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
