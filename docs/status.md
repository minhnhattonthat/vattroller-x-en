# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 3. Identity build (phase 2 debug tool done). Last build: none yet.
- **Done:**
  - Step 0: rom.sha1 pinned, MesenCE 2.2.1 + GBA BIOS in tools/mesen, smoke boot + Start input + Lua log work, pre-commit hook rejects a failing test, guard hook blocks the `sed -i` canary.
  - Phase 1: no earlier English patch found. Text is plain Shift-JIS. Resource archive at 0x100000 (2714 files, (ptr,size) table, contiguous, relocatable) — `docs/re/archive.md`. Event scripts are 4-aligned `op,size` command streams; text ops 0x00/0x01/0x06/0x13 — `docs/re/script.md`. ~3,580 pointered strings outside the archive — `docs/re/text.md`. SRAM save, ROM can grow past 8 MiB. Static graphics-text sweep done (G1-G9 in `docs/re/graphics.md`).
  - Phase 2: `tools/debug/warp.py` + `warp.lua` + `scenes.json` (52 scenes) reach title, title menu, shelf (all 16 books force-unlocked), book prompts, all 7 RPG character-creation screens, every comic chapter card and おわり/終 room (7 books), デスロール編, endings 1-3, credits, オリジナル再スタート, the tutorial battle, RPG intro rooms and 10 RPG town/shop/gym/stadium rooms — all from a cold boot, proof sheets `docs/screenshots/phase2_warps*.png`, states in `work/states/`. RAM/code map in `docs/re/debug.md` (room loader, player struct, room table 0x0BC20, script interpreter + jump table, op 0x05 teleport, op 0x1D battle, op 0x06 conditional, flag/var stores).
- **Next:** Phase 3 identity build: archive + script-stream rebuild byte-identical (note op 0x06 is a conditional block whose `+4` field is a byte skip — a length inside the stream; check every op for stream offsets/lengths before relaying text). Debug-tool follow-ups (non-blocking, see `docs/re/debug.md` §Gaps): RPG free control after the ~20k-frame intro, story flags so shopkeepers appear, field menu + submenus, shop buy/sell, save and `つづきから`, battle auto-win (`GOD`). Add them to scenes.json before phase 8.
- **Open bugs:** none.
- **Waiting on the user:** keyboard input in the Mesen GUI not checked by hand (no user at the terminal); emu.py writes default key mappings. Graphics survey still needs its tour rows (marker build, debug-tool warps). RPG-mode menus and shops are not yet warpable (story flags), non-blocking.
