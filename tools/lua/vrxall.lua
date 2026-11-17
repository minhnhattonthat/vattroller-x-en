-- vrxall.lua: unlock every VRX character: the unlock test 0x08065748(id) reads bit id of u32[6] at IWRAM
-- 0x03002CF8 (refreshed on screen init); the bits are set at that function's entry, so the VRX player/opponent
-- select lists show every name and profile (text coverage, visual QA). Reach VRX with the `vrx_*` warp scenes
-- (docs/re/debug.md §VRX). KEY/EVERY/START: optional press loop.
local M = emu.memType.gbaMemory
L.on_exec(0x08065748, 0x08065748, function()
  for a = 0x03002CF8, 0x03002D0F do emu.write(a, 0xFF, M) end
end)
L.on_frame(function(f)
  if KEY and f >= (START or 30) and (f - (START or 30)) % (EVERY or 30) == 0 then L.press(KEY, 2) end
end)
