# Text encoding and string locations

## Encoding — verified

Plain Shift-JIS, uncompressed, NUL-terminated (`さいしょから` found at 0x77E00, `バトローラー` 171 times). Fullwidth
characters throughout, including digits and Latin (`Ｖショップ`). Half-width ASCII appears in a few places.
`jp_left.py --sjis` applies directly. No table file is needed for extraction; the English font will need its own
encoding decision in phase 5 (`font.md`).

## Where the text is

| Region | What | How reached | Count |
|---|---|---|---|
| archive files (#2475-2711 mostly) | event dialogue, choices, comic titles | script command streams (`script.md`) | 11,062 op-0 lines + ~380 strings in op 1/6/0x13 |
| 0x000000-0x020000 | names, battle quotes, item/arm data strings (e.g. 0x471C 「バトローラー」) | u32 pointer tables in the same area (e.g. 0x0E4C) | ~2,800 strings with pointers |
| 0x073000-0x07C000 | menus, shop lines, box names (0x73CC8 「ボックス１６」..., 0x73E3C shop greetings) | pointer tables at 0xEC224.., 0xEE460.. | ~600 |
| 0x0E0000-0x0F2000 | strings near / inside the two link-cable images | pointers in 0xE0000-0xFFFFF | ~180 |

`tools/sjis_scan.py --dump START END` lists runs with their pointers.

## Extraction (phase 4) — verified by roundtrip + coverage test (`tests/test_text.py`, `tools/text.py check`)

`tools/text.py dump` writes `script/` from the original ROM (ids are original addresses; re-running keeps `en`,
`status`, `notes` and flags `jp-changed` under an existing translation):

| file | id | what | count |
|---|---|---|---|
| `script/events/e<file>.json` | `e<file>_<cmd offset>[.k]` | op 0x00 lines (`flags`, `script`), op 0x01 choice fields, op 0x13 title fields | 11,070 + 362 + 44 |
| `script/rom/r<bank>.json` | `r<addr>` | NUL-terminated strings with 4-aligned `0x08xxxxxx` pointers (`ptrs`); `inside` = shared tail of another string | 3,689 |
| `script/rom/r00.json` | `r<addr>`, kind `data` | pointered non-text: kanji list 0x3C0-0x880 (code searches it: font or name-entry index), digit table 0xCC0, pointer/code bytes | 39 |
| `script/rom/credits.json` | `c<addr>` | ending credits: fixed records at 0x74570-0x75E30, 0x2C bytes = 0x28-byte SJIS slot + 4 attribute bytes (`attr`: heading/name/spacing). **No pointer**: code indexes the table | 144 |
| `script/rom/noptr.json` | `n<addr>` | strings in 0xF0A0C-0xF16E8 with no pointer found (VS-mode labels: `かくとくポイント`, `ＶＰ`, digits); in place, `max` = original length | 11 |

Pointer rule: a target counts as a string start when a NUL precedes it, or (even address, starts with SJIS, >= 2
SJIS chars, not right after another SJIS char). Odd targets are Thumb code pointers. Pointers inside archive files
are ignored (event files hold none; other files are data).

Coverage sweep (whole ROM outside the archive, every event file): every run of >= 2 SJIS chars with a kana, or
NUL-bounded, lies inside an extracted string, except the ranges in `script/waive.tsv` (code, byte ramps, tile
data; each looked at by hand). Event files: 0 uncovered, no waivers. Code-built strings (glyph codes as
instruction immediates) cannot be found this way: the marker build (phase 5) shows them as Japanese that stays.

Codec: cp932 per character; bytes that do not round-trip become `[XX]` (cp932 maps 0xFD-0xFF to the PUA; IBM 桒
`FA E3` re-encodes as `ED 93`, one credit uses it). A literal `[` is written `[5B]`.
