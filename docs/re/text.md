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

`tools/sjis_scan.py --dump START END` lists runs with their pointers. Outside the archive, 3,582 of 3,815
kana-bearing strings have a direct 4-aligned pointer; the other 233 are mostly 1-2 character false hits inside code.
Strings without pointers (code-built or base+offset) still need a sweep in phase 4.
