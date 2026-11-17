# Graphics-text survey

Static sweep: `python -X utf8 tools/gfx_sweep.py --out work/gfx` renders all 1155 archive files over 0x200 bytes
(LZ10/Huffman unpacked) as 4bpp tiles into 39 pages, with `index.tsv` (page, file) and `skipped.tsv` (1559 files:
palettes/tables <=0x200 bytes and script files, each with its reason). All 39 pages were read on 2026-11-17, plus a
zoom of the UI sheets. The code region 0x18000-0x100000 was rendered too: code and data only, no tiles.

**Tour part still to do:** the skill's survey also lists every screen whose Japanese does not change in the marker
build (phase 5) and every mid-game card reached with the debug tool (phase 2). Add rows below as they turn up.

| # | Element | Source | Seen where | State |
|---|---|---|---|---|
| G1 | Status menu labels: キャラクター, アームレット, すきなことば, せつめい, アイトウタ?, ヒトガタ, ロール, チャージ, スマッシュ, アタック, アーマレットサイズ, ガタ, ツッカエル | archive #431 (4bpp, 0x1800) | sweep page 1 | to redraw |
| G2 | Name-entry keyboard: kana grid, カタカナ / ABC toggles, END | archive #432 (0x6580) | sweep page 1 | to redraw (kana grid becomes A-Z) |
| G3 | Menu/shop UI labels: ねだん, そうび, しなもの, なまえ, きりかえ, プレイヤー, ダウン, セレクト/スタート hints (ＰＡＧＥ, SELECT, タイトルにもどる), もっている, NEW | archive #446 (0x5000) | sweep page 1, zoom | to redraw |
| G4 | Single kanji tiles (一二三, 刀, 法, 術, 日, 川, 八 ...; likely attribute or day icons) | archive #472 (0x400) | sweep page 2, zoom | identify in game, redraw |
| G5 | Small labels in #433 (icons with tiny text) and #442 (digits/labels) | archive #433, #442 | sweep page 1 | check zoomed |
| G6 | Title logo 「バトローラーX」 | archive ~#448-452 | boot smoke shot | keep Japanese: no official English logo exists (D5) |
| G7 | Map tilesets: shop/building signs (e.g. "V-center" is already English) | archive #644-676 | sweep pages 6-8 | check each sign in the tour |
| G8 | Comic-mode art pieces | archive #1655-1835 | sweep pages 33-36 | no lettering seen at sweep scale; check comic mode in the tour |
| G9 | Fonts (#1132-1135) | archive | page 18-20 | not graphics text; replaced/extended by the font work |
| G10 | Title screen credit line "Created by やぶのてんや・ガンバリオン © BANDAI 2004" | not traced yet (title BG) | tour `title` | to redraw: "Created by Tenya Yabuno / Ganbarion" (credits c075dac/c075dd8 wording) |
| G11 | Book spines on the shelf (comic/RPG/Death Roll titles, katakana/kanji) | not traced yet | tour `shelf` | to redraw (titles as in the comic title strings) |
| G12 | VS-screen rule panel "バトルルール … オフィシャル" | not traced yet | tour `comic_*_end`, battles | to redraw ("Battle Rules … Official") |
| G13 | Chapter cards (comic chapters, RPG chapters) | marker tour | `comic_*`, `ch1_start_raw` | to redraw (titles = the `title` rows of the chapter) |

### Phase 8 notes (2026-11-17)

- **Button hints are sprites built from #446 (raw 4bpp, 640 tiles, 1D OAM mapping).** Title menu OAM
  (`work/qa/vram/titlemenu/ppu.oam.bin`): "Ⓐ ▶けってい" = 16x16 icon (#446 tiles 24-27) + 32x8 label (#446
  tiles 4-7); "Ⓑ ▶タイトルにもどる" = icon (tiles 48-51) + 32x8 (tiles 76-79) + 16x8 (80-81) + 8x8 (82). So each
  label is a fixed run of tiles: English must fit that tile count (a 4-tile label = 32 px including the ▶).
  Method for the rest: dump OAM + VRAM per screen (`work/qa/probe/dumpat.lua`), map sprite tiles to #446 offsets
  with `vramfind.py ppu.vram.bin work/gfx/unpacked`, list label → tile run, then redraw with a 5 px pixel font in
  the sheet's palette indices and write #446 back in place (raw, same size). `work/gfx/unpacked/` holds every
  archive file unpacked (`NNNN_raw|lz10|huff.bin`).
- Archive files are LZ10/Huffman or raw; there is no LZ10 compressor in `tools/archive.py` yet (a literal-only
  LZ10 stream is valid and grows 1/8; `archive.write_files` relocates files that grow).

English already present: GAME BOY/Nintendo/BANDAI logos, PRESS START, "V-center" signage.
