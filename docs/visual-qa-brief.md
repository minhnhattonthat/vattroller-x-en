# Visual-QA reviewer brief - Vattroller X (GBA)

You review contact sheets from a translated build's QA tour and give each one a verdict. Read-only on everything
except your one verdict file: no edits to the repo, no git, no subagents.

## Inputs (in your dispatch)
- A chunk file: one `id<TAB>path` line per sheet. Read every sheet in it; none may be skipped.
- Your verdict file: `work/qa/verdicts/<chunk>.tsv`.
- Optional: the original ROM's sheets (`work/qa/tour_jp/`, same ids) and `glossary.md`.

## How to look
- Read each sheet whole first. Where text is small, zoom into it with
  `python -X utf8 $SKILL/scripts/sheet.py SHEET.png --crop x,y,w,h --zoom 3 --out <scratch>.png` and read that.
- When something looks wrong, open the same id from `tour_jp/` (`sheet.py EN.png --compare JP.png`). If the
  original shows the same thing, it is the game's own behaviour: `ok`, with a note.
- Zoom into every Yes/No prompt, selection box, menu row and speech bubble: a few pixels of misalignment don't show
  at sheet scale. To measure one: `python -X utf8 $SKILL/scripts/inkbox.py SHOT.png x,y,w,h`.

## Judge
An `issue` is any of:
- Japanese still visible;
- text overflowing a box, clipped by a frame, or running off screen;
- text off-centre where the original centres it: an option in its selection box or cursor brackets, a label, a bubble;
- garbage tiles, wrong or missing glyphs, a strike or stray pixels across letters;
- broken line breaks: a word split mid-line, a page ending mid-sentence, a one-word last line;
- an empty box where text belongs;
- a name that differs from `glossary.md`.

Standing non-bugs, `ok` (the controller adds the game's own below):
- text still typing out, a box mid-fade or mid-scroll, a cursor caught mid-blink;
- a map or scene still loading after a warp;
- anything identical in the original's sheet.
- A dialogue box whose lines look doubled or overprinted for one frame: the game scrolls the box one line by
  redrawing it, and a frame caught mid-redraw shows both lines (the original does the same, checked 2026-11-17).
- English dialogue is drawn as two 6 px letters per 12 px glyph (a deliberately narrow font): narrow letters
  are the engine, not a bug. Speaker tags and small headers ("Which?") use an even smaller 3 px font.
- The player's name is fullwidth (wider letters) in tags and dialogue: by design (6-cell name buffer, D10).
- Song lines end in "~" instead of a note symbol (style rule).
- The Ganbarion boot logo (the developer's trademark, katakana ガンバリオン) and the title logo with its katakana
  subtitle バトローラーエックス stay as they are (D5: no official English logo). The title's *credit line* below
  "PRESS START" is NOT part of the logo: Japanese there is an issue.
- Every warp boots through the logos, title and bookshelf, so these frames repeat on many sheets: judge them the
  same way each time.

## Verdicts
Write your verdict file once you have read every sheet, one line per id in the chunk:
`id<TAB>ok|issue<TAB>what and where` (for an issue: which tile, which text, what is wrong).
Then return a short summary: counts, and the issues one per line.
