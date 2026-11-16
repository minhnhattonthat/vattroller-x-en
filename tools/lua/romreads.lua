-- Log reads of a ROM range per (pc): lowest/highest address and count, flushed every 60 frames and at the end.
-- Also with SEQ=1 logs every read "f<frame> pc addr value" (up to MAX lines).
--   emu.py ... --script tools/lua/romreads.lua --var LO=0x08751BE0 --var HI=0x08753283 [--var SEQ=1 --var MAX=4000]
local lo, hi, seq, max = assert(LO), assert(HI), SEQ, MAX or 4000
local stat, n = {}, 0
L.on_read(lo, hi, function(addr, value)
  local pc = L.pc()
  local s = stat[pc]
  if not s then s = { lo = addr, hi = addr, n = 0, f = L.frame }; stat[pc] = s end
  if addr < s.lo then s.lo = addr end
  if addr > s.hi then s.hi = addr end
  s.n = s.n + 1
  if seq and n < max then n = n + 1; L.log(string.format("f%d pc=%08X a=%08X v=%X", L.frame, pc, addr, value or -1)) end
end)
L.on_frame(function(f)
  if f % 600 == 0 then
    for pc, s in pairs(stat) do
      L.log(string.format("stat pc=%08X lo=%08X hi=%08X n=%d first=f%d", pc, s.lo, s.hi, s.n, s.f))
    end
    stat = {}
  end
end)
