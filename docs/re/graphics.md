# Graphics-text survey

Static sweep: `python -X utf8 tools/gfx_sweep.py --out work/gfx` renders all 1155 archive files over 0x200 bytes
(LZ10/Huffman unpacked) as 4bpp tiles into 39 pages, with `index.tsv` (page, file) and `skipped.tsv` (1559 files:
palettes/tables <=0x200 bytes and script files, each with its reason). All 39 pages were read on 2026-11-17, plus a
zoom of the UI sheets. The code region 0x18000-0x100000 was rendered too: code and data only, no tiles.

**Tour part still to do:** the skill's survey also lists every screen whose Japanese does not change in the marker
build (phase 5) and every mid-game card reached with the debug tool (phase 2). Add rows below as they turn up.

| # | Element | Source | Seen where | State |
|---|---|---|---|---|
| G1a | Creation-confirm boxed labels キャラクター / アーマレット / すきなことば (#431 tiles 33-39, 40-46, 47-53) | archive #431 | create_confirm | **done** 2026-11-17 (`gfx.BOXES_431`): Character / Armalet / Fav. Word, verified f2520; also START "▶けってい" = #446 tiles 99-102 → "OK" |
| G1 | Status menu labels: キャラクター, アームレット, すきなことば, せつめい, アイトウタ?, ヒトガタ, ロール, チャージ, スマッシュ, アタック, アーマレットサイズ, ガタ, ツッカエル | archive #431 (4bpp, 0x1800) | sweep page 1, `menu_armalet`, `menu_chara` | **part done** 2026-11-17 (`gfx.STATUS_431`, tiles found with `tools/bgfind.py`): ヒトガタ/ロールガタ → Human / Roll, アーマレットサイズ → Armalet Size, ツカエル/アームケイトウ → Usable / Arm Types; also #446 hints ▶アームデータかくにん (408-415) → View Arm Data, ▶Ｖスキルかくにん (416-422) → View V Skills, tab pills (`gfx.PILLS`) キャラクター (398-401) → Player (D15), アーマレット (402-405) → Armalet; verified on screen. Arm Data page 2 head (`gfx.ARM_431`, 2026-11-17): アタック/スマッシュ/チャージ → Attack / Smash / Charge (2 px `t`/`r` in `gfx.NARROW` to fit 22 px cells), ロール/ガタ box → "Roll"; ひっさつわざ tab = #434 tiles 131-138 (`gfx.TAB_434`) → "Special"; verified `menu_armdata2`. Left: せつめい (76-79), not seen on any reached page yet, ガタ variants (178-183), on screens not reached yet (Arm/V Skill detail pages) |
| G2 | Name-entry keyboard: kana grid, カタカナ / ABC toggles, END | archive #432 (0x6580) tiles + #893 BG2 map (32x64, 16-byte header; pages at map rows 5/25/45) + code-row pointer table ROM 0xEEC4C | sweep page 1 | **done** 2026-11-17 (`tools/namegrid.py`, D13): pages abc / !? / ABC, tabs and DEL redrawn; verified `create_word` + `tools/lua/pages.lua` (R switches pages) |
| G3 | Menu/shop UI labels: ねだん, そうび, しなもの, なまえ, きりかえ, プレイヤー, ダウン, セレクト/スタート hints (ＰＡＧＥ, SELECT, タイトルにもどる), もっている, NEW | archive #446 (0x5000) | sweep page 1, zoom | to redraw |
| G4 | Single kanji tiles (一二三, 刀, 法, 術, 日, 川, 八 ...; likely attribute or day icons) | archive #472 (0x400) | sweep page 2, zoom | identify in game, redraw |
| G5 | Small labels in #433 (icons with tiny text) and #442 (digits/labels) | archive #433, #442 | sweep page 1 | check zoomed |
| G6 | Title logo 「バトローラーX」 | archive ~#448-452 | boot smoke shot | keep Japanese: no official English logo exists (D5) |
| G7 | Map tilesets: shop/building signs (e.g. "V-center" is already English) | archive #644-676 (raw, loaded at tile 0) | sweep pages 6-8 | in progress (`gfx.SIGNS`): club-room banner ころがれ! → "ROLL ON!" (#647, `ending1`), dojo plaque こんじょう → "GUTS" (#658, `credits`), both verified; other signs as rooms are reached |
| G8 | Comic-mode art pieces | archive #1655-1835 | sweep pages 33-36 | no lettering seen at sweep scale; check comic mode in the tour |
| G9 | Fonts (#1132-1135) | archive | page 18-20 | not graphics text; replaced/extended by the font work |
| G10 | Title screen credit line "Created by やぶのてんや・ガンバリオン © BANDAI 2004" | archive #452 raw (title BG0 tiles, charblock 0): tiles 0x360-0x37A + 0x380-0x39A, palette 3 | tour `title` | **done** 2026-11-17 (`gfx.sheet_452`): "Created by Tenya Yabuno, Ganbarion / © BANDAI 2004", same letter style and outline rule; verified frame 690 |
| G11 | Book spines on the shelf (comic/RPG/Death Roll titles, katakana/kanji) | archive #433 raw (shelf BG1 tiles, charblock 0); デスロール spine = tiles 0x1A9-0x1B8 (2x8, palette 1) | tour `shelf` | **done** 2026-11-17 (`gfx.sheet_433`, D14): "DEATH ROLL" turned sideways; the バトロラ / バトローラーX stacks are the series logo, kept; verified `warp.py shelf` |
| G12 | VS-screen rule card "バトルルール … オフィシャル" (before a battle) | archive #441 raw (OBJ): words are sprites whose tile blocks the game copies from #441; cell lists at ROM 0x273CDE-0x2752A0 (12-byte records `size?, 0, #441 byte offset, y, x, shape?|0x1000`, frame ends `c000 0000 0000 00f0`; the shape/size bits did not decode cleanly, so the layout is taken from OAM) | `rpg_tutorial` frame ~10680 (`tools/lua/dumpframes.lua`, `tools/oamcomp.py`) | **done** 2026-11-17 (`gfx.CARD_LINES`): the animation set is decoded after all (`tools/cardframes.py`: set at ROM 0x273B94, 26 frames, records = {attr0 shape, attr1 size, pal, offset, y, x}, same as #437); all six words: バトルルール "BATTLE RULE", オフィシャル "OFFICIAL", サバイバル "SURVIVAL", たくさんとれ!!! "GRAB LOTS!!!", いっぱいたおせ!!! "KNOCK DOWN!!!", HPをへらせ!!! "DRAIN HP!!!", ボスをたおせ!!! "BEAT THE BOSS!". `cardframes.py --gfx --draw` draws every frame; `tools/cardtest.py N` shows word N in game (repoints the tutorial's OFFICIAL frames, dumps the card at f~10560 of `rpg_tutorial`); verified on screen. Frames 5-10 are the VS art (no text) |
| G14 | SELECT ▶Help bubbles on the field-menu pages (71 messages: page hints, stat names, Arm types, "アームが セットかのう"...) | archive #437 raw (OBJ, 1017 tiles); animation set at ROM 0x271E60 {#437 ROM ptr, 71, 71, frame table 0x271E70}; frame = {u16 0, u16 count, u32 0, ptr}; record = 6 x u16 {shape, size, pal, #437 offset, y, x} | `help_armdata`, `help_armalet`, `help_vskills` | **done** 2026-11-17 (`tools/helpbub.py`, tests `tests/test_helpbub.py`): every frame rebuilt in English (font3 white with black outline on the green bubble), new tiles + record lists form the new #437 (relocated), the set and frame table repointed; each frame within its original sprite count, tile count and width. Verified 6 bubbles on screen. `--render DIR` / `--english DIR` draw all frames |
| G13 | Chapter cards (comic chapters, RPG chapters) | marker tour | `comic_*`, `ch1_start_raw` | **not graphics** (2026-11-17): every chapter card is a text box from the 44 `title` rows (op 0x13, e.g. "Vattroller Jin / Debut Arc - Episode 1", "Death Roll Arc / The End"), already English (`comic_jin1` scene shot); RPG mode has no chapter cards (`ch1_start_raw` is plain dialogue). Covered by the tour verdicts |

### Phase 8 notes (2026-11-17)

- **Button hints are sprites built from #446 (raw 4bpp, 640 tiles, 1D OAM mapping).** Title menu OAM
  (`work/qa/vram/titlemenu/ppu.oam.bin`): "Ⓐ ▶けってい" = 16x16 icon (#446 tiles 24-27) + 32x8 label (#446
  tiles 4-7); "Ⓑ ▶タイトルにもどる" = icon (tiles 48-51) + 32x8 (tiles 76-79) + 16x8 (80-81) + 8x8 (82). So each
  label is a fixed run of tiles: English must fit that tile count (a 4-tile label = 32 px including the ▶).
  Method for the rest: dump OAM + VRAM per screen (`work/qa/probe/dumpat.lua`), map sprite tiles to #446 offsets
  with `vramfind.py ppu.vram.bin work/gfx/unpacked`, list label → tile run, then redraw with a 5 px pixel font in
  the sheet's palette indices and write #446 back in place (raw, same size). `work/gfx/unpacked/` holds every
  archive file unpacked (`NNNN_raw|lz10|huff.bin`).
- G10/G11 were "not found raw" only because the search looked for the wrong tiles: both are raw (#452, #433).
  Method that found them: `warp.py SCENE --script tools/lua/dumpscene.lua` (PPU dump at the scene shot),
  `python tools/bgrender.py DIR` (each BG layer as a PNG + its char/screen base), read the map entries
  under the text, then search the tile bytes in `work/gfx/unpacked/`.
- Archive files are LZ10/Huffman or raw; there is no LZ10 compressor in `tools/archive.py` yet (a literal-only
  LZ10 stream is valid and grows 1/8; `archive.write_files` relocates files that grow).

English already present: GAME BOY/Nintendo/BANDAI logos, PRESS START, "V-center" signage.
