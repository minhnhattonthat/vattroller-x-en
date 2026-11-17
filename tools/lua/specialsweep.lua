-- specialsweep.lua: draw every special move (ROM 0x160D0, 36 records: 5 name parts + 4 desc lines) in the Arm Data
-- device's Special box, for text coverage. The box (0x0804B0B4, state *0x03002D50, cursor s16 +0x36) draws a
-- special only on a combo slot (cursor >= 2) whose special byte (0x08051474) is >= 0; the special id is the byte
-- read at 0x080534D8 (combo table *0x02009D60). Each up/down press redraws the box: the probe sets the cursor to
-- 2 for the draw, forces the "has a special" test and the id, then restores the cursor.
--   emu.py BUILD --state-in work/states/menu_armdata.mss --script tools/lua/specialsweep.lua [--var N=36]
--     [--var LEVEL=k] --script $SKILL/scripts/lua/probes/textcover.lua --var "RANGES='8000000-91CBFC0'"
-- LEVEL=k: also force the name-part byte (state +0x14..) to k (see docs/re/debug.md §Special moves).
local M = emu.memType.gbaMemory
local n, every, start = N or 36, EVERY or 40, START or 30
local i, pending, saved = -1, false, nil
local function setreg(r, v) local s = emu.getState(); s["cpu.r" .. r] = v; emu.setState(s) end
L.on_exec(0x0804B0B4, 0x0804B0B4, function()
  if not pending then return end
  local b = emu.read32(0x03002D50, M)
  saved = emu.read16(b + 0x36, M)
  emu.write16(b + 0x36, 2, M)
end)
L.on_exec(0x0804B18A, 0x0804B18A, function() if pending then setreg(0, 0) end end)
L.on_exec(0x080534DA, 0x080534DA, function()
  if not pending then return end
  setreg(1, i)
  L.log(string.format("IDSWEEP %d f%d", i, L.frame))
end)
local function restore()
  if saved then emu.write16(emu.read32(0x03002D50, M) + 0x36, saved, M); saved = nil end
  pending = false
end
L.on_exec(0x0804B1D0, 0x0804B1D0, restore)
L.on_exec(0x0804B1F4, 0x0804B1F4, restore)
L.on_frame(function(f)
  if f < start or (f - start) % every ~= 0 then
    if SHOT and i >= 0 and (f - start) % every == every - 4 then L.shot(string.format("id%03d.png", i)) end
    return
  end
  i = i + 1
  if i >= n then L.log(string.format("IDSWEEP DONE f%d", f)); L.finish(0); return end
  pending = true
  L.press(i % 2 == 0 and "down" or "up", 2)
end)
