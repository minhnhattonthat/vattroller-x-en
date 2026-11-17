# Translator brief - Vattroller X

Read first: `glossary.md` (rulings, style rules, names; binding), then your batch's `build/terms_bNNN.txt`.

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
- (none yet)
