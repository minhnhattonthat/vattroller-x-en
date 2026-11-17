-- romruler.lua: width test for a pointered ROM string without a rebuild. Writes TEXT (ASCII) + NUL at ROM offset
-- AT in the emulator's ROM copy and points every 4-byte pointer at the ROM offsets in PTRS there (the `ptrs` of the
-- row in script/rom/*.json; pointer tables are not moved by the build). Pick AT in free space (all 0xFF).
--   warp.py vrx_stage --out work/qa/vrxstage/ruler --script tools/lua/romruler.lua \
--     --var "TEXT='ABCDEFGHIJKLMNOPQRSTUVWXYZ'" --var "PTRS='efbe8,efd5c'" --var AT=0x9F0000
local P = emu.memType.gbaPrgRom
local at = assert(AT, "AT")
local text = assert(TEXT, "TEXT")
for k = 1, #text do emu.write(at + k - 1, text:byte(k), P) end
emu.write(at + #text, 0, P)
for h in string.gmatch(assert(PTRS, "PTRS"), "%x+") do
  local p = tonumber(h, 16)
  emu.write32(p, 0x08000000 + at, P)
end
L.log(string.format("ROMRULER %d chars at %X", #text, at))
