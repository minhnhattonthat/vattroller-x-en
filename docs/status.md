# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1. Research and recon (Step 0 setup done). Last build: none yet.
- **Done:** Step 0: rom.sha1 pinned (035ae457...), MesenCE 2.2.1 + GBA BIOS in tools/mesen, original ROM smoke boots to the title and Start reaches the new/continue menu (`tools/routes/boot.txt`), Lua probe logging works, pre-commit hook (`tools/check.py`) rejects a failing test, guard hook blocks the `sed -i` canary.
- **Next:** Phase 1 recon: earlier patches, text encoding (menu shows さいしょから / さいかい), pointer tables, compression, free space, graphics-text survey. Write findings in docs/re/.
- **Open bugs:** none.
- **Waiting on the user:** keyboard input in the Mesen GUI not checked by hand (no user at the terminal); emu.py writes default key mappings.
