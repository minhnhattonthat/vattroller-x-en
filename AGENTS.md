# Vattroller X (GBA) English translation

Skill: translate-retro-game (Claude Code: plugin, enabled in .claude/settings.json; other agents: `<SKILL_DIR>/SKILL.md`; `$SKILL` = the directory holding its SKILL.md; `python tools/skill.py` prints it). Read it before ROM, text or QA work.

## Commands (run from repo root)
- Build:    `python -X utf8 tools/build.py`        -> build/vattroller_x_en.gba (checks the dump against `rom.sha1` first)
- Check:    `python -X utf8 tools/check.py`  (tests + lint; the pre-commit hook runs this; hooks: `git config core.hooksPath tools/hooks`)
- Smoke:    `python -X utf8 $SKILL/scripts/emu.py build/vattroller_x_en.gba --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Warp:     `python -X utf8 tools/debug/warp.py <scene> [--state] [--sheet]` (cold boot -> work/qa/warp/<scene>/scene.png; `--all --jobs 5 --state` regenerates every state; scenes: `tools/debug/scenes.json`, `--list`; docs/re/debug.md; never ask the user to play to a scene)
- Release:  `python -X utf8 tools/release.py` (patch + verify; never publish without the user)
- Clean:    `python -X utf8 tools/clean.py` (published projects: lists rebuildable/downloadable files; `--yes` deletes)

## Paths
- Original ROM: `rom/Vattroller X (Japan).gba` (gitignored; SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`). Emulator: this repo's own copy in `tools/mesen/` (MesenCE 2.2.1, https://github.com/nesdev-org/MesenCE/releases/download/2.2.1/Mesen_2.2.1_Windows.zip; gitignored; BIOS `tools/mesen/Firmware/gba_bios.bin` from retrobios `bios/Nintendo/Game Boy Advance/GBA_bios.rom`, SHA-1 300c20df...; settings in `tools/emu-config/`). Savestates: `work/states/`.
- Text: `script/events/e<file>.json` (dialogue/choices/titles), `script/rom/*.json` (pointered strings, credits, no-pointer strings); fields `id kind jp en status notes` (+ `flags`, `ptrs`, `max`). `python -X utf8 tools/text.py dump|check|stats` (dump never clobbers `en`; layout in docs/re/text.md). Width budgets per box variant: `budgets.json` (measured; lint `tools/lint.py`, run by check; table in docs/re/font.md §Width gate). Glossary: `glossary.md`. RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- Subagents: dispatch the agent types (translator, reviewer, visual-qa, playtester, graphics) shipped by the plugin as `translate-retro-game:<type>` (Claude Code), `.codex/agents/` (Codex) or `.opencode/agents/` (opencode), never general-purpose: their short tool list cuts each agent's start-up context from ~43k to ~9k tokens. Under Orca, nested workers are refused: do reviews yourself in a fresh read-only pass, or with `codex exec`.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- Gotchas: the plugin's guard hook did not load from the plugin; `.claude/settings.json` carries the `hooks` block pointing at the marketplace path. 8 MiB ROM, no EEPROM/SRAM/FLASH library string found (save type: see docs/re/).

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
