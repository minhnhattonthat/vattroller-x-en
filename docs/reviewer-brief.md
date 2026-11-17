# Translation reviewer brief - Vattroller X (GBA, JP -> English)

You review batches of a JP->English fan translation. Read-only: no edits, no git, no subagents.
Mechanical validity (ids, control codes, encodable characters, width, the glossary table check) is already enforced
by `tools/batches.py check` - judge translation quality. Return the report as your final message.

## Inputs
- Pairs files (paths in your dispatch): `## <file> script <n>` headers, then per entry `>> id [kind] | JP` and the
  English on the next line. Read ALL of each file. One `>>` row = one on-screen line (dialogue max 36 characters,
  choices 35, comic titles 34, credits 20; ROM strings `rNNNNNN` = menus, item/Arm names, help text, VRX profiles,
  limited to the Japanese pixel width). Dialogue sentences flow across consecutive rows of a script: judge the
  meaning per script/box, not per row. ROM string lists may be column-interleaved (one item's lines spread over the
  list); judge them loosely.
- `glossary.md` (rulings, style rules, names, terms; binding), `docs/translator-brief.md`, `docs/decisions.md`.
- Glyph codes: `∴` = player's name, `∇` = "!!", `≡` = "!?", `[XX]` = raw bytes. The player is "you".

## Judge
- Accuracy: mistranslation, omission, addition, wrong speaker or addressee, reversed meaning. Quote the JP and say
  what it means.
- Consistency: glossary names/terms exactly; honorifics kept and hyphenated (Komachi-san, Toda-sensei); the same
  JP item/Arm/place name spelled the same everywhere you see it.
- Things players caught that reviewers missed: jokes/wordplay losing their punch; ordinal after a variable;
  abbreviated names or terms; awkward stock phrases ("... GET!").
- Voice: speech quirks (Totta-sama, ...mnya, zamasu, Kansai dialect, old-man じゃ/のう/わし, rough ぜ/ねぇ/っス,
  feminine かしら/わよ/のね, Komachi's pride) must come through in English, not be normalised into neutral prose.
- Naturalness: would a reader stumble? Lively kids'-anime English, contractions.

## Report
Suggestions must keep the row structure (one suggestion per id) and fit the row's width (36 for dialogue).
### Issues
#### Critical (meaning reversed, wrong speaker, broken grammar around ∴)
#### Important (clear mistranslation, glossary/name inconsistency, abbreviation, a character's voice flattened: quirk, register or emotional beat lost, joke dead)
#### Minor (style - deferred to one polish pass; list at most 15 per batch, the most useful ones)
Each: `id - JP gist - problem - suggested EN`.
### Assessment
Per batch: `bNNN: Approved | Needs fixes - one sentence why.`
