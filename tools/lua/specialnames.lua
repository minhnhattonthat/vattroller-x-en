-- specialnames.lua: draw every special-move name in the Arm Set screen's Special box, for text coverage.
-- The box (mode 15, scene md15; drawer 0x080517E0, called after the loadout fill 0x0805156C) shows three specials,
-- each "<Armalet form name> <name part>": state *(0x030051BC) +4/+8, +0xC/+0x10, +0x14/+0x18 hold the
-- (form, part) string pointers. Form = *0x02009D68 table (ROM 0x17A60, 48 = 16 Armalets x 3, r017b44..),
-- part = special record (*0x02009D64 = ROM 0x160D0, stride 0x38) +0..+0x10 (5 per special, chosen by the
-- Armalet record +0x20; 180, r0168b0..). At 0x0805186E (lengths, then layout and the six renders) this probe
-- writes the pointers of draw i; at the epilogue 0x08051A48 it sends the CPU back to 0x0805186E for the next
-- draw (sp is the same there), so one real call draws all N groups (logs "SPN i").
--   warp.py md15 --set mode=15 --set mode_arg=0 --script tools/lua/specialnames.lua \
--     --script $SKILL/scripts/lua/probes/textcover.lua --var "RANGES='8000000-91CBFC0'"
-- SHOT=1: no loop, the real draw shows group FIRST (for a zoomed shot of chosen names).
-- Group i: slot j (0-2) = part k = 3i+j (special k//5, part k%5), form (3i+j) % 48.
local M = emu.memType.gbaMemory
local n, i = N or 60, FIRST or 0
local function setregs(t)
  local s = emu.getState()
  for k, v in pairs(t) do s[k] = v end
  emu.setState(s)
end
local function fill(g)
  local st = emu.read32(0x030051BC, M)
  local sp, fm = emu.read32(0x02009D64, M), emu.read32(0x02009D68, M)
  local parts = {}
  for j = 0, 2 do
    local k = (3 * g + j) % 180
    local form = FORMS and FORMS[j + 1] or ((3 * g + j) % 48)
    local part = PARTS and PARTS[j + 1] or k
    emu.write32(st + 4 + j * 8, emu.read32(fm + form * 4, M), M)
    emu.write32(st + 8 + j * 8, emu.read32(sp + (part // 5) * 0x38 + (part % 5) * 4, M), M)
    parts[#parts + 1] = string.format("%d/%d", form, part)
  end
  L.log(string.format("SPN %d f%d %s", g, L.frame, table.concat(parts, " ")))
end
local done = false
L.on_exec(0x0805186E, 0x0805186E, function()
  if done then return end
  -- state +0 bits 0x200/0x400/0x800 (set by the fill when bits 0x30/0x50/0x60 are) make the separator cell of
  -- row 1/2/3 show tile 0xC8/0xD8/0xE8 instead of the separator 0xF8; an empty loadout sets them. NOFLAGS=1 clears.
  if NOFLAGS then
    local st = emu.read32(0x030051BC, M)
    emu.write32(st, emu.read32(st, M) & ~0xE00, M)
  end
  fill(i)
end)
L.on_exec(0x08051A48, 0x08051A48, function()
  if done then return end
  if SHOT then done = true return end
  i = i + 1
  if i >= n then done = true; L.log("SPN DONE") return end
  setregs({ ["cpu.r15"] = 0x0805186E, ["cpu.pipeline.reloadRequested"] = true })
end)
