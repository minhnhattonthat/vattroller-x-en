-- roomnames.lua: draw every room name through the room-name banner 0x08036678(room), for text coverage.
-- The banner (called from the room loader at 0x0803602C when *(0x03003070+0x1684) != 0) loads
-- r4 = *0x02009D54 + room*0x28 (ROM 0xBC20 table, 236 records, +0 = name pointer) and draws the name with
-- 0x080282B8 (ldr r1,[r4] at 0x080366A4). At the return of that draw (0x080366AE) this sweep points r4 at the
-- next record and sends the CPU back to 0x0803669A, so one banner call draws all N names (logs "ROOM i").
--   warp.py menu_field --script tools/lua/roomnames.lua --script $SKILL/scripts/lua/probes/textcover.lua ...
-- SHOT=1: no loop; each real banner call draws the next id instead (slow, one per room load).
local M = emu.memType.gbaMemory
local n, i = N or 236, FIRST or 0
local function setregs(t)
  local s = emu.getState()
  for k, v in pairs(t) do s[k] = v end
  emu.setState(s)
end
-- 0x080282B8 queues the text into a slot table *(0x030028C0+0x10): +0xC0 = lines (max 7), +0xC1 = glyphs
-- (max 0x40); both are restored to their first-call values before every looped draw, or it bails after ~5.
local q, c0, c1
L.on_exec(0x080366A4, 0x080366A4, function()
  if i >= n then return end
  q = q or emu.read32(0x030028D0, M)
  if c0 == nil then c0, c1 = emu.read(q + 0xC0, M), emu.read(q + 0xC1, M) end
  emu.write(q + 0xC0, c0, M)
  emu.write(q + 0xC1, c1, M)
  setregs({ ["cpu.r4"] = emu.read32(0x02009D54, M) + i * 0x28 })
  L.log(string.format("ROOM %d f%d", i, L.frame))
end)
if DEBUG then
  L.on_exec(0x080366A6, 0x080366A6, function()
    local s = emu.getState()
    L.log(string.format("ROOMDBG r1=%08X r4=%08X r0=%08X", s["cpu.r1"], s["cpu.r4"], s["cpu.r0"]))
  end)
end
L.on_exec(0x080366AE, 0x080366AE, function()
  if SHOT then i = i + 1 return end
  i = i + 1
  if i >= n then L.log("ROOM DONE") return end
  -- a jump needs the pipeline refilled from r15 (Mesen GBA: reloadRequested)
  setregs({ ["cpu.r15"] = 0x0803669A, ["cpu.pipeline.reloadRequested"] = true })
end)
