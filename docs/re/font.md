# Fonts

**guess** (from the static sweep, not yet hooked on the draw path):

| File | Size | What |
|---|---|---|
| #1132 | 0x3C00 | 8x8 font in SJIS row order: symbols, fullwidth digits, Latin, hiragana, katakana |
| #1133 / #1134 | 0x7800 each | 8x16 font split in top/bottom halves (4bpp, background 0x4) |
| #1135 | 0x21000 | main dialogue font, ~12x12 glyphs incl. kanji (4bpp, background 0x4) |

Dialogue and menus draw fullwidth ~12 px cells (screenshot `work/qa/r1/f001320.png`: 「この本を　はじめますか？」).
English needs a VWF or a narrow-cell font: decide in the phase 5 engine spike after hooking the SJIS->glyph routine.
