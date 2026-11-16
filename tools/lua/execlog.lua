-- Log r0-r3 and lr at each execution of one or more addresses.
--   emu.py ... --script tools/lua/execlog.lua --var "ADDRS={0x0802FF34,0x0802E980}" [--var FROM=0 --var MAX=500]
local from, max, n = FROM or 0, MAX or 500, 0
for _, a in ipairs(assert(ADDRS, "set --var ADDRS={0x...}")) do
  L.on_exec(a, a, function()
    if L.frame < from or n >= max then return end
    n = n + 1
    local s = emu.getState()
    L.log(string.format("f%d @%08X r0=%X r1=%X r2=%X r3=%X lr=%08X", L.frame, a,
      s["cpu.r0"], s["cpu.r1"], s["cpu.r2"], s["cpu.r3"], s["cpu.r14"]))
  end)
end
