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

Mode survey (`warp.py mdN --set mode=N --set mode_arg=0 --set "post=200 -" --set hold=10`, arg 0, cold boot):
1 logos, 2 title, 3 Continue/data screen (Play Time, Vattroller Points, Battles; Delete Data), 4 shelf, 5/7/8
black, 6 a field map, 9 **world/town map** (place names r00e1xx), 10 shop, 11/12/15 two-panel box screens with VP
(V Box / storage?), 13 **V-Pon machine** ("Gale Sword obtained!"), 14 "Choose an item to throw away", 16 "Choose a
V Skill to forget!", 17 list with VP (sell/transfer?), 18 blank, 19/20 **link** ("Linking... Please wait a
moment."), 21 VRX, 22 stripes, 23 character portrait panel, 24 stats panel, 25 black, 26 "Rematch?". Each still
needs its arg meaning, scenes and id sweeps (next worker).

## Room names, V Skill tail (2026-11-17, 15th worker)

- Room table ROM 0xBC20 (`*0x02009D54`, 236 records, stride 0x28, +0 = name pointer, r00e1xx-r00ecxx). The
  only reader of the name is the **room-name banner** `0x08036678(room)` (top of the screen on entering an
  area; called by the room loader at `0x0803602C` when `*(0x03003070+0x1684)` != 0). `tools/lua/roomnames.lua`
  loops the banner over all 236 rooms in one call (re-enters at `0x0803669A` with r4 = next record; Mesen GBA
  jump = set `cpu.r15` + `cpu.pipeline.reloadRequested`; the text queue `*(0x030028D0)` +0xC0 lines / +0xC1
  glyphs is reset each loop, or `0x080282B8` bails after ~5). `FIRST=k N=k+1` shows one room's banner
  (`menu_field` draws it about f21530). All 236 covered; the longest, "Death Roll Colosseum", fits. Left
  margin = the original's (5 px).
- World map (mode 9): the place labels on the map are graphics (G15), not the room table.
- V Skill table `*0x02009D48` = ROM 0x7890 has 128 records (owned bits u32[4]); the 13th-worker sweep did ids
  0-102. Ids 103-127: `idsweep.lua ... --var FIRST=103 --var N=25` (`work/qa/cover/ids/vskills2`). Field +0 of
  the record (r008c90 "Sturdy"...) is read only at `0x0804084C` (record 25 in `menu_vskills`); the list rows draw
  other copies (r00a1xx), so most +0 names are still unshown: find that page.
- `tools/lua/setbytes.lua` holds bytes (e.g. every owned bit) on every frame, for pages that build their list
  when opened.
- Armalet table `*0x02009D44` = ROM 0x7080 (19 records, stride 0x24: name + 4 desc lines + data). Special-move
  table `*0x02009D64` = ROM 0x160D0 (36 records, stride 0x38: 5 name parts + 4 desc lines); readers: 14 code
  refs, none draws the strings in the scenes tried (menu_armalet, menu_chara, battle_tutorial).

## Special moves (2026-11-17, 16th worker)

- A special = a combo of two Arms: `0x080534AC` takes the two Arm ids at state `*0x03006D4C` +0x18/+0x19, their
  type byte (Arm record +0x10), the combo table `*0x02009D60`[type1*16 + type2] = special id (read at
  `0x080534D8`), and copies the 4 desc pointers (+0x14..+0x20) into the state; `0x0805310C` draws them in the
  right-hand "special details" panel (head ひっさつわざしょうさい, graphics G17). Caller chain: Arm Data device box
  `0x0804B0B4` (state `*0x03002D50`, cursor s16 +0x36; up/down in `menu_armdata` moves it 0↔1) → cursor >= 2 =
  combo slot → `0x08051474(cursor+3)` (special byte `*(0x030051BC)+0x20+n`, < 0 = none) → `0x08053080`.
- `tools/lua/specialsweep.lua` forces cursor 2, the "has a special" test and the id: all 36 descriptions drawn
  (`work/qa/cover/ids/specials/id###.png`), +145 strings. The 5 **name parts** per record (+0..+0x10, r0168b0
  "Nova", "Flash"...; 180 strings) are not read by this page; the other 13 table refs (`0x08051680`..,
  `0x0805F0A6`, `0x0805FF74`, `0x08060052`, `0x08061B2C`) are battle logic/effects. Next: watch reads of
  ROM 0x0168B0-0x017D90 (`probes/watch.lua`, WATCH_MODE read) in a battle where a special is used.

## Key Items, V Skill list, V Shop unlocks, rulers (2026-11-17, 19th worker)

- The data-table block ROM 0xED48C.. is copied to EWRAM at boot (f274, DMA): ROM 0xEEBD8 (Key Item name table)
  = EWRAM 0x0200B494, so ROM X = EWRAM X - 0x080E3744 + 0x02000000 for the whole block; `*0x02009D44..0x02009D98`
  are its table pointers. `tools/lua/findword.lua --var WORD=0x...` finds where a (built) pointer value sits in RAM.
- **Key Items**: owned = bit i of u32 `*(0x03002A90)+0x1E0` (13 items, names ROM 0xEEBD8.., descriptions 4-5
  pointer arrays of 13 from 0xEEA98, stride 0x34); drawer `0x080410BC`, unowned rows show r076618 "??????????"
  (ptr 0xEEA90). `tools/lua/keyall.lua`; scene `key_items_all` walks all 13 (names + descriptions covered).
- **V Skills page list** = the 5 equipped slots, s8 at `*(0x03002A90)+0x73..0x77` (`0x0802DEE8(i)`), each row
  the record's +0 name (`0x0804084C`); owning all 128 (bits at +0x53C) does not lengthen it.
  `tools/lua/vsslots.lua` puts ids 5g..5g+4 in the slots and moves g on each B press of the post route (needs
  `WARP_PHASE`, now a global set by warp.lua); scene `vskills_names` reopens the page 26 times: all 128 names.
- **V Shop unlock table** `*0x02009D94` = ROM 0x1D5F0.. (count at ROM 0x1E3D0; records 0x14: +0 handler type,
  +3 s8 bit in u16 save+0x58C (-1 none), +4 s16 threshold, +8 name ptr, +0xC/+0x10 message lines
  "X now sold / at the V Shop!!∇", r01d900-r01e3xx). `0x0802D874(delta)` adds to the counter save+0x588
  (`*(0x03002AA0)+0x588`, clamped 0..999; called from `0x0802D500`, probably the battle result) then
  `0x0802CCC0` runs the handler (`*0x02008EE8`[type]) of every record whose threshold <= counter and sets its
  0x58C bit; `0x0802D044` re-applies the handlers for set bits (room load `0x08034E50`). The **message** is printed
  by callbacks `0x0804FE60` (+0xC) / `0x0804FE9C` (+0x10) with the record index at `*(*0x03003648)`, via the
  text printer `0x08073064`: find who queues them (likely the VS result screen after `0x0802D874`), then sweep
  the index like idsweep.lua. Holding 0x58C = 0xFFFF on `rpg_free` with the field menu opened shows nothing.
- Rulers (`romruler.lua`, no rebuild; free 0xFF run at ROM 0x26BA4F-0x26BC91 for AT): Key Items list 16 chars,
  Arm Data header 24, Armalet Data Name box 12, shop Tools list 20 (to the price column), VRX Data list name 16,
  shop profile panel line 16, Character Data "Fav. Word" label 12 (`work/qa/keyruler`, `work/qa/ruler19/*`).

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

## Coverage across builds, VRX overlay, link block (2026-11-18, 20th worker)

- **Logs from older builds**: `tools/cover.py` maps every textcover `log.txt` to the build it ran on and reads it
  as string ids, so probe passes survive text edits (only repointed ROM strings move, ~2000 r ids; event text
  stays put). Layouts `work/layouts/<rom sha1>.tsv/.gba`; old ones rebuilt from their commits in a scratch
  worktree (sha1s reproduce exactly). A log's build = its `build.sha1` stamp (warp.py and textsweep.py write it
  now), else the layout whose ROM puts a NUL in the last halfword of most read runs inside the repointed-string
  block 0x810000-0x81BCxx (the text loop reads halfwords and stops on the NUL; right layout 0.8-1.0, wrong
  0.2-0.6). Ties count only ids they agree on. The probe's 2nd field is the frame, not the byte read.
  Report: `cover.py` then `textcover.py work/qa/cover_now build/strings.tsv --mask 0x1FFFFFF --waive docs/text_unshown.tsv`.
- **VRX overlay**: boot (`0x08025994`) DMAs ROM 0xE4994-0xEFF78 to EWRAM 0x02001250; VRX tables in that range are
  read from the copy (stage name table ROM 0xEFBE8 = EWRAM 0x0200C4A4), so a ROM-range read probe on them only sees
  the boot DMA. Stage Select: list builder `0x0806588C` puts each stage i (0-19) passing `0x080657C4(i)` (bit i of
  u32 IWRAM 0x03002D90, reloaded on screen init) into the byte list 0x03002D98; records ROM 0x0807AEAC + id*12.
  `tools/lua/vrxstages.lua` sets the bits at the test's entry: scene `vrx_stage_all` (all 20 stages + size/base/
  wall lines). `vrx_rules_survival` = Survival description.
- **Link block ROM 0xEFF78-0xFFFFF** (RFU-MBOOT, Sio32, flash library ids; pointer table 0xFFB94 to twin copies
  of the VRX/shop strings r0f0b-r0f16 and no-pointer n0f0-n0f1): `tools/lua/execrange.lua` counts 0 instructions
  there in vrx_stage_all, md19, md20 and rpg_start. VRX 3/4-Player rows are greyed offline; modes 19/20 (V Skill
  trade) wait on "Linking..." forever (B/START don't cancel). Waived in `docs/text_unshown.tsv`.
- **VRX roster record** (ROM 0xCE0 + idx*0x58): +4 = the win quote ("Yay!", r004738-r0065a0, '..' for the hero);
  ids 0x5F+ are NPC/object types (Boy, Student, Clerk, Door 1-8, Undefined 1-2, Arm, Bento...: r0065e8-r006f7c),
  probably never drawn as names. `tools/lua/pcread.lua` logs PC/regs of a read (romreads.lua missed some).
  +4 is the character's favourite word (8 bytes): the fighter load `0x0802B554` copies +0 and +4 into the slot
  (+0x8C, getter `0x0802DE6C`); the VRX win handler `0x080693EC` draws winner name + word. Ids 0x5F+ (and id 0)
  are never drawn: getter `0x0806B0FC` reads roster names only below the count word at ROM 0x73DD8 (0x5F); the
  box speaker tag is op 0x0A byte 5 when byte 4 = 7 (byte 4 = 3: no tag), and no such box names them; room actors
  read only +0x1C/+0x1D/+0x1F (pcread in rpg_conbini/rpg_town). Waived in `docs/text_unshown.tsv`.
- **VRX battle result**: scene `vrx_fight` = Official battle left idle; time-out at ~f9917 → step `0x08068F94`
  picks the DRAW screen when byte 0x03003557 == 1 (cmp `0x08068FC2`), else the win handler `0x080693ED`.
  `tools/lua/vrxwin.lua` forces the win and loops the word draw over roster ids (`N`, `FIRST`; N=0 = real winner).
- **Armalet records** (table ROM 0x7080 via `*0x02009D44`, stride 0x24: name + 4 lines): creation Armalet Select
  redraws on up/down at `0x080474F4` with the id in r1 at `0x08047508`: `idsweep.lua --var HOOK=0x08047508
  --var REG=1 --var N=19 --var "KEY='down'"` from `work/states/create_armalet.mss` draws all 19.

## Special-move names: the Arm Set screen (2026-11-18, 22nd worker)

- Game mode 15 (`warp.py md15 --set mode=15 --set mode_arg=0`) = the Arm Set / Box screen (Armalet with its Arm
  slots, tab ◁Box, hint Ⓐ Grab/Swap; G18). Its bottom "Special" box lists the loadout's three specials, each
  "<Armalet form> <name part>". The loadout fill `0x0805156C` (via `0x080512D8`/`0x0805130C`, from state
  callbacks `0x0804AD5C`..`0x080507D8` in the EWRAM state tables) computes the combos (state `*0x030051BC`:
  +0x1C..1E Arms, +0x21 Armalet, +0x25..27 specials) and stores pointer pairs at +4/+8, +0xC/+0x10, +0x14/+0x18:
  form = `*0x02009D68`[Armalet*3 + special record +0x24] (ROM 0x17A60, 48 names r017b44..), part = special
  record +4*(Armalet record +0x20) (ROM 0x160D0, r0168b0..). The drawer `0x080517E0` renders each with
  `0x08029260` (48 px, 8 px pair cells): form at tile x 1, separator r077d50 (one cell) at x pairs+1, part at
  pairs+2. State bits 0x200/0x400/0x800 swap a row's separator tile for the form's first tile (an empty
  loadout sets them).
- `tools/lua/specialnames.lua` loops the drawer over all 180 parts + 48 forms (`FIRST`, `N`; a run stops after
  ~20 draws, so it ran as FIRST=0/17/20/37/40/56 into `work/qa/cover/ids/specialnames*`). `SHOT=1 NOFLAGS=1
  FORMS={..} PARTS={..}` shows chosen names: "Death Lord  Catastrophe" fits (`work/qa/spn/shot2`); forms and
  parts hold at most 6 cells = 12 letters.

## PC menu, shops, event ops (2026-11-18, 23rd worker)

- **Windows**: `0x080712B8(id)` opens a menu window; the opener `0x080712E0` reads the id at IWRAM s8 `0x03002B00`,
  geometry `0x080E1FC0 + id*12`, callbacks EWRAM `0x02008F20 + id*8` (= ROM 0xEC664, init/tick pairs). Id 6 =
  field menu (Armalet / Key Items / Settings / Save, labels r0e20cc..), 7 = **PC menu** (Arm Set / Box / List /
  Password, r0e2100..; drawer `0x08071770`), 8 = V-Pon / Quit, 9 = Buy / Sell / Quit (`0x080719B4`), 10-12 VP /
  Back. Callers by id: 7 only at `0x08032A64`, 8 at `0x08036A62`, 6 at `0x080384C4` (the field-menu task).
- **Event ops**: dispatch `0x08030B80` (`ldrb r0,[r2]` = op, r2 = command), jump table `0x08030B98` (ops
  0-0x42); most cases set the continuation `*(0x03005500+0xEEC)`. Op 0x18 = room PC (`0x08032999`, ~30 rooms:
  e2534, e2551, e2613...), op 0x19 = V-Pon machine (arg byte +4 = 0-3), op 0x29 = shop clerk (arg +4 = shop
  0-0x15; the clerk's 4 lines come from table EWRAM `0x0200AD1C` = ROM 0xEE460, 16-byte records, index byte
  +5 of the command: 0 V Shop, 1 "Rare" V Shop, 2 plain shop, 4 V Machine, 5 link group), ops 0x2A/0x2D-0x2F/
  0x3E/0x1E/0x42/0x17/0x41 = link sessions ("One moment, please. / B Button: Cancel", wait forever offline).
- `tools/lua/pcmenu.lua` makes the first command dispatched after warp phase "loaded" read as op `OP` (default
  0x18), so `warp.py rpg_town --script tools/lua/pcmenu.lua` opens the PC menu from a cold boot (`REC=n` picks the
  clerk set for op 0x29, `PRESS=n` clicks through). Down x3 + A = the **Password** screen.
- **Password screen** (tick `0x0804EDC4`, struct `*(0x03003648)`, state +0x29, table ROM 0xEEE18): state 9
  `0x0804FE3C` opens the box, 0xA prints unlock record +0xC, 0xB +0x10, 0xC waits for A. `tools/lua/vshopmsg.lua`
  forces state 9 for records 0-37: all 76 V Shop unlock lines drawn (`work/qa/cover/ids/vshopmsg`, sheet.png;
  each fits two box lines).
- Owner map of what is still unshown (string pointer → nearest table base loaded by code): link sessions
  `0x080336EC-0x08034F68` (r073fac-r074248), V-Pon/VP/save `0x08036A48-0x08037030` (r0742f0-r0743b8), match
  results `0x0803727C` (r0743c4-r074474, Vattleague), V Skill trade `0x08039A48-0x0803C710` (r075e74-r076380,
  "partner" text), V Skill forget/learn `0x0803CB10..`, `0x0803D494..`, Break Roll `0x0803E34C`, roster lists
  `0x080404A8`, VS lobby O/X/Guest/roles `0x0804CAE0`/`0x0804D034`, numbers `0x0804E7A4`, win-quote/greeting
  entry `0x0804EF78`/`0x0804EE4C` (default phrases) / grid `0x0804F308`, data delete `0x08054824`, points shop
  `0x0806AA5C`/`0x0806B0BC` (stage names).
