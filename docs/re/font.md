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

## Open (phase 5)

- **Speaker name tag** (`0x08072F18`): copies the player name (12 bytes) and calls mapper A with width 0x30 and
  the "count every glyph as 8 px" flag, so a 12 px pair glyph overruns its 8 px slot (garbage in the marker build,
  where the name is `777777777777` because the name-entry grid is itself a marker string). Plan: keep player names
  as fullwidth SJIS Latin (the original 8 px glyphs, 6 chars = 48 px), i.e. the name-entry grid offers fullwidth
  letters, and check the default names.
- Box variants still to measure: lines per box, choices, comic titles, menus/list fields, credits, VS labels.
