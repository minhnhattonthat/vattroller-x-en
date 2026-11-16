-- Log every event-script command the interpreter dispatches (0x08030B80: r2 = command pointer):
-- "f<frame> op<op> @<addr> <first 16 bytes hex>". Skips text ops 0x00 unless TEXT=1.
--   emu.py ... --script tools/lua/oplog.lua [--var FROM=0 --var MAX=3000 --var TEXT=1]
local from, max, n = FROM or 0, MAX or 3000, 0
L.on_exec(0x08030B80, 0x08030B80, function()
  if L.frame < from or n >= max then return end
  local p = emu.getState()["cpu.r2"]
  local op = emu.read(p, emu.memType.gbaMemory)
  if op == 0 and not TEXT then return end
  n = n + 1
  local size = emu.read16(p + 2, emu.memType.gbaMemory)
  local t = {}
  for i = 4, math.min(size, 24) - 1 do t[#t + 1] = string.format("%02X", emu.read(p + i, emu.memType.gbaMemory)) end
  L.log(string.format("f%d op%02X sz%d @%08X %s", L.frame, op, size, p, table.concat(t)))
end)
