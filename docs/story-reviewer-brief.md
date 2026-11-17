# Story reviewer brief - Vattroller X (GBA)

You read one chapter (or one part of a long chapter) of a JP->English fan translation straight through, in story
order, the way a player meets it. Per-batch reviewers already judged single lines with +-2 lines of context; your job
is what they can't see. Read-only: no edits, no git, no subagents. Return the report as your final message.

## Inputs (all pasted below this brief)
- The chapter text: every line in story order (event file order, then line order), `>> id | JP` / `   EN`. There is no
  speaker column: infer speakers from context. `∴` in JP and `[name]`/the player's name in EN is the player's name.
  Read ALL of it before judging.
- `docs/synopsis.md` (plot, who is who, late reveals), `docs/style-reference.md` (voice per character), `glossary.md`
  (rulings at the top).

## Constraints the translation works under (not issues)
- Dialogue lines hold at most 36 characters; boxes are 2-3 lines. Short ROM labels (menus, names) are cut to fit JP
  pixel widths and are already tracked; do not report abbreviations in labels.
- Song lines drop the note sign and use "~". Honorifics are kept for names (decision D1).
- Event files are in file order, which is close to but not always exactly the order a player meets them; side events
  and town NPCs are independent scenes. Do not report a jump between two files as a continuity break.

## Judge, across the whole chapter
- Continuity: each line follows from the one before; setups, callbacks and references back are kept; who knows what
  stays coherent; nothing gives a later reveal away early.
- Voice: each character sounds like the same person all chapter and matches their style-reference row: speech quirks,
  register, how they address others. Name the line where a voice drifts or goes neutral.
- Emotion: anger, fear, grief and comedy beats are as strong as the Japanese; a running gag keeps its punchline.
- Accuracy only where a line breaks one of the above; single-line accuracy was reviewed already. Also flag a wrong
  name, a wrong number ("1th"), or an awkward stock phrase.

## Report
### Issues
#### Critical (continuity break, reveal given away, wrong speaker)
#### Important (voice drift or flattened, emotional beat lost, setup or callback dropped, joke dead)
#### Minor (deferred to the polish pass)
Each: `id - JP gist - problem - suggested EN`. Keep suggested EN within 36 characters per line.
### Assessment
End with exactly one line, tab-separated, nothing after it:
`ASSESSMENT<TAB>ok<TAB><one sentence>` (no Critical/Important) or `ASSESSMENT<TAB>issue<TAB><one sentence why>`.
