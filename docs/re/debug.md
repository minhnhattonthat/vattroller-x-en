# Debug tool: warps, rooms, scripts, flags

**verified** by `tools/debug/warp.py --all`: all 52 scenes in `tools/debug/scenes.json` reached from a cold boot on
the original ROM (2026-11-17), shots in `docs/screenshots/phase2_warps*.png` (order = `warp.py --list`).

## Use

    python -X utf8 tools/debug/warp.py SCENE [SCENE..] [--state] [--sheet]   # work/qa/warp/<scene>/scene.png
    python -X utf8 tools/debug/warp.py --all --jobs 5 --state                # every scene; regenerates work/states/
    python -X utf8 tools/debug/warp.py try --set book=0 --set room=27        # ad-hoc scene (any scenes.json field)
    python -X utf8 tools/debug/rooms.py --list                               # room ids, names, entry points

`warp.lua` boots cold, presses through the logos/title, forces the shelf unlock mask, puts the shelf cursor on the
book, answers the "start this book?" prompt, (RPG slots: clicks through character creation, then mashes the story
until the target load), swaps the room id/position at the room loader, plays `post`, waits `hold`, shoots
`scene.png`, asserts the loaded room (and `expect`, the room at the shot, if given) and saves the state. Extra
probes: `--script tools/lua/oplog.lua` etc.

## Game structure

- Title → title menu (`さいしょから／つづきから はじめる`, データをけす) → bookshelf. The shelf holds 16 books
  (table at ROM `0x77E8C`, 0x18 bytes each: room, player character, title pointers, shelf position): books 0-7 are
  RPG-mode save slots (start room 107), 8 Jin 登場編 (190), 9 げきとう編 (194), 10 修行編 (199), 11 アレーナ編 (204),
  12 Ryou 番外編 (215), 13 Tota 番外編 (220), 14 Shuu 番外編 (218), 15 デスロール編 (229).
- Fresh save unlocks only book 8 (mask 0x100).

## RAM / code (IWRAM unless noted)

| What | Where | State |
|---|---|---|
| shelf unlock mask (u32, bit = book) | `0x03003D38`, read by the shelf init at `0x080550B0` | verified (forced, all books open) |
| shelf cursor column / row (s8) | `0x03003DA9` / `0x03003DAA`; grid of book ids at `0x03003D64` (row 0 = books 8-15, row 1 = 0-7) | verified |
| player struct | `0x03005490`: +0x60 x, +0x62 y (tiles), +0x64 facing (u16, flags in high byte), +0x68 room id (s16) | verified |
| room loader, first room of a book | `0x0802F65C` reads room id; `0x0802FF34(room)` loads it | verified |
| room loader, door / teleport | `0x0802F930` (reads x, y, room), calls `0x080300C8` | verified |
| room table | ROM `0x0BC20`, 236 × 40 bytes: +0 name ptr, +0x0E map-data file, +0x10 event file | verified |
| archive lookup | `0x0802E980` get_file_ptr(index), table pointer at `0x02008FFC` | verified |
| script interpreter | op dispatch `0x08030B80` (jump table `0x08030B98`, 0x43 ops), command pointer `0x030063F4`, wait callback `0x030063EC` | verified |
| op 0x05 teleport | `u16 room, x, y, facing` (size 12) | verified (warp uses its fields) |
| op 0x1D battle start | installs callback `0x08032685` (battle runner) | verified (tutorial battle) |
| op 0x06 conditional block | `0x08031328`: condition type `+0x0A & 0xFFF`; false → skip `+4` bytes | verified by disassembly |
| flags, cond type 1 | bit `d` of u32 `[c]` at `*(0x03002AA0)+0x4EC` (= `0x02001794` EWRAM) | guess (code read, not poked) |
| flags, cond type 2 / 4 | `*(0x03002A90)+0x1E0` / `+0x1E4` (= `0x02002238` / `0x0200223C`) | guess |
| script vars (s8, 8 per group) | `*(0x03002A90)+0x2D6` (= `0x0200232E`); set/add/sub at `0x080312CC/E8/0x08031308` | guess |

## RPG free control and the field menu (2026-11-17)

The controls tutorial (`rpg_tutorial`) ends in free control in room 84 after ~2000 frames of A taps. Scene field
`premash N` (warp.py) taps A for N frames before `post`; `rpg_free` and `menu_field` / `menu_armalet` /
`menu_chara` / `menu_keyitems` / `menu_settings` / `menu_save` use it (Start opens the field menu: Armalet, Key
Items, Settings, Save). Key Items lists "??????????" for items not owned (game behaviour). `create_confirm` needed
csteps 28 (not 31) after the English name-entry pages (D13). `tools/bgfind.py DUMP x,y,w,h` lists the BG map
entries under a screen rectangle (dump coordinates sit 16 px above the screenshot's: subtract 16 from y) and
finds their tiles in `work/gfx/unpacked/`.

## Text-coverage id sweeps (`tools/lua/idsweep.lua`)

A detail page that draws one table record per cursor move can show every record: the sweep presses KEY each EVERY
frames and, at the page's id load (exec HOOK), writes the next id into `*(PTR)+OFF` (FILL bytes). Run it from the
scene's state with the textcover probe into `work/qa/cover/ids/<name>` (textcover.py searches all of `work/qa/cover`).

| page | HOOK | PTR / OFF | record | status |
|---|---|---|---|---|
| Arm Data (`menu_armdata`, KEY right, N 134) | `0x0804D2E0` (`ldrb r1,[r0,#1]`, r0 = `*0x03002BF4`+0x4C) | `0x03002BF4` / `0x4D` | `*0x02009D58` + id*0x78 = ROM 0xED50 (name + 3 desc ptrs) | verified, 134 Arms drawn, +529 strings |
| V Skills (`menu_vskills`, KEY down, N 103) | `0x0803FB8E` = return of `0x0802DEE8(list idx)` in the desc draw; `REG=0` sets r0 = id there | owned bits u32[4] at `*(0x03002AA0)+0x53C` (unowned → blank page): `OWN_PTR=0x03002AA0 OWN_OFF=0x53C OWN_N=16` | `*0x02009D48` + id*0x28 = ROM 0x7C78 (name + 5 desc line ptrs) | verified, 103 skills drawn (`work/qa/cover/ids/vskills/id###.png`), +449 strings |
| Arm Data page header (`0x0803FDFE`, id `*(0x03002BF8)+0xD`, V Skill record) | fires once per page open only | | | |

## VRX (the single-player VR game, 2026-11-17)

V Center 2F's single-player machine runs event op `0x2A` arg 1 (`2a00080001000000`, e2617 after line
e2617_00a24). warp.lua var `NODE` (scene field `node` = `{"after": id, "op": hex}`, resolved by warp.py from
`build/strings.tsv`, build only) runs that one command from the comic room when POST starts: scenes `vrx_title`,
`vrx_players`, `vrx_player`, `vrx_opponent`, `vrx_rules`, `vrx_stage` (states saved). A battle then runs on its
own (both sides CPU-like; ~120 s timer, a draw returns to the comic). `tools/lua/vrxall.lua` (scene field
`scripts`) unlocks every character: the test `0x08065748(id)` reads bit id of u32[6] at IWRAM `0x03002CF8`
(re-read from the save on screen init, so the bits are set at the function's entry). Roster: id → record map at
`0x03002D10`, records `*0x02009D38` + idx*0x58 = ROM 0xCE0 (22 pointers: +0 name, +4 "…", +8.. profile lines and
win quote); the list draw is `0x080668CC`. The profile panel (lines from record +8) is drawn by `0x0806A2F4(id)`,
called from the state machine at `0x0806A4C8` — not seen in a draw-ended battle: probably the winner screen;
needs a forced win (next).

## Shops: game mode 10 (2026-11-17, 14th worker)

The top-level mode switch is `0x0802D128` (jump table `0x0802D168`, index mode-1): mode `*0x030029D4`, next mode
`*0x030029D8`, taken at `0x0802D134` when the running task ends. Mode 10 = shop `0x080696FC(arg)`, arg = byte
`*(0x03002AA4)+0x14` = shop id (1-15 all stock lists; 10 is empty). warp.lua vars `MODE` /
`MODE_ARG` (scene fields `mode`, `mode_arg`) redirect the first boot dispatch, so a shop opens from a cold boot
with no book or room: scenes `shop_arms`, `shop_tools`, `shop_vrxdata`, `shop_buy` (VRX profile panel),
`shop_buy_arm`. The shop has three tabs (R/L; state byte `0x03002DB0`): Arms / Tools / VRX Data; A opens the buy
prompt `0x0806A3B0` with the item's detail on the right. `tools/lua/shopall.lua`: save struct `*(0x03002AA0)`
+0x54C u32 bits = owned VRX Data (unowned rows show `????????????`), +0x584 = VP; `PROFILE=1 N= [HOOK= REG=]`
sweeps every record through the buy prompt's detail draw (A/B route in POST):

| tab | HOOK / REG | records | run |
|---|---|---|---|
| VRX Data | `0x0806A4C8` / r0 (bl `0x0806A2F4`, roster id) | 165, ROM 0xCE0 stride 0x58 | `work/qa/cover/ids/shop_profiles`, +442 strings |
| Tools | `0x0806A484` / r2 (item id to `0x0803F608`) | 46, ROM 0x14FB0 stride 0x18 | `work/qa/cover/ids/shop_tools`, +181 strings |
| Arms | `0x0806A40E` / r3 | 134 (covered by the Arm Data sweep) | |

Other modes of the same switch are untested: try `warp.py tryN --set mode=N --set mode_arg=K` for the screens
still missing in text coverage (V-Pon, link, data screens).

## Gaps (next)

- RPG mode: free control and the field menu are reached (above). Shops are reached as rooms, but shopkeepers need
  story flags (and walking from free control, or a warp into a shop room that keeps control): find
  the flag(s) the shop common event (op 0x29 → common script 0x0D) tests, and an "intro done" state. Then add
  scenes: field menu and submenus (items, armalet, settings `せってい`, character data), shop buy/sell, save
  (`記録`), title `つづきから` with a save, data delete.
- Battles: no auto-win yet. The tutorial battle and the RPG intro battle end under mashing; story battles may not.
  Battle HP is not found (on-screen gauges are sprite/BG bars; RAM correlation failed). Find it from the op 0x1D
  runner (`0x08032685`) for a `GOD` option.
- `rooms.json` entry points come from script teleports; 91 story rooms have none (they set their own position).
