# Event scripts (archive files #2475-2711 and others)

**verified** by byte layout over all 11,062 text commands (each `size == align4(8 + len + 1)` and a NUL at `len`), and
by walking forward from every text command: 28,173 commands chain cleanly. Tool: `tools/script_fmt.py`.

## Command stream

4-byte-aligned commands, little-endian: `u16 op, u16 size` (bytes, header included, multiple of 4), then arguments.
Since every command carries its size, a stream can be re-laid with longer text **if no command holds a byte offset
into the stream** (jumps/labels). Not checked yet: find branch opcodes and their target encoding in phase 3/4.

Event files start with a header of nested sections (example #2475 at 0x74C850: `01 00 02 00 02 00 20 00 11 00 ...`,
section sizes at +0x0C and +0x20, commands from +0x3C). Only 194 files walk cleanly from one start to the file end;
the others hold several sections. Section layout: phase 3/4.

## Opcodes carrying text

| op | size | layout | example |
|---|---|---|---|
| 0x00 | `align4(8+len+1)` | `u16 0, u16 size, u16 flags, u16 len, SJIS[len], 00, pad` (pad bytes are leftover garbage, not zero) | 0x74FFF4 「小さな島に　住んでいたんだけど」 |
| 0x01 | 0x3C typ. | choice option(s): `u16 1, u16 size, u16 ?, u16 ?` then fixed-width SJIS field(s) | 0x750854 「わからないから　教えて」 |
| 0x06 | 0x200 | choice menu container; holds op 0x01 / 0x07 / 0x0A sub-commands | 0x7958C0 「アームセットをしゅうりょうする」 |
| 0x13 | 0x30 | comic-mode chapter title: two NUL-terminated SJIS fields | 0x753150 「バトローラージン」 |

Text-command `flags`: 0x0200 (6562), 0x0000 (4409), 0x0600 (53), 0x0400 (37), 0x1C00 (1). **guess:** 0x0200 =
continue in the same box / wait, 0x0000 = new box; check in the marker build.

Each dialogue line is its own command (one box line per op 0x00); a box holds 2-3 lines of up to ~19 fullwidth chars.
Other ops seen around text: 0x0A size 8 (portrait/speaker?), 0x0B size 4 (wait / end of box?), 0x11 size 0x10-0x18,
0x30 size 8, 0x3B, 0x27. Meaning: phase 4/5.
