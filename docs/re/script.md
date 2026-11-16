# Event scripts (archive files #2475-2711, one per room)

**verified**: `tools/events.py` parses all 237 event files (2,641 scripts, 34,317 commands, 11,070 text lines) and
rebuilds each byte-identically (`tests/test_events.py`, `tests/test_build.py`). Relayout verified in game: a stress
ROM with a fullwidth space appended to every line (227 files relaid and moved past 8 MiB) reached 7 warp scenes
(`rpg_start`, `comic_jin1`, `battle_tutorial`, `rpg_school`, `rpg_tutorial`, `deathroll`, `ending1`) with dialogue
and branches intact (`tools/stress_build.py`, then `warp.py ... --rom work/stress.gba`).
No archive file outside #2475-2711 holds Shift-JIS text, and no script command stream exists outside the archive.

## File layout

| Level | Layout |
|---|---|
| file | `u16 page count`, 10 bytes (keep), then pages back to back to the file end |
| page | `u32 size` (counted from this field), 8 bytes (keep), then scripts back to back to the page end |
| script | header: `+2 u16 0x24`, `+4 u32` offset of the first command, `+8 u32` script size; commands follow. `+4` is 0x24 everywhere except one script in #2604 (0x84: a 0x60-byte data block in the header) |

## Commands

`u8 op, u8 0, u16 NEXT, args`, 4-aligned, little-endian. Interpreter: `0x08030B80` (jump table `0x08030B98`, 0x43
ops, op read as a byte), command pointer `0x030063F4`; the main loop (`0x08030248`) advances by NEXT, then runs the
command.

- **NEXT is a relative link, not a length.** It equals the command's length except at the end of a then-branch,
  where the compiler patched it to jump over the else-branch. A data-only "script" (move routes, #2604, #2688) has
  NEXT = 0 and is copied as is.
- **op 0x06 (if)** `0x08031328`: condition type `+0xA & 0xFFF`; true → pointer `+= u16 +4` (THEN, always 0x14:
  the header length); false → `+= u16 +6` (ELSE) when `+0xA & 0x8000`, else falls through by NEXT. With the else
  flag set NEXT is never read and holds stale values (368 cases; 321 point mid-command): `events.py` keeps it as is.
  The skip helper `0x08030AF8` (`ptr += r0`) has one other caller, the main loop itself.
- **op 0x07 / 0x24**: save / restore the command pointer in RAM (`0x030063FC`): a loop mark, no stream offset.
- **op 0x0C**: end. Its NEXT is 4. Seven scripts end with two 0x0C (dead 4 bytes), kept.
- No other op holds a stream offset: a search over every (op, u16 field) for values that land on a command start
  found only op 0x06 +4/+6 (op 0x17 +4 hits are wait frame counts, multiples of 8).

Rebuild rule (`events.py`): commands are the nodes reached from the first command through NEXT / THEN / ELSE; a
node's bytes run to the next node start (so pad garbage and dead tails are kept); nodes are laid out in the original
order and every link is recomputed. Text can grow or shrink freely; a link must stay below 0x10000 bytes.

## Opcodes carrying text

| op | size | layout | example |
|---|---|---|---|
| 0x00 | `align4(8+len+1)` | `u16 0, u16 NEXT, u16 flags, u16 len, SJIS[len], 00, pad` (pad bytes are leftover garbage, not zero; new text pads with 0) | 0x74FFF4 「小さな島に　住んでいたんだけど」 |
| 0x01 | 0x18-0x48 | two choice options: `u16 1, u16 NEXT, u16 off2, u16 0`, field 1 at +8, field 2 at `off2`; each NUL-terminated, padded to 4 | 0x750854 「わからないから　教えて」 |
| 0x13 | 0x24-0x38 | comic-mode chapter title: `u16 0x13, u16 NEXT, u16 off2, u16 off3`; fields at +8, `off2`, `off3` (the third is always empty) | 0x753150 「バトローラージン」 |

op 0x01 / 0x13 layout **verified** as a file-format fact: every one of the 181 + 22 commands rebuilds byte-identically
from its own fields (`text.py check`); whether the game reads `off2` (rather than scanning past the NUL) is
checked in the marker build, since English changes the field lengths (`Node.set_fields` recomputes the offsets).

The "op 0x06 size 0x200 choice container" of the phase 1 notes (0x7958C0, #2593 +0x124) is a 0x14-byte if without
else: NEXT = 0x200 skips its then-branch, which holds the choice commands.

Text-command `flags`: 0x0200 (6562), 0x0000 (4409), 0x0600 (53), 0x0400 (37), 0x1C00 (1). **guess:** 0x0200 =
continue in the same box / wait, 0x0000 = new box; check in the marker build.

Each dialogue line is its own command (one box line per op 0x00); a box holds 2-3 lines of up to ~19 fullwidth chars.
Other ops seen around text: 0x0A size 8 (portrait/speaker?), 0x0B size 4 (wait / end of box?), 0x11 size 0x10-0x18,
0x30 size 8, 0x3B, 0x27. Meaning: phase 4/5.
