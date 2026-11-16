# Skill gotchas

One line per gotcha: the reference file it belongs in, then the fact.

- references/setup.md + scripts/fetch_emu.py: `fetch_emu.py gba-bios` 404s; retrobios moved the file to `bios/Nintendo/Game Boy Advance/GBA_bios.rom` (same SHA-1 300c20df...).
- SKILL.md Step 0: plugin hook did not fire on Windows/Orca; adding the hooks block with `$HOME/.claude/plugins/marketplaces/...` to .claude/settings.json made it live mid-session.
