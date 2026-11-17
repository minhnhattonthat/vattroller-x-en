-- shots.lua: a screenshot every EVERY frames between FROM and TO (for warp.py runs, which have no --shot-every).
--   warp.py SCENE --script tools/lua/shots.lua --var FROM=4800 --var EVERY=20 [--var TO=9000]
local from, every, to = FROM or 0, EVERY or 20, TO or math.huge
L.on_frame(function(f)
  if f >= from and f <= to and (f - from) % every == 0 then L.shot(string.format("f%06d.png", f)) end
end)
