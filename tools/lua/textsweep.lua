-- textsweep.lua: run listed event commands (text lines, choices, chapter titles) through the game's own script
-- interpreter, one after another, so every line is drawn once (text coverage for textcover.py, sampled shots).
-- At the interpreter step entry 0x08030B40 (reads command pointer 0x030063F4; wait callback 0x030063EC), when no
-- wait is pending and the pointer is not the node in hand, the pointer is set to the next listed node.
--   emu.py BUILD --state-in work/states/comic_jin1.mss --mash 8 --script tools/lua/textsweep.lua \
--     --var "LIST='work/qa/sweep/nodes_00.txt'" [--var SHOT=1]  (+ textcover.lua for the log)
-- LIST: one hex CPU address per line (node start). Logs "SWEEP i addr f<frame>" and "SWEEP DONE".
-- SHOT=1: a shot WAIT frames (default 40) after each redirect. STALL (default 900): frames before a command that
-- never finishes is logged ("SWEEP STALL") and skipped.
local M = emu.memType.gbaMemory
local list = {}
for line in io.lines(LIST) do
  local h = line:match("^(%x+)")
  if h then list[#list + 1] = tonumber(h, 16) end
end
local i, target, start, wait, shot_at = 0, nil, START or 0, WAIT or 40, nil
local stall, last = STALL or 900, 0
local function take()
  i = i + 1
  if i > #list then
    L.log(string.format("SWEEP DONE f%d", L.frame))
    return
  end
  target = list[i]
  emu.write32(0x030063F4, target, M)
  shot_at, last = L.frame + wait, L.frame
  L.log(string.format("SWEEP %d %X f%d", i, target, L.frame))
end
L.on_exec(0x08030B40, 0x08030B40, function()
  if L.frame < start or i > #list then return end
  if emu.read32(0x030063EC, M) ~= 0 then return end
  if emu.read32(0x030063F4, M) == target then return end
  take()
end)
-- watchdog: a command that never finishes (STALL frames) is logged and skipped, its wait callback cleared
L.on_frame(function(f)
  if target and i <= #list and f - last > stall then
    L.log(string.format("SWEEP STALL %d %X f%d", i, target, f))
    emu.write32(0x030063EC, 0, M)
    take()
  end
end)
if SHOT then
  L.on_frame(function(f)
    if shot_at and f == shot_at then L.shot(string.format("n%05d.png", i)) end
  end)
end
