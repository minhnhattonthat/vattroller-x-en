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
| D8 | 2026-11-17 | Publishing | publish, don't | Never `gh release create`, never change repo visibility; the run ends at a built and verified release zip. Pushing to main is allowed. |
