# Fonts and the English text engine

## Japanese glyph path — verified (disassembly + marker build in game)

| Step | Where | What |
|---|---|---|
| op 0x00 | `0x08030CF0` installs `0x08031760` → `0x0803178C` | flags byte `+5` bit 2 (0x0400) first clears the box (`0x0807319C`); then `0x08073064(text, mode, 0x03005500+0xF15)` |
| line setup | `0x08073064` → `0x0807345C` | line object (stride 0x48 at `0x03002B10+0x18`): +0x00-0x37 2-byte-code buffer (**56 bytes = 28 codes**), +0x38 dest, +0x3C text pointer, +0x40.. state; calls mapper A with width 0xD8 (216 px) |
| typer | `0x080734D4` | copies one 2-byte unit per tick (`ldrh`, so text must start on an even address; the end test reads the byte after each unit). A unit equal to `*(0x02008FC0)` (= ROM `0x080E21D8`, `∴`) is replaced by the player name (`*(0x03002A90)+0x78`, 12 bytes) |
| mapper ×5 | A `0x080282B8`, B `0x0802844C`, C `0x080285D4`.., D `0x08028FB4`, E `0x08029110` | code 0x8140-0x8396 → `idx = (hi-0x81)*192 + lo-0x40`; above → kanji list `0x3C0` (index 0x1E0+); `<= 0x813F` → glyph 0. Index goes into a glyph pool (`*(0x030028C0)+0x10`, ≤ 0x3F entries); width subtracted from the budget, from `width[idx]` or 8 when the 4th argument is set |
| widths | ROM `0x8A0`, 1056 bytes | 8 (Latin, digits, small kana, much punctuation) or 12 |
| blitters | `0x08028978` (dialogue), `0x08027C80` (variant) | glyph = `font + idx*128`, 16x16 4bpp, tiles TL BL TR BR; written in 4 px (halfword) columns. BIOS CpuSet also copies glyphs for some views |
| font | archive #1135 at `0x083F4E44`, 0x21000 bytes | 1056 glyphs; palette: bg 4, ink 7, shadow 5 (right and below); ink rows 3-14 |

Other fonts in the archive (#1132 8x8, #1133/#1134 8x16) were not read on the dialogue path.

## English: pair glyphs — verified in game (marker build, `rpg_start`, `comic_jin1`)

`tools/font.py`, no code changes:
- English is stored as ASCII, one byte per char. The five mapper literals `0x813F` (`0x2836C 0x284F8 0x28614 0x2902C
  0x29180`) become `0x1F`, so an ASCII pair hi:lo takes the 0x81-0x83 formula; in u16 arithmetic that gives a unique
  index 46,848-65,022.
- A 12 px glyph showing both letters (6 px each, `fonts/font6.txt`, drawn for this project) is written at
  `font + idx*128` = ROM 0x9ACE44-0xBE4DC4.
- The width table moves to ROM `0x800000` (64 KiB, the original 1056 entries then 12 everywhere); its seven
  pointers (`0x27D80 0x28448 0x28558 0x28630 0x28A7C 0x29108 0x291E0`) are repointed.
- Encoder (`font.encode`): non-ASCII chars (`∴`, `…`, `♪`) stay 2-byte SJIS on an even offset (a space is
  inserted before them if needed); the result is padded to even length so the NUL starts a unit.

Budgets: a dialogue line is 216 px = **36 chars** (marker line `120/43c The quick brown fox jumps ov` fills it
exactly). Code buffer limit 56 bytes per line is not reached by 36 chars.

## Width gate — verified in game (2026-11-17), budgets in `budgets.json`, lint `tools/lint.py` (run by `check.py`)

| Variant | Budget | Evidence |
|---|---|---|
| dialogue line (op 0x00) | 216 px = 36 chars; box shows **2 lines** | marker `120/43c` fills it; flags 0x0000 new box, 0x0400 clear, 0x0200 next line: past line 2 it waits for A and **scrolls up one line** (`120/7d8, 7fc, 828`), so runs of any length work; the wait arrow sits under the text |
| choice (op 0x01 fields) | 35 chars | ruler build: 36 visible, but the fixed dashed highlight ends at x=218, cutting the 36th |
| comic chapter title (op 0x13) | 34 chars per row | ruler build, `comic_jin1` |
| credits | 20 chars (120 px), ≤ 38 bytes | ruler build: clipped at x=120 for headings and names alike (pair glyphs draw at 6 px in both; the JP headings used an 8 px font) |
| speaker name tag | player: 6 fullwidth chars; NPC (character-table name, ASCII): 12 chars = 6 codes, 3 px letters | `tools/lua/setname.lua` poked `ＷＷＷＷＷＷ` into the name at `rpg_start`: fits its tab; NPC tags need the tagfont hook (§Speaker tags) |
| ROM strings | the Japanese **pixel** width (`font.jp_px`: ROM width table, 8 px for fullwidth Latin/digits/ー/small kana) and ≤ the JP byte length | construction: replacing text never gets wider; menus that need more get a measured `ids` entry in `budgets.json` |
| in-place strings (noptr) | ≤ original bytes and px | construction |
| wide rows | name 6, favourite word 4, grid row 14 (cells); default phrases 8 = **guess** (shown on screens not yet warpable; lint warns) | create_name / create_word fields |

Glyph torture line (`tools/torture_build.py`, all of 0x20-0x7E plus double spaces on `e2520_0043c` and its two
choices): every glyph and both double spaces render, `work/qa/tort/z.png`. Markers are now cut to these budgets
(`build.MARKER_CHARS`; ROM strings to their JP px), and `lint.py --all` over the marker text is clean (test).

### Name entry fix

The name and word fields start filled with the **empty-slot sentinel** `≠` (ROM `r077c94`, copied one code per
slot by `0x08028714`; the entry code tests for it). As a marker string it became `77`, so every blank slot read
`77` and the stored name kept ASCII pairs. It is now `data`; with it, blank slots show and the name is all
fullwidth SJIS (`７` from the widened grid), tag clean (`rpg_start`).

### Name entry (marker tour 2026-11-17, second session)

- The **visible grid is graphics** (kana still drawn in the marker build); the pointered rows at `0xEEC4C`
  (21 rows of 14 codes: blank, hiragana ×5, blank, blank, katakana ×5, blank, blank, alphanumeric ×5, blank) only
  give the code a cell enters. They and the default names/words (`0xEED68-0xEEDE8`) are now `"wide": true` rows
  (`text.py WIDE/WIDE_IDS`): English in ASCII, the build writes fullwidth SJIS (`font.widen`), `max` in characters
  (grid row 14, name 6, favourite word 4, phrases 8 = guess). The grid tiles need a graphics redraw (phase 8) to
  match whatever English rows are chosen.
- RAM name buffer: `82 56` then `37 37 ...` before the sentinel fix (above); the entry-screen copy is at IWRAM
  `0x030043CC`. Speaker tag (`0x08072F18`) measures every code as 8 px (width 0x30), which is why names stay
  fullwidth SJIS.
- Credits end "おしまい" = four one-code strings r075e38-r075e44, each drawn alone in a 16 px cell
  (`0x08029260`, width 0x10): at most 2 ASCII chars per cell.

## Speaker tags and small headers: the 8x8 font (phase 8, 2026-11-17; `tools/tagfont.py`, `fonts/font3.txt`)

Found in phase 8: every NPC speaker tag and the choice header "Which?" (r0e20c0) showed tile garbage in the full
build, though the player's tag was fine.

- **Where the name comes from:** the tag routine `0x08072F18(r0 = character id, .., r2 = name, r3 = table)` takes
  the name from the character table at ROM 0x45A0 (0x58-byte records, the same name field the VRX profile shows;
  `r00493c` "Komachi" for Komachi). The player's tag passes the name buffer. It copies 6 codes (`0x08028714`) and
  calls mapper A with width 0x30 and the 4th argument 1 (8 px per code), so the tag holds **6 codes**.
- **Two text systems:** system 1 (struct `0x030028C0`: +0 8x8 font `0x083E2244`, +4 8x16 font `0x083E5E44`,
  +0xC 16x16 font `0x083F4E44`, pool pointer at `0x030028D0`) with blitters `0x08027BBC` (8x8),
  `0x08027BFC` (8x16), `0x08027C3C`, `0x08027C80` (16x16 variant), `0x08027F90` (8 px cells: 8x16 for idx <=
  0x1DF, left half of the 16x16 glyph above), `0x08028978` (dialogue); system 2 (struct `0x030028E0`, mappers D
  `0x08028FB4` / E `0x08029110`, draw `0x08028890`) with copies `0x080288B8` (8x8), `0x080288F8`, `0x08028938`.
- **The bug:** the 8x8 blitters read `font8 + idx*32` with no range check. A pair index (46,848-65,022) lands
  1.5 MB into archive data. The tag and "Which?" (mapper D, width 0x20) both draw with the 8x8 blitter.
- **The fix (code hook):** the entry branch at ROM 0 jumps straight to 0x200 (it used to slide through zero
  words 0xC0-0x1FF), which frees 0x120-0x1FF; a 32-byte Thumb hook at 0x140 returns `TABLE + (idx-46,848)*32`
  for pair indices and the original address otherwise; both 8x8 blitters call it (`0x27BDA`, `0x288D4`). TABLE
  (ROM 0xF00000, 581,600 bytes) holds one 8x8 tile per pair: two 3 px letters (`fonts/font3.txt`) at x 0 and 4,
  shadow right and below. So a tag holds **12 letters** (6 codes), "Komachi" fits. Verified in game:
  `rpg_start` tags "Komachi", header "Which?" (`work/qa/cmp_en2`, `work/qa/probe/hdr2`).
- Player names stay fullwidth (8 px letters, 6 cells) because name entry and the save data hold 6 codes; D10.
- Probe `work/qa/probe/bigidx.lua` (any narrow blitter receiving a pair index) was run over all warp scenes.
