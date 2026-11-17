-- pcmenu.lua: open the PC menu (Arm Set / Box / List / Password, window 7, labels r0e2100..) from a cold boot.
-- Room PCs run event op 0x18 (dispatch 0x08030B80: ldrb r0,[r2] = op, jump table 0x08030B98; case 0x18 sets
-- the event continuation *(0x03005500+0xEEC) = 0x08032999, which opens window 7 via 0x080712B8(7) and runs
-- the menu's selections; docs/re/debug.md §PC menu). This probe makes the first event command dispatched in
-- warp phase PHASE (default "loaded") read as op 0x18, so any scene whose room runs an event opens the PC menu.
--   warp.py rpg_start --out work/qa/pcm --script tools/lua/pcmenu.lua [--var "PHASE='post'"] --set "post=..."
-- OP=0x19: the V Shop counter instead (op 0x19 -> 0x08032BAD -> 0x0803696C, window 8: V-Pon / Quit, Buy / Sell).
-- OP=0x29: a shop clerk (Buy / Sell / Quit); REC=n picks the clerk's line set (0x0200AD1C = ROM 0xEE460,
-- 16-byte records of 4 lines: 0 V Shop, 1 "Rare" V Shop, 2 plain shop, 4 V Machine, 5 link group).
-- WINDOW_ONLY=1: only swap the window id 6 -> 7 in the opener 0x080712E0 (Start on menu_field draws the PC
-- menu, but its rows run the field menu's actions).
local M = emu.memType.gbaMemory
local done = false
if WINDOW_ONLY then
  L.on_exec(0x080712E0, 0x080712E0, function()
    if done or emu.read(0x03002B00, M) ~= 6 then return end
    done = true
    emu.write(0x03002B00, 7, M)
    L.log(string.format("PCMENU window 6 -> 7 f%d", L.frame))
  end)
else
  local want = PHASE or "loaded"
  L.on_exec(0x08030B82, 0x08030B82, function()
    if done or WARP_PHASE ~= want then return end
    done = true
    local s = emu.getState()
    L.log(string.format("PCMENU op %02X at %08X -> %02X f%d", s["cpu.r0"], s["cpu.r2"], OP or 0x18, L.frame))
    s["cpu.r0"] = OP or 0x18
    emu.setState(s)
  end)
  if PRESS then   -- after the swap, click through: KEY1 (default "down") then A every PRESS frames
    L.on_frame(function(f)
      if done and f % PRESS == 0 then L.press(KEY1 or "down", 6); L.press("-", 8); L.press("a", 6) end
    end)
  end
  if REC then   -- op 0x29: clerk line set = record byte cmd+5 of the table 0x0200AD1C (stride 16)
    for _, pc in ipairs({ 0x08032312, 0x08032354, 0x0803239E, 0x0803248A }) do   -- after each ldrb r0,[rX,#5]
      L.on_exec(pc, pc, function()
        local s = emu.getState()
        s["cpu.r0"] = REC
        emu.setState(s)
      end)
    end
  end
end
