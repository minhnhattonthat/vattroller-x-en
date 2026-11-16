# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool (phase 1 recon done). Last build: none yet.
- **Done:**
  - Step 0: rom.sha1 pinned, MesenCE 2.2.1 + GBA BIOS in tools/mesen, smoke boot + Start input + Lua log work, pre-commit hook rejects a failing test, guard hook blocks the `sed -i` canary.
  - Phase 1: no earlier English patch found. Text is plain Shift-JIS. Resource archive at 0x100000 (2714 files, (ptr,size) table, contiguous, relocatable) — `docs/re/archive.md`. Event scripts are 4-aligned `op,size` command streams; text ops 0x00/0x01/0x06/0x13 — `docs/re/script.md`. ~3,580 pointered strings outside the archive (0x0-0x20000, 0x73000-0x7C000, 0xE0000-0xF2000) — `docs/re/text.md`. SRAM save, ROM can grow past 8 MiB. Static graphics-text sweep done (G1-G9 in `docs/re/graphics.md`).
- **Next:** Phase 2 debug tool: find the RAM for current map/event id and story flags (ramsearch/watch probes), build `tools/debug/warp.lua` + `tools/debug/scenes.gba` (scene list incl. comic mode chapters, shops, menus, name entry, battles, ending/credits), prove each with a cold-boot shot. Then phase 3: archive + script-stream identity rebuild (check for jump opcodes holding stream offsets first).
- **Open bugs:** none.
- **Waiting on the user:** keyboard input in the Mesen GUI not checked by hand (no user at the terminal); emu.py writes default key mappings. Graphics survey still needs its tour rows (marker build, debug-tool warps).
