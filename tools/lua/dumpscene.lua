-- with warp.py --script: dump PPU state (ppu.vram/pal/oam/io.bin) when the scene shot is taken
local shot = L.shot
L.shot = function(name)
  if name == "scene.png" then L.dump_ppu("ppu") end
  return shot(name)
end
