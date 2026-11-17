-- dumpevery.lua: PPU dump (d<frame>.oam.bin/.vram.bin/...) every EVERY frames from FROM, for oamlabels.py.
--   warp.py SCENE --script tools/lua/dumpevery.lua --var FROM=1000 --var EVERY=120
local from, every = FROM or 0, EVERY or 120
L.on_frame(function(f)
  if f >= from and (f - from) % every == 0 then L.dump_ppu(string.format("d%06d", f)) end
end)
