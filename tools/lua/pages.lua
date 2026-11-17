-- pages.lua: after a warp lands on name entry, shoot each keyboard page (KEY switches pages; default "r").
--   warp.py create_name --set hold=400 --script tools/lua/pages.lua [--var AT=1920 --var KEY=r]
local at, key = AT or 1920, KEY or "r"
L.on_frame(function(f)
  local k = f - at
  if k == 0 or k == 60 or k == 120 or k == 180 then L.shot(string.format("f%06d.png", f)) end
  if k == 20 or k == 80 or k == 140 then L.press(key, 6) end
end)
