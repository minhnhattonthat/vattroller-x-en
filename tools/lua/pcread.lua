-- pcread.lua: log the PC (and r0-r7, sp, lr) of the first N reads of a ROM range by CPU address.
--   warp.py SCENE --script tools/lua/pcread.lua --var LO=0x0881AA00 --var HI=0x0881AA03 [--var N=8]
-- romreads.lua keys its stats by pc and logged nothing for some text reads; this one logs the raw state.
local n, max = 0, N or 8
local function hook(addr, value)
  if n >= max then return end
  n = n + 1
  local s = emu.getState()
  local regs = {}
  for k = 0, 7 do regs[#regs + 1] = string.format("r%d=%08X", k, s["cpu.r" .. k] or 0) end
  L.log(string.format("PCREAD f%d addr=%08X pc=%08X lr=%08X sp=%08X %s", L.frame, addr, s["cpu.r15"] or 0,
    s["cpu.r14"] or 0, s["cpu.r13"] or 0, table.concat(regs, " ")))
end
emu.addMemoryCallback(L.safe(hook), emu.callbackType.read, assert(LO), assert(HI), emu.cpuType.gba,
  emu.memType.gbaMemory)
