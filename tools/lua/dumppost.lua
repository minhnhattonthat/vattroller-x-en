-- dumppost.lua: PPU dump + shot every EVERY frames while warp.lua is in its "post" phase (the scene's input route),
-- as p<frame>.ppu.* / p<frame>.png, for oamlabels.py on screens whose post route is long (help-bubble sweeps).
--   warp.py SCENE --script tools/lua/dumppost.lua --var EVERY=30 --set "post=..."
local every, start = EVERY or 30, nil
L.on_frame(function(f)
  if WARP_PHASE ~= "post" then return end
  start = start or f
  if (f - start) % every == 0 then
    L.dump_ppu(string.format("p%06d.ppu", f))
    L.shot(string.format("p%06d.png", f))
  end
end)
