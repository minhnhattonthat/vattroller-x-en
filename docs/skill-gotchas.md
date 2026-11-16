# Skill gotchas

One line per gotcha: the reference file it belongs in, then the fact.

- references/setup.md + scripts/fetch_emu.py: `fetch_emu.py gba-bios` 404s; retrobios moved the file to `bios/Nintendo/Game Boy Advance/GBA_bios.rom` (same SHA-1 300c20df...).
- SKILL.md Step 0: plugin hook did not fire on Windows/Orca; adding the hooks block with `$HOME/.claude/plugins/marketplaces/...` to .claude/settings.json made it live mid-session.
- references/emulator-qa.md §Hooks: Mesen GBA Lua has `emu.read`/`emu.read16`/`emu.read32`/`emu.write`/`write16`/`write32` but no `read8`/`write8`; GBA registers are `emu.getState()["cpu.r0"]`..`["cpu.r15"]`.
- references/emulator-qa.md §emu.py: emu.py's `--mash` presses one key; games whose choice boxes start with nothing selected need a direction then A (this repo: tools/lua/mash2.lua). A mash script queuing L.press also fights any other script that waits on L.route_done().
- references/emulator-qa.md §Debug tool: for room-based games, the cheapest warp is swapping the room id at the loader's read (on_exec just before the ldrsh) plus script teleport ops for entry coordinates; a story script running when the room is swapped keeps running in the new room.
- references/pipeline.md §Extract: Python cp932 decodes 0x80/0xA0/0xFD-0xFF to the Private Use Area and IBM-extension duplicates (桒 FA E3) re-encode to the NEC code (ED 93); a decoder must emit [XX] for any char that does not re-encode to the same bytes, or the roundtrip test catches it late.
- references/setup.md: the template .gitignore's unanchored `rom/` also ignored `script/rom/` (the ROM-string scripts went uncommitted through phase 4); anchor it as `/rom/`.
