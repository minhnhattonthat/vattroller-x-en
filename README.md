# Vattroller X English translation

Unofficial English fan translation of **Vattroller X** (Game Boy Advance, Bandai, 2004; developed by Ganbarion): the
source text and tools that build the patch.

**Just want to play?** Download the patch from [Releases](../../releases) and follow its README. This repository holds
no game data you can play; you need your own dump of the Japanese game.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## Translation status

| Part | Status |
|---|---|
| Story and dialogue (comic mode, RPG mode, side events, town NPCs) | Translated |
| Menus, items, Arms, Armalets, V Skills, shops, system messages | Translated |
| Graphics with text (menu labels, help bubbles, world-map labels, signs, book spines, rule cards) | Translated |
| Name entry | Translated (Latin keyboard pages replace the kana pages) |
| Credits roll | Translated |
| Title logo, Ganbarion boot logo | Left in Japanese (logos, no official English version) |

Known issues: link-cable features (multiplayer battles, V Skill trading) are untested; see [Issues](../../issues).

## Base ROM

Apply the patch to `Vattroller X (Japan).gba` (No-Intro name), 8388608 bytes:

| Hash | Value |
|---|---|
| CRC32 | `E368A67A` |
| MD5 | `ac4f3b73a920ddaabc9f9e003c92e02b` |
| SHA-1 | `035ae457c23d564ad97392572ab8a422abfce96e` |

The patch is BPS (Flips, beat or RomPatcher.js). The patched ROM is larger than 16 MiB, which is expected; the patched
CRC32 is in the release README. Tested in MesenCE 2.2.1. Start from a cold boot, not from an old savestate.

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `tools/` | Python build chain: extract, insert, lint, release. |
| `tests/` | pytest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |
| `.codex/agents/`, `.opencode/agents/` | Subagent types (translator, reviewer, visual QA, playtester, graphics) for Codex and opencode; Claude Code gets them from the plugin. |

## Build your own patched ROM

Needs Python 3.12+ and your own dump of the Japanese game.

```sh
git clone https://github.com/minhnhattonthat/vattroller-x-en
cd vattroller-x-en
# copy your dump to: rom/Vattroller X (Japan).gba
#   (8388608 bytes, SHA-1 035ae457c23d564ad97392572ab8a422abfce96e; the build refuses any other dump, see rom.sha1)
python -X utf8 tools/build.py                          # -> build/vattroller_x_en.gba
python -X utf8 tools/check.py                          # tests + text lint
```

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is Bandai's and is included only so the
translation can be checked against it. Vattroller X is (c) Bandai / Ganbarion / Tenya Yabuno; this project is not
affiliated with them. Do not share patched ROMs.

The translation was made with extensive AI assistance (Claude by Anthropic). Corrections are very welcome.
