# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

All answered up front by the owner in the Orca run brief (2026-11-17), applied to every one-shot project.

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-11-17 | Honorifics and name order | keep (-san), drop; JP or Western order | Keep honorifics; Western order (given name first). Owner's standing answer. |
| D2 | 2026-11-17 | Romanization source for names | official art, earlier patch, Hepburn | Official English names where they exist, else an earlier fan patch, else Hepburn without macrons. |
| D3 | 2026-11-17 | Credits | stay Japanese, translate | English. |
| D4 | 2026-11-17 | Abbreviations | engine work first (default), abbreviate | Default: full names and terms, engine work first; abbreviate only as a flagged last resort. |
| D5 | 2026-11-17 | Graphics text left in Japanese | none (default), list | Translate all (titles, menus, banners, cards); leave the Japanese logo only if it has no official English version. |
| D6 | 2026-11-17 | Specs and plans | need approval, pre-approved | Pre-approved: keep going through every checkpoint without asking. |
| D7 | 2026-11-17 | Existing saves / savestates | user's saves, none | None provided; build the debug tool as usual. |
| D9 | 2026-11-17 | Register, sound effects, title terms (pre-approved run: skill defaults, decided by the agent) | literal, natural; keep or translate SFX; Battroller / Vattroller | Natural kids'-anime English with each character's verbal tic kept; SFX in English; the title's own spelling "Vattroller" drives バトローラー/バトローリング/バトリーグ (Vattroller, Vattrolling, Vattleague). Owner can overrule; all are glossary rows. |
| D8 | 2026-11-17 | Publishing | publish, don't | Never `gh release create`, never change repo visibility; the run ends at a built and verified release zip. Pushing to main is allowed. |
| D10 | 2026-11-17 | Default player name ツバサ (r077ad4), which needs 7 letters in a 6-cell name (pre-approved run: decided by the agent after the phase-6 review rejected "Sora"; owner may override) | "Tsubasa" via engine work; "Tubasa" (Kunrei spelling, 6); "Sora" (another name, same meaning) | "Tubasa". The name buffer (`*(0x03002A90)+0x78`) is 12 bytes = 6 fullwidth codes, the speaker tag draws 6 codes at 8 px, and name entry, save and status screens read the same buffer; an ASCII pair-glyph "Tsubasa" was tried in game and garbles the speaker tag (`work/qa/tsubasa/`). Engine support would mean rewriting every name consumer and moving save data, for a default the player renames. "Tubasa" keeps the character's actual name (D2 spirit), "Sora" did not. |
| D11 | 2026-11-17 | Ganbarion boot logo (katakana ガンバリオン) and the title logo's katakana subtitle (pre-approved run: decided by the agent under D5) | redraw, keep | Keep: both are logos with no official English version (D5); the developer's logo is its trademark. The title-screen credit line under PRESS START is text and gets redrawn (graphics.md G10). |
| D12 | 2026-11-17 | Small-font Yes/No box (r0e20b0/r0e20b8: book prompt and other confirm boxes; agent's call, pre-approved run) | "Yes"/"No", " Yes"/"  No", " Sure"/"  No", "  OK"/"  No" | " Sure"/"  No": the 3 px tag font puts letters on a fixed 4 px grid, so a 3-letter "Yes" is always 4 px off-centre in the 3-cell box (inkbox 11/15); a 4-letter word with one leading space centres (11/11), and "Sure" reads naturally after every question that uses the pair. |
| D13 | 2026-11-17 | Name-entry keyboard (かな / カナ / ABC pages; agent's call, pre-approved run) | redraw the kana grids as new Latin glyphs; copy the existing ABC glyph cells into the kana pages | Copy (`tools/namegrid.py`): page 1 "abc" = the ABC page lower case first (the default page now shows Latin), page 2 "!?" = digits and symbols taken from kana-page cells (! ? & ~ ー ・ + - × =), page 3 "ABC" unchanged; けす → "DEL" (letters from END). No new glyph art in the grid, codes always match the glyph copied; kana names are no longer possible (English release). |
| D14 | 2026-11-17 | Bookshelf spines (G11; agent's call under D5, pre-approved run) | redraw every spine, redraw titles only | Titles only: the デスロール spine becomes "DEATH ROLL" (turned 90 deg, read top to bottom, `gfx.sheet_433`); the small バトロラ stack on the comic spines and the Ⓥ バトローラーX stack on the RPG save books are the series logo, kept like the title logo (D5/D11). JIN I-IV / RYO / TOTA / SHU / NEW are already English. |
