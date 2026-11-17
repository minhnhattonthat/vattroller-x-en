-- vrxstages.lua: unlock all 20 VRX stages in Stage Select (text coverage). The list builder 0x0806588C fills the
-- byte list 0x03002D98 with every stage i (0-19) that passes 0x080657C4(i) = bit i of the u32 at IWRAM 0x03002D90
-- (re-read from the save on screen init, so set at the test's entry, like vrxall.lua). Stage records: ROM
-- 0x0807AEAC + id*12 (+0 = name index into the table copied to EWRAM 0x0200C4A4). Use with vrxall.lua on vrx_stage.
local M = emu.memType.gbaMemory
L.on_exec(0x080657C4, 0x080657C4, function()
  for a = 0x03002D90, 0x03002D93 do emu.write(a, 0xFF, M) end
end)
