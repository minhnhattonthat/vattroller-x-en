-- with warp.py/emu.py --script and --var DUMP_FRAMES="{10200,10320}": PPU dump + shot at each listed frame,
-- as d<frame>.ppu.vram.bin ... and d<frame>.png in the run directory
local want = {}
for _, f in ipairs(DUMP_FRAMES or {}) do want[f] = true end
L.on_frame(function(f)
  if want[f] then
    L.dump_ppu("d" .. f .. ".ppu")
    L.shot("d" .. f .. ".png")
  end
end)
