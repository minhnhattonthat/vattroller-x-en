-- execrange.lua: count instructions executed in a ROM range (prove a code block never runs in a scene).
--   warp.py SCENE --script tools/lua/execrange.lua --var LO=0x080EFF78 --var HI=0x080FFFFF
-- Logs "EXECRANGE first f<frame> pc=<pc>" on the first hit and "EXECRANGE n=<count>" every 600 frames and at the end.
local n, first = 0, nil
L.on_exec(assert(LO), assert(HI), function(addr)
  n = n + 1
  if not first then
    first = addr
    L.log(string.format("EXECRANGE first f%d pc=%08X", L.frame, addr))
  end
end)
L.on_frame(function(f)
  if f % 600 == 0 then L.log(string.format("EXECRANGE n=%d", n)) end
end)
