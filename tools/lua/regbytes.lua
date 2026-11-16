-- At each execution of PC, log register REG (default 0) and N bytes at the address it holds (first MAX hits).
--   emu.py/warp.py ... --script tools/lua/regbytes.lua --var PC=0x08072FAE [--var REG=0 --var N=16 --var MAX=20]
local pc, reg, n, max = assert(PC), REG or 0, N or 16, MAX or 20
local hits = 0
L.on_exec(pc, pc, function()
  if hits >= max then return end
  hits = hits + 1
  local s = emu.getState()
  local a = s["cpu.r" .. reg]
  local b = {}
  for i = 0, n - 1 do b[#b + 1] = string.format("%02X", emu.read(a + i, emu.memType.gbaMemory)) end
  L.log(string.format("f%d pc=%08X r%d=%08X %s", L.frame, pc, reg, a, table.concat(b, " ")))
end)
