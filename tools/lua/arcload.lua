-- Log archive file loads: every read of the archive table at 0x08100000 (2714 x (ptr,size)).
--   emu.py ... --script tools/lua/arcload.lua [--var FROM=0 --var TO=99999]
-- Logs "f<frame> load #<index> pc=<pc>" once per (index, frame).
local from, to = FROM or 0, TO or math.huge
local last = {}
L.on_read(0x08100000, 0x081054CF, function(addr)
  if L.frame < from or L.frame > to then return end
  local idx = (addr - 0x08100000) // 8
  local key = idx
  if last[key] == L.frame then return end
  last[key] = L.frame
  L.log(string.format("f%d load #%d pc=%08X", L.frame, idx, L.pc()))
end)
