-- Log calls to the archive lookup get_file_ptr(r0 = index) at 0x0802E980 and get_file_size at 0x0802E990,
-- with the caller (lr). Usage: emu.py ... --script tools/lua/getfile.lua [--var LO=2475 --var HI=2713]
local lo, hi = LO or 0, HI or 99999
local function reg(s, n) return s["cpu.r" .. n] or s["cpu.r[" .. n .. "]"] or -1 end
local dumped = false
local function hook(name)
  return function()
    local s = emu.getState()
    if not dumped then
      dumped = true
      local ks = {}
      for k in pairs(s) do if k:match("^cpu%.") then ks[#ks + 1] = k end end
      table.sort(ks); L.log("keys: " .. table.concat(ks, " "))
    end
    local r0 = reg(s, 0)
    if r0 >= lo and r0 <= hi then
      L.log(string.format("f%d %s #%d lr=%08X", L.frame, name, r0, reg(s, 14)))
    end
  end
end
L.on_exec(0x0802E980, 0x0802E980, hook("ptr"))
