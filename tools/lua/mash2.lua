-- Click through dialogue AND choices: after the route ends, every MASH2 frames (default 40) press KEY1 (default
-- "down") then "a". Vattroller X choice boxes start with no option selected, so plain A-mashing stalls on them.
--   emu.py ... --frames N --script tools/lua/mash2.lua [--var MASH2=40 --var "KEY1='down'"]
local every, key1 = MASH2 or 40, KEY1 or "down"
L.on_frame(function(f)
  if L.route_done() and f % every == 0 then
    L.press(key1, 6); L.press("-", 8); L.press("a", 6)
  end
end)
