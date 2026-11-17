# Translator brief - Vattroller X

Read first: `glossary.md` (rulings, style rules, names; binding), `docs/style-reference.md` (voice table, paired
examples), `docs/synopsis.md` (chapters, who is who, reveals), then your batch's `build/terms_bNNN.txt`.

## Input
`work/tl/bNNN.tsv`: `id<TAB>speaker<TAB>form<TAB>limit<TAB>jp`, in game order (file by file).
- form for dialogue: `box` = starts a new 2-line box, `+` = next line (past line 2 the box waits for A and scrolls
  one line), `clr`/`clr+` = clears the box first. Other forms: `title` (comic chapter title), `choice`, `string`
  (menus, item and arm names, help text), `string/wide` (shown fullwidth: limit in characters), `credit`, `noptr`.
- limit = characters per row. Dialogue 36, choices 35, titles 34, credits 20; strings: the Japanese pixel width.
- `∴` is the player's name (up to 6 wide letters = 12 characters of width): keep every `∴`, budget 12 for it.
  `[XX]` byte codes must also survive unchanged.

## Output
`work/tl/bNNN.out.tsv`: `id<TAB>English`, every id once, same order, written with the file-write tool.
One row = one line on screen: no `\n`. Plain ASCII. A sentence may flow across `+` rows; never move text into
another `box`.

## Check
`python -X utf8 tools/batches.py check bNNN` until it prints OK, then `python -X utf8 tools/batches.py merge bNNN`.

## Quality bar
- Natural English that a kid playing in 2002 would enjoy; keep jokes and each speaker's tic (glossary).
- Names and terms exactly as the glossary spells them.
- No suffix glued on a variable; no "a/an" right before `∴`.
- Don't shorten terms to fit: rephrase.

## Report
`NEW TERM: jp -> en`, `UNSURE: id - note`, `CUT: id - what was dropped`.

## Notes from earlier batches
- Solo workflow (Orca worker, no subagents): `python -X utf8 tools/tl_pair.py show bNNN 1 75` and `76 150`
  (keep each print under ~4 KB: the context-mode hook swaps bigger output for a search stub), write all 150 rows
  of `work/tl/bNNN.en.txt` in ONE file-write (appending with the shell makes the harness echo the file back),
  `tl_pair.py put bNNN work/tl/bNNN.en.txt`, `batches.py check bNNN`, fix with Edit, `batches.py merge bNNN`.
- Town NPC / counter batches repeat a lot: `python -X utf8 tools/tm.py show bNNN` lists only rows with no exact-JP
  match in the merged script; write those to a scratch file, `tm.py put bNNN file` fills the rest and checks.
  TM lines are context-free: read the filled rows around a hit that continues a sentence (b058-b061 had
  `使えるはずだ` -> "Hunt-type Arms." and a "Yes, I do" choice that needed fixing).
- The glossary check sees one batch only: a box split across two batches needs the term in each half.
- A row flagged `box` starts a new box: never let a sentence spill from a `+` row into the next `box` row.
- The glossary check is per box: the English term must appear somewhere in the same box as the JP term.
- Choices come in pairs after a question; translate each as a short reply (<= 35).
- Most first drafts overflow by 1-4 chars: count before writing (36 = this line's length, roughly ->|).
