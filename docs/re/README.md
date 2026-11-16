# Reverse-engineering notes

One file per subsystem (text engine, pointers, compression, font, graphics). Mark every finding with how far it is
proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely (byte pattern, another game, an earlier patch's notes). Promote it to verified
  before code depends on it.

Addresses are for the dump in `rom.sha1` unless a note says otherwise.

| File | Covers | State |
|---|---|---|
| archive.md | resource archive table at 0x100000, file groups, compression, free space, save type, writer | verified (layout, no pointers into event files), guess (other files) |
| script.md | event file/page/script layout, command links (NEXT, op 0x06 THEN/ELSE), text opcodes | verified (identity + relayout in game), guess (text flags) |
| text.md | Shift-JIS encoding, string regions, pointer rule, credits table, extraction to `script/` and coverage sweep | verified (roundtrip + coverage test) |
| font.md | font files #1132-1135 | guess (sweep only) |
| graphics.md | graphics-text survey (static sweep done, tour rows pending) | sweep verified |
| debug.md | warp tool, rooms, shelf/books, player struct, script interpreter, teleport/battle ops, flag stores | verified (warps), guess (flags) |

Tools: `tools/archive.py`, `tools/events.py` (parse/rebuild event files), `tools/text.py` (dump/check/apply text), `tools/build.py`, `tools/script_fmt.py`, `tools/sjis_scan.py`, `tools/gfx_sweep.py`, `tools/ramview.py`,
`tools/debug/` (warp), `tools/lua/` probes (arcload, getfile, execlog, romreads, oplog, mash2).
