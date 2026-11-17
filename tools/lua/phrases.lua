-- phrases.lua: on the text-entry screen (the PC menu's Password screen; struct *(0x03003648), state +0x29,
-- mode +0x20, list +0x2C, buffer +0xC (10 bytes)), confirming an entry the checker 0x080501CC rejects fills
-- the field with a default phrase: 0x0804EE4C(list 1-8) = table EWRAM 0x0200B628.. (r077ac4-r077bf0: default
-- names, win quotes, greetings, favourite words), entry = rand() mod k via 0x08020BD4. Mode 5 (password) prints
-- "Password error!" instead. This probe sets mode MODE (0), list n and forces entry j (the modulo result at
-- the picker's call sites), restores the empty buffer, presses START (cursor to END) + A, and shoots.
--   warp.py rpg_town --script tools/lua/pcmenu.lua --script tools/lua/phrases.lua \
--     --set "post=60 -;8 down;8 -;8 down;8 -;8 down;8 -;8 a;120 -" --set hold=9000 --set frames=26000
local M = emu.memType.gbaMemory
local J = 0
-- An exec hook on the hot modulo routine itself changes the run (the PC menu then ignores A), so hook the
-- return points of its 8 calls inside the picker and replace the result there.
local armed = false
for _, pc in ipairs({ 0x0804EE94, 0x0804EEAC, 0x0804EEC4, 0x0804EEDC, 0x0804EEF4, 0x0804EF0C, 0x0804EF24,
                      0x0804EF3C }) do
  if not NOHOOK then L.on_exec(pc, pc, function()
    if not armed then return end
    local s = emu.getState()
    s["cpu.r0"] = J
    emu.setState(s)
  end) end
end
local KS = { 4, 3, 4, 5, 3, 3, 1, 3 }   -- entries per list 1-8 (tables 0xEED6C..0xEEDE0)
local n, j, t, step = 1, 0, 0, 0
local empty
L.on_frame(function(f)
  if DEBUG and f % 300 == 0 then L.log(string.format("PHRASE f%d phase %s st %08X", f, tostring(WARP_PHASE), emu.read32(0x03003648, M))) end
  if WARP_PHASE ~= "hold" and step == 0 then return end
  local st = emu.read32(0x03003648, M)
  if st < 0x02000000 or st >= 0x04000000 then
    if f % 60 == 0 then L.press("a", 6) end   -- the route's A can land while the PC menu still prints
    return
  end
  local state = emu.read(st + 0x29, M)
  if DEBUG and f % 600 == 0 then L.log(string.format("PHRASE tick f%d state %d step %d", f, state, step)) end
  if not empty then
    empty = {}
    for k = 0, 9 do empty[k] = emu.read(st + 0xC + k, M) end
    empty.len = emu.read(st + 0x23, M)
  end
  if step == 0 then
    if state ~= 6 then return end
    for k = 0, 9 do emu.write(st + 0xC + k, empty[k], M) end
    emu.write(st + 0x23, empty.len, M)
    emu.write(st + 0x20, MODE or 0, M)
    emu.write(st + 0x2C, n, M)
    J = j
    L.press("start", 6); L.press("-", 10); L.press("a", 6)
    step, t, armed = 1, f, true
  elseif f - t >= (WAIT or 50) then
    armed = false
    L.log(string.format("PHRASE list %d entry %d state %d f%d", n, j, state, f))
    if SHOT then L.shot(string.format("l%d_%d.png", n, j)) end
    j = j + 1
    if j >= KS[n] then n, j = n + 1, 0 end
    if n > 8 then L.log("PHRASE DONE"); L.finish(0); return end
    step = 0
  end
end)
