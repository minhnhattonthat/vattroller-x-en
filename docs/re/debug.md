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

## Gaps (next)

- RPG mode: the intro runs ~20,000 frames (creation, club room, tutorial battle, controls tutorial) before free
  control. Shops are reached as rooms, but shopkeepers and the field menu need free control and story flags: find
  the flag(s) the shop common event (op 0x29 → common script 0x0D) tests, and an "intro done" state. Then add
  scenes: field menu and submenus (items, armalet, settings `せってい`, character data), shop buy/sell, save
  (`記録`), title `つづきから` with a save, data delete.
- Battles: no auto-win yet. The tutorial battle and the RPG intro battle end under mashing; story battles may not.
  Battle HP is not found (on-screen gauges are sprite/BG bars; RAM correlation failed). Find it from the op 0x1D
  runner (`0x08032685`) for a `GOD` option.
- `rooms.json` entry points come from script teleports; 91 story rooms have none (they set their own position).
