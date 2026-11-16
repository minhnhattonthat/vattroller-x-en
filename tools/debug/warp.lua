-- Vattroller X debug warp (docs/re/debug.md). Cold boot -> bookshelf (all books unlocked) -> open a book ->
-- (RPG mode: click through character creation) -> swap the first room the game loads for ROOM -> play POST ->
-- hold HOLD frames -> shot "scene.png", assert the room, optional state save, stop.
-- Normally driven by tools/debug/warp.py from tools/debug/scenes.json. Vars (all optional except BOOK):
--   BOOK      shelf book: 0-7 RPG save slots, 8 Jin 登場編, 9 げきとう編, 10 修行編, 11 アレーナ編,
--             12 Ryou 番外編, 13 Tota 番外編, 14 Shuu 番外編, 15 デスロール編; -1 = stop on the shelf
--   ROOM      room id (0-235, rom 0x0BC20 table) to load instead of the book's first room
--   X, Y, FACE  entry tile and facing for ROOM (same fields as script op 0x05); default: the book's spawn
--   VIA       "load" (comic books' first room) or "door" (first door/teleport; default for RPG slots)
--   FROM_ROOM swap only a load of this room (default 107 for RPG slots: the intro shows panels first)
--   POST      route after the room loads, "FRAMES BUTTONS;..." like emu.py --route-str ("30 start;60 -")
--   HOLD      frames to wait after POST before the shot (default 240)
--   STOP_AT   "title" | "titlemenu" | "shelf" | "prompt" | "creation" stops early at that screen
--   UNLOCK    shelf unlock mask (default 0xFFFF; the game's fresh-save value is 0x100)
--   STATE_OUT absolute path: save a state after the shot
--   MASHPOST  1 = after POST, keep pressing down,A during HOLD (choices need a direction first)
local M = emu.memType.gbaMemory
local ROOM_VAR = 0x030054F8          -- s16 room id read by the room loader
local UNLOCK_VAR = 0x03003D38        -- u32 shelf unlock mask (bit = book index)
local CUR_X, CUR_Y = 0x03003DA9, 0x03003DAA  -- shelf cursor column / row (s8)
local book = BOOK or 8
local stop_at = STOP_AT or ""
local hold = HOLD or 240
local phase, t0 = "boot", 0
local loaded_room, warped = nil, false

local function set_phase(p) phase = p; t0 = L.frame; L.log(string.format("f%d phase %s", L.frame, p)) end

local function play(route)
  for step in (route or ""):gmatch("[^;]+") do
    local n, spec = step:match("^%s*(%d+)%s+(%S+)%s*$")
    if not n then L.fail("bad POST step: " .. step) return end
    L.press(spec, tonumber(n))
  end
end

local function finish()
  if phase == "stopped" then return end
  local room = emu.read16(ROOM_VAR, M)
  L.shot("scene.png")
  L.log(string.format("f%d done room=%d loaded=%s", L.frame, room, tostring(loaded_room)))
  set_phase("stopped")
  -- scene flag check: the room the warp loaded (scripts may move on to other rooms during HOLD), and EXPECT
  -- (the room id at the shot) when the scene names one
  if ROOM and loaded_room ~= ROOM then L.fail(string.format("expected room %d, loaded %s", ROOM, tostring(loaded_room))) return end
  if EXPECT and room ~= EXPECT then L.fail(string.format("expected room %d at the shot, game is in room %d", EXPECT, room)) return end
  if STATE_OUT then
    L.save_state(STATE_OUT, function() L.finish(0) end)
  else
    L.finish(0)
  end
end

-- the shelf init: force the unlock mask before the shelf builds its book grid
L.on_exec(0x080550B0, 0x080550B0, function()
  emu.write32(UNLOCK_VAR, UNLOCK or 0xFFFF, M)
  if phase == "boot" or phase == "titlemenu" then set_phase("shelf") end
end)

-- Two room-load paths, both reading room/x/y/facing from 0x030054F0-F8:
--   "load": the book's first room (0x0802F65C, just before the ldrsh of the room id)
--   "door": a door or script teleport (op 0x05) (0x0802F930, before x/y and the room id are read)
-- RPG mode's intro teleports to room 107 right after its first load, so RPG scenes warp on "door".
local via = VIA or (book < 8 and "door" or "load")
local from = FROM_ROOM or (book < 8 and 107 or nil)   -- RPG: the teleport into the club room (107), not the intro
local from_seen = 0                                   -- FROM_NTH: swap the Nth load of FROM_ROOM (default 1st)
local function on_load(kind)
  if kind ~= via then return end
  local cur = emu.read16(ROOM_VAR, M)
  if from and not warped then
    if cur == from then from_seen = from_seen + 1 end
    if cur ~= from or from_seen < (FROM_NTH or 1) then
      if phase == "creation" then set_phase("intro") end   -- creation is over; mash through the story to FROM_ROOM
      return
    end
  end
  if ROOM and not warped then
    emu.write16(ROOM_VAR, ROOM, M)
    if X then emu.write16(ROOM_VAR - 8, X, M); emu.write16(ROOM_VAR - 6, Y, M) end   -- tile x, y
    if FACE then emu.write16(ROOM_VAR - 4, FACE, M) end   -- facing | flags << 8, as in op 0x05
    L.log(string.format("f%d warp room %d -> %d at %s,%s", L.frame, cur, ROOM, tostring(X), tostring(Y)))
    cur = ROOM
  end
  warped = true
  if phase ~= "stopped" and phase ~= "post" and phase ~= "hold" then
    loaded_room = cur
    set_phase("loaded")
  end
end
L.on_exec(0x0802F65C, 0x0802F65C, function() on_load("load") end)
L.on_exec(0x0802F930, 0x0802F930, function() on_load("door") end)

L.on_frame(function(f)
  local dt = f - t0
  if phase == "boot" then
    -- logos, title, title menu: Start on the title, A on the menu
    if stop_at == "title" then if f >= 720 then finish() end return end  -- no input: logos, then title
    if stop_at == "titlemenu" and f >= 1000 then finish() return end
    if dt % 40 == 0 and L.route_done() then
      if f < 800 then L.press("start", 6)
      elseif stop_at ~= "titlemenu" then L.press("a", 6) end
    end
  elseif phase == "shelf" then
    if dt == 90 then
      if stop_at == "shelf" or book < 0 then finish() return end
      if book >= 8 then emu.write(CUR_X, book - 8, M); emu.write(CUR_Y, 0, M)
      else emu.write(CUR_X, book, M); emu.write(CUR_Y, 1, M) end
    elseif dt == 100 then
      L.press("a", 6)
    elseif dt == 160 then
      if stop_at == "prompt" then finish() return end
      set_phase("open")
    end
  elseif phase == "open" then
    -- "この本を はじめますか?" yes is the top option; nothing is selected until a direction is pressed
    if dt % 60 == 0 and L.route_done() then
      if book < 8 and dt >= 120 then set_phase("creation") return end
      L.press("up", 6); L.press("-", 14); L.press("a", 6)
    end
  elseif phase == "creation" then
    -- armalet select, face select, name entry, favourite word, confirm: A picks, Start confirms entries
    -- STOP_AT "creation": stop 60 frames after CSTEPS presses (0 = the first screen, armalet select)
    if stop_at == "creation" and dt == (CSTEPS or 0) * 50 + 60 then finish() return end
    -- name entry: Start jumps to the end key, the next A confirms it
    if dt % 50 == 0 and L.route_done() and not (stop_at == "creation" and dt >= (CSTEPS or 0) * 50) then
      L.press(({ "a", "start", "a", "down" })[(dt // 50) % 4 + 1], 6)
    end
  elseif phase == "intro" then
    -- story text and choices (nothing is selected until a direction is pressed)
    if dt % 40 == 0 and L.route_done() then L.press("down", 6); L.press("-", 8); L.press("a", 6) end
  elseif phase == "loaded" then
    if dt == 30 then play(POST); set_phase("post") end
  elseif phase == "post" then
    if L.route_done() then set_phase("hold") end
  elseif phase == "hold" then
    if MASHPOST and dt % 40 == 0 and L.route_done() then L.press("down", 6); L.press("-", 8); L.press("a", 6) end
    if dt >= hold then finish() end
  end
end)
