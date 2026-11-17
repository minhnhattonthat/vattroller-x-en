-- regset.lua: at every exec of each address set one register, e.g. force a Yes/No result and a check's return
-- value so a screen takes a branch the cold-boot state never reaches (text coverage with textcover.lua).
--   warp.py md16 ... --script tools/lua/regset.lua --var "REGSET={{0x0803CDAA,1,0},{0x0803CDCA,0,1}}"
--   (mode 16 V Skill forget: choice result r1 = 0 "Sure", then the Armalet Size check returns 1 = exceeded)
-- An optional 4th field caps the hits that are changed ({addr,reg,val,1} = once, for a per-frame callback).
-- REGSET_FROM: first frame to act (default 0). Logs "REGSET addr rN=v f<frame>" for the first 20 hits.
local from, logged = REGSET_FROM or 0, 0
for _, t in ipairs(assert(REGSET, "set --var REGSET={{addr,reg,val},..}")) do
  local a, r, v, left = t[1], t[2], t[3], t[4] or math.huge
  L.on_exec(a, a, function()
    if L.frame < from or left <= 0 then return end
    left = left - 1
    local s = emu.getState()
    s["cpu.r" .. r] = v
    emu.setState(s)
    if logged < 20 then
      logged = logged + 1
      L.log(string.format("REGSET %08X r%d=%X f%d", a, r, v, L.frame))
    end
  end)
end
