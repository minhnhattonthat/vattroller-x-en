-- readlr.lua: like the skill's watch.lua (read mode), but logs the registers (lr, r0-r4) too, once per distinct
-- (pc, lr): finds the caller of a shared copy routine (e.g. IWRAM memcpy at 0x030023C2) for a source range.
--   warp.py SCENE --script tools/lua/readlr.lua --var WATCH_LO=0x08261A90 --var WATCH_HI=0x08262930
local lo, hi = assert(WATCH_LO, "WATCH_LO"), WATCH_HI or WATCH_LO
local seen = {}
L.on_read(lo, hi, function(addr)
  local s = emu.getState()
  local key = string.format("%08X/%08X", s["cpu.r15"] or 0, s["cpu.r14"] or 0)
  if seen[key] then return end
  seen[key] = true
  L.log(string.format("f%d READ addr=%08X pc=%08X lr=%08X r0=%08X r1=%08X r2=%08X r3=%08X r4=%08X", L.frame, addr,
    s["cpu.r15"] or 0, s["cpu.r14"] or 0, s["cpu.r0"] or 0, s["cpu.r1"] or 0, s["cpu.r2"] or 0, s["cpu.r3"] or 0,
    s["cpu.r4"] or 0))
end)
