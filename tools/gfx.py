"""gfx.py: graphics-text redraws (docs/re/graphics.md). Each edited archive file is rebuilt from the original here
and handed to the build as a whole file (written in place when it fits).

#446 (raw 4bpp, 640 tiles, OBJ sheet): the button-hint labels are fixed runs of tiles that the game puts in
sprites ("▶けってい" = tiles 4-7 in a 32x8 sprite ...; map from OAM dumps, graphics.md §Phase 8 notes). A label
keeps its ▶ arrow (columns 0-3 of its first tile) and gets English cores from fonts/font3.txt (3 px, advance 4,
space 2) in fill 1 with a 1 px outline 5 on background 0, the style of the original kana.

    python -X utf8 tools/gfx.py --preview work/gfx/edit/labels_en.png
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import archive  # noqa: E402
import tagfont  # noqa: E402

SHEET = 446
BG, FILL, OUTLINE = 0, 1, 5
ARROW_W = 4                    # columns of the ▶ kept from the original first tile (the kana may start at col 4)
# (first tile, tile count, English); every run is one row of 8x8 tiles laid side by side by its sprites
LABELS = [
    (4, 4, "OK"),              # ▶けってい   (A: confirm)
    (99, 4, "OK"),             # ▶けってい   (START: confirm, creation screens; same art as 4-7)
    (36, 3, "Back"),           # ▶もどる     (B: back)
    (64, 4, "Check"),          # ▶かくにん   (SELECT: check)
    (76, 7, "Back to title"),  # ▶タイトルにもどる
    (323, 3, "Help"),          # ▶ヘルプ
    (408, 8, "View Arm Data"), # ▶アームデータかくにん (A, field menu > Armalet Data)
    (416, 7, "View V Skills"), # ▶Ｖスキルかくにん (A, Character Data page)
]
# Page tabs of the field menu's Armalet Data / Character Data screens (32x8 sprites; the ▶/◀ beside them is
# tile 181, a sprite of its own): a pill of colour 4 with ink 5 (7 = antialias) on background 0. The inner
# arrow and kana are cleared and the English centred in the pill (3 px font3, advance 4). "Character" (35 px)
# cannot fit 32 px, so the tab to the Character Data page reads "Player" (D15).
PILLS = [
    (398, 4, "Player"),        # キャラクター▷ (Armalet Data -> Character Data)
    (402, 4, "Armalet"),       # ◁アーマレット (Character Data -> Armalet Data)
    (156, 4, "Box"),           # ◁ボックス (Arm Set screen, game mode 15: tab to the Arm Box; G18)
]
# Labels whose tiles are not one run: a 32x8 sprite plus a 16x8 and an 8x8 one side by side (tiles in screen
# order), drawn like LABELS.
SPLIT_LABELS = [
    ((388, 389, 390, 391, 160, 161, 162), "Grab/Swap"),   # ▶つかむ・いれかえ (A, Arm Set screen; G18)
]
PILL_BG, PILL_INK = 4, 5


def tile_px(data, n):
    t = data[n * 32:n * 32 + 32]
    return [[(t[y * 4 + x // 2] >> 4 * (x & 1)) & 15 for x in range(8)] for y in range(8)]


def put_tile(buf, n, px):
    buf[n * 32:n * 32 + 32] = bytes(px[y][i] | px[y][i + 1] << 4 for y in range(8) for i in range(0, 8, 2))


def render_label(orig, first, count, text, glyphs):
    """8 x (8*count) pixel rows for one label: original arrow, English cores, outline."""
    return label_px(tile_px(orig, first), 8 * count, text, glyphs)


# Labels drawn 16 px tall: the kana's dakuten rise above the 8 px strip, so the label is a 32x16 sprite plus
# a 16x16 one (Ⓐ ▶つぎにすすむ, the "next" hint on the battle result screen: OAM at x 170 + 202, 1D mapping).
# (blocks as (first tile, columns, rows), English). The blocks are laid side by side into one canvas; the
# arrow sits on canvas rows 6-10, so the 8-row strip from TALL_TOP has it on rows 2-6 like an 8 px label.
TALL_LABELS = [
    (((12, 4, 2), (20, 2, 2)), "Next"),   # ▶つぎにすすむ
]
TALL_TOP = 4


def tall_tiles(blocks):
    """(tile, canvas x, canvas y) for every tile of the blocks laid side by side."""
    out, x0 = [], 0
    for first, cols, rows in blocks:
        out += [(first + r * cols + c, x0 + c * 8, r * 8) for r in range(rows) for c in range(cols)]
        x0 += cols * 8
    return out


def render_tall(orig, blocks, text, glyphs):
    tiles = tall_tiles(blocks)
    w, h = max(x for _, x, _ in tiles) + 8, max(y for _, _, y in tiles) + 8
    canvas = [[BG] * w for _ in range(h)]
    for n, x0, y0 in tiles:
        for y, row in enumerate(tile_px(orig, n)):
            canvas[y0 + y][x0:x0 + 8] = row
    strip = [row[:ARROW_W] for row in canvas[TALL_TOP:TALL_TOP + 8]]
    assert all(v == BG for y, row in enumerate(canvas) if not TALL_TOP <= y < TALL_TOP + 8 for v in row[:ARROW_W])
    px = [[BG] * w for _ in range(h)]
    px[TALL_TOP:TALL_TOP + 8] = label_px(strip, w, text, glyphs)
    return {n: [row[x0:x0 + 8] for row in px[y0:y0 + 8]] for n, x0, y0 in tiles}


def label_px(arrow, w, text, glyphs, arrow_w=ARROW_W):
    """8 x w label pixels: the arrow's first `arrow_w` columns, then English cores with an outline."""
    px = [[BG] * w for _ in range(8)]
    for y in range(8):
        for x in range(arrow_w):
            px[y][x] = arrow[y][x]
    core = [[False] * w for _ in range(8)]
    x = arrow_w + 2
    for ch in text:
        if ch == " ":
            x += 2
            continue
        for gy, row in enumerate(glyphs[ch]):
            for gx, c in enumerate(row):
                if c == "#":
                    assert x + gx + 1 < w, f"{text!r} does not fit {w} px"
                    core[1 + gy][x + gx] = True
        x += 4
    for y in range(8):
        for xx in range(arrow_w, w):
            if core[y][xx]:
                px[y][xx] = FILL
            elif any(0 <= y + dy < 8 and arrow_w <= xx + dx < w and core[y + dy][xx + dx]
                     for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
                px[y][xx] = OUTLINE
    return px


# #431 (raw 4bpp, 192 tiles, OBJ sheet of the creation-confirm / status screens): boxed labels, each a run of
# tiles with a 2 px border (colour 4) at the run's left and right ends, background 2, ink d with shadow 1
# right/below. (first tile, tile count, English); English centred, 3 px font3 letters (advance 4).
SHEET_431 = 431
BOXES_431 = [
    (33, 7, "Character"),      # キャラクター
    (40, 7, "Armalet"),        # アーマレット
    (47, 7, "Fav. Word"),      # すきなことば (glossary: "Fav. Word")
]
BOX_BG, BOX_BORDER, BOX_INK, BOX_SHADOW = 2, 4, 0xD, 1


def render_box(orig, first, count, text, glyphs):
    w = 8 * count
    px = [[BOX_BG] * w for _ in range(8)]
    l, r = tile_px(orig, first), tile_px(orig, first + count - 1)
    for y in range(8):                          # keep the borders (and their corner shading) as drawn
        px[y][0:2] = l[y][0:2]
        px[y][w - 2:w] = r[y][6:8]
    width = sum(2 if ch == " " else 4 for ch in text) - 1
    x = (w - width) // 2
    ink = [[False] * w for _ in range(8)]
    for ch in text:
        if ch == " ":
            x += 2
            continue
        for gy, row in enumerate(glyphs[ch]):
            for gx, c in enumerate(row):
                if c == "#":
                    ink[1 + gy][x + gx] = True
        x += 4
    for y in range(8):
        for xx in range(2, w - 2):
            if ink[y][xx]:
                px[y][xx] = BOX_INK
            elif (xx > 0 and ink[y][xx - 1]) or (y > 0 and ink[y - 1][xx]) or (y > 0 and xx > 0 and ink[y - 1][xx - 1]):
                px[y][xx] = BOX_SHADOW
    return px


# #431 labels of the field menu's Armalet Data / Character Data pages (G1), placed by the BG maps (tiles found with
# tools/bgfind.py on warp dumps of menu_armalet / menu_chara). Each entry: the tiles left to right as the map lays
# them, English, background, ink, shadow (None = flat), glyph top row, ink x range [lo, hi) over the run, and the
# colours cleared to the background inside that range (old ink and antialias).
STATUS_431 = [
    ((129, 130, 131, 117), "Human", 0xD, 3, None, 2, 0, 32, (3, 0xE)),        # ヒトガタ (column head)
    ((90, 158, 159, 178, 113), "Roll", 0xD, 3, None, 2, 1, 40, (3, 0xE)),     # ロールガタ (column head)
    ((147, 148, 149, 150, 151, 152, 153, 154), "Armalet Size", 3, 0xD, 0xE, 2, 0, 64, (0xD, 0xE, 1)),  # アーマレットサイズ
    ((185, 186, 187, 188, 189, 118), "Usable", 0xD, 3, None, 3, 4, 46, (3, 0xE, 1)),       # ツカエル (box line 1)
    ((64, 65, 66, 110, 111, 112), "Arm Types", 0xD, 3, None, 1, 3, 46, (3, 0xE)),         # アームケイトウ (line 2)
]
# G17: ひっさつわざしょうさい, head of the special-details panel (Arm Data device, combo slot): BG3 map row 0 lays
# #431 tiles 175-177, 101-103, 143 (cb 0xC000, tile n = #431 n; found with tilefind.py on a specialsweep dump).
# Ink 4 on 6 with shadow 2 under the kana feet (row 7); tile 143 cols 5-7 / row 7 cols 3-7 are the box corner.
# "Special Details" (57 px) cannot fit the 53 px box: "Special Info".
HEAD_431 = ((175, 176, 177, 101, 102, 103, 143), "Special Info", 6, 4, None, 1, 0, 53, (4, 2, 5))
HEAD_431_FOOT = 51             # row 7 is cleared of the kana shadow up to the corner
COPIES_431 = [(117, 132)]      # 132 is an identical copy of 117 (the タ end of ヒトガタ) in the original: keep it so


def relabel(data, out, tiles, text, bg, ink, shadow, top, lo, hi, clear, glyphs, rows=None):
    """`tiles`: one row of tile numbers, or a tuple of rows (a label crossing a tile row). Glyph advance = its width
    + 1 (font3 = 4; narrow override glyphs are allowed). `rows` = (first, end) pixel rows cleared (default all)."""
    grid = tiles if isinstance(tiles[0], tuple) else (tiles,)
    w, h = 8 * len(grid[0]), 8 * len(grid)
    px = [sum((tile_px(data, t)[y % 8] for t in grid[y // 8]), []) for y in range(h)]
    r0, r1 = rows or (0, h)
    for y in range(r0, r1):
        for x in range(lo, hi):
            if px[y][x] in clear:
                px[y][x] = bg
    width = sum(2 if ch == " " else len(glyphs[ch][0]) + 1 for ch in text) - 1
    assert width <= hi - lo, f"{text!r} ({width} px) does not fit {hi - lo} px"
    x = lo + (hi - lo - width) // 2
    dots = set()
    for ch in text:
        if ch == " ":
            x += 2
            continue
        for gy, row in enumerate(glyphs[ch]):
            for gx, c in enumerate(row):
                if c == "#" and top + gy < h:
                    dots.add((top + gy, x + gx))
        x += len(glyphs[ch][0]) + 1
    for y, xx in dots:
        px[y][xx] = ink
        if shadow is not None:
            for sy, sx in ((y, xx + 1), (y + 1, xx), (y + 1, xx + 1)):
                if sy < h and sx < hi and (sy, sx) not in dots:
                    px[sy][sx] = shadow
    for r, trow in enumerate(grid):
        for k, t in enumerate(trow):
            put_tile(out, t, [row[k * 8:k * 8 + 8] for row in px[8 * r:8 * r + 8]])
    assert w == len(px[0])


# Arm Data page 2 (G1): the stat table head. Human (above, tiles 129-132, done in STATUS_431) spans three columns
# アタック (166-168) / スマッシュ (163-165) / チャージ (160-162), each a 24 px cell: background f, ink 3, a d border
# at x 0 and 23 and on the rounded top corners (row 0 is kept). The Roll column box is ロール (134-136) over ガタ
# (181-183): "Roll" goes on the top row, level with "Human"; ガタ is cleared. "Attack"/"Charge" need 22 px: a 2 px
# t and r (NARROW) make them fit.
NARROW = {"t": ["#.", "##", "#.", "#.", ".#", ".."], "r": ["..", "##", "#.", "#.", "#.", ".."]}
ARM_431 = [
    ((166, 167, 168), "Attack", 0xF, 3, None, 2, 1, 23, (3, 0xD, 0xE), (1, 8)),
    ((163, 164, 165), "Smash", 0xF, 3, None, 2, 1, 23, (3, 0xD, 0xE), (1, 8)),
    ((160, 161, 162), "Charge", 0xF, 3, None, 2, 1, 23, (3, 0xD, 0xE), (1, 8)),
    ((134, 135, 136), "Roll", 0xD, 3, None, 2, 1, 23, (3, 0xE), (2, 8)),
    ((181, 182, 183), "", 0xD, 3, None, 2, 1, 24, (3, 0xE), (0, 8)),
]
# #434 (raw, Armalet device BG1 tiles): the ひっさつわざ tab over the moves box (BG1 map row 12 = tiles 131-134,
# row 13 = 135-138). The tab is row 13's rows 0-5 (green 2, ink e, kana feet d; border d/e in rows 6-7, slant at
# x 30-31); the kana tops stick up into rows 6-7 of row 12, which are cleared to transparent. 必殺技 = "Special".
SHEET_434 = 434
TAB_434 = [
    ((131, 132, 133, 134), "", 0, 0xE, None, 0, 0, 32, (2, 0xE, 0xD), (6, 8)),
    ((135, 136, 137, 138), "Special", 2, 0xE, None, 0, 0, 30, (0xE, 0xD), (0, 6)),
]


def sheet_431(orig):
    glyphs = tagfont.load_font3()
    out = bytearray(orig)
    for first, count, text in BOXES_431:
        px = render_box(orig, first, count, text, glyphs)
        for k in range(count):
            put_tile(out, first + k, [row[k * 8:k * 8 + 8] for row in px])
    for tiles, text, bg, ink, shadow, top, lo, hi, clear in STATUS_431:
        relabel(orig, out, tiles, text, bg, ink, shadow, top, lo, hi, clear, glyphs)
    narrow = dict(glyphs, **NARROW)
    for *args, rows in ARM_431:
        relabel(orig, out, *args, narrow, rows=rows)
    tiles = HEAD_431[0]
    relabel(orig, out, *HEAD_431, glyphs, rows=(0, 7))
    relabel(bytes(out), out, tiles, "", 6, 4, None, 0, 0, HEAD_431_FOOT, (2, 4), glyphs, rows=(7, 8))
    for src, dst in COPIES_431:
        out[dst * 32:dst * 32 + 32] = out[src * 32:src * 32 + 32]
    return bytes(out)


def render_pill(orig, first, count, text, glyphs):
    """The tab pill with its ink cleared and `text` centred on the columns that are pill on every glyph row."""
    w = 8 * count
    rows = [sum((tile_px(orig, first + k)[y] for k in range(count)), []) for y in range(8)]
    px = [[PILL_BG if c in (PILL_INK, 7) else c for c in row] for row in rows]
    inside = [x for x in range(w) if all(px[y][x] == PILL_BG for y in range(1, 7))]
    lo, hi = inside[0], inside[-1]
    width = sum(2 if ch == " " else 4 for ch in text) - 1
    assert width <= hi - lo + 1, f"{text!r} ({width} px) does not fit the {hi - lo + 1} px pill at {first}"
    x = lo + (hi - lo + 1 - width + 1) // 2
    for ch in text:
        if ch == " ":
            x += 2
            continue
        for gy, row in enumerate(glyphs[ch]):
            for gx, c in enumerate(row):
                if c == "#":
                    px[1 + gy][x + gx] = PILL_INK
        x += 4
    return px


# Shop screen (G3, game mode 10; tiles from `oamlabels.py --file 446` on a `shop_arms` dump). Column heads are 32x16
# sprites: a d box (border e) with ink 9 (antialias 7/8) on the second tile row. Rows as in relabel(): tiles, text,
# bg, ink, shadow, glyph top, x range, cleared colours, pixel rows.
SHOP_HEADS = [
    ((437, 438, 439, 440), "Item", 0xD, 9, None, 1, 1, 31, (9, 8, 7), (0, 7)),     # しなもの (433-436 above: border only)
    ((460, 461, 462, 463), "Equip", 0xD, 9, None, 1, 2, 30, (9, 8, 7), (0, 7)),    # そうび (448-451 above)
    ((452, 453, 454, 455), "Price", 0xD, 9, None, 1, 2, 30, (9, 8, 7), (0, 7)),    # ねだん (448-451 above)
]
# できない in each row's Equip column (32x16, tiles 464-467 over 468-471): fill 8 with an outline 5 (antialias 7).
SHOP_CANT = (((464, 465, 466, 467), (468, 469, 470, 471)), "No", 8, 5, 6)   # "Can't": the ' outline clogs it
# ▶ページきりかえ (L/R: change page): a 32x16 sprite (tiles 56-59 over 60-63, the top row holds only dakuten) at
# x 26 plus a 16x8 one (574-575) at x 58, label style like LABELS but with a 5 px arrow (its outline reaches col 4).
PAGE_LABEL = ((60, 61, 62, 63, 574, 575), (56, 57, 58, 59), "Turn page", 5)    # "Change page" is 2 px too long


def outlined(data, out, grid, text, fill, outline, top, glyphs):
    """Clear the tile grid to BG and draw `text` centred in `fill` with an 8-neighbour `outline` ring."""
    w, h = 8 * len(grid[0]), 8 * len(grid)
    width = sum(2 if ch == " " else 4 for ch in text) - 1
    assert width + 2 <= w, f"{text!r} does not fit {w} px"
    x, core = (w - width) // 2, set()
    for ch in text:
        if ch != " ":
            core |= {(top + gy, x + gx) for gy, row in enumerate(glyphs[ch]) for gx, c in enumerate(row) if c == "#"}
        x += 2 if ch == " " else 4
    px = [[BG] * w for _ in range(h)]
    for y, xx in core:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if 0 <= y + dy < h and 0 <= xx + dx < w and (y + dy, xx + dx) not in core:
                    px[y + dy][xx + dx] = outline
        px[y][xx] = fill
    for r, trow in enumerate(grid):
        for k, t in enumerate(trow):
            put_tile(out, t, [row[k * 8:k * 8 + 8] for row in px[8 * r:8 * r + 8]])


def sheet_446(orig):
    glyphs = tagfont.load_font3()
    out = bytearray(orig)
    for args in SHOP_HEADS:
        relabel(orig, out, *args[:9], glyphs, rows=args[9])
    grid, text, fill, outline, top = SHOP_CANT
    outlined(orig, out, grid, text, fill, outline, top, glyphs)
    tiles, above, text, arrow_w = PAGE_LABEL
    px = label_px(tile_px(orig, tiles[0]), 8 * len(tiles), text, glyphs, arrow_w)
    for k, t in enumerate(tiles):
        put_tile(out, t, [row[k * 8:k * 8 + 8] for row in px])
    for t in above:
        put_tile(out, t, [[BG] * 8 for _ in range(8)])
    for first, count, text in LABELS:
        px = render_label(orig, first, count, text, glyphs)
        for k in range(count):
            put_tile(out, first + k, [row[k * 8:k * 8 + 8] for row in px])
    for first, count, text in PILLS:
        px = render_pill(orig, first, count, text, glyphs)
        for k in range(count):
            put_tile(out, first + k, [row[k * 8:k * 8 + 8] for row in px])
    for tiles, text in SPLIT_LABELS:
        px = label_px(tile_px(orig, tiles[0]), 8 * len(tiles), text, glyphs)
        for k, t in enumerate(tiles):
            put_tile(out, t, [row[k * 8:k * 8 + 8] for row in px])
    for blocks, text in TALL_LABELS:
        for n, px in render_tall(orig, blocks, text, glyphs).items():
            put_tile(out, n, px)
    return bytes(out)


# #452 (raw 4bpp, title-screen BG0 tiles loaded at charblock 0): the credit line under PRESS START (G10) is two
# rows of 27 tiles, 0x360-0x37A and 0x380-0x39A, palette 3: ink 1, outline 2, background 0. Its outline is the
# 8-neighbour dilation of the ink plus the same of the ink shifted (+1,+1) (checked: reproduces the original
# line exactly). The Latin "Created by" and "© BANDAI 2004" are kept as drawn; the kana middle is replaced with
# letters in the same style (caps 6 rows, x-height 4, 1 px gap, word space 3 px) and the line is re-centred.
SHEET_452 = 452
CREDIT_ROWS = (0x360, 0x380)           # first tile of each 8 px row
CREDIT_TILES = 27
CREDIT_KEEP = ((0, 42), (145, 216))    # x ranges of the original ink kept: "Created by", "© BANDAI 2004"
CREDIT_TEXT = "Tenya Yabuno, Ganbarion /"
CREDIT_SPACE = 4                       # empty columns between words ("Created by" has 3: one more reads better)
# rows 0-7 = line rows 3-10; caps on rows 0-5, x-height rows 2-5, descenders to row 7
CREDIT_GLYPHS = {
    "T": ["###", ".#.", ".#.", ".#.", ".#.", ".#."],
    "Y": ["#.#", "#.#", ".#.", ".#.", ".#.", ".#."],
    "G": [".##.", "#...", "#...", "#.##", "#..#", ".##."],
    "a": ["...", "...", ".##", "#.#", "#.#", ".##"],
    "b": ["#..", "#..", "##.", "#.#", "#.#", "##."],
    "e": ["...", "...", ".##", "###", "#..", ".##"],
    "i": ["#", ".", "#", "#", "#", "#"],
    "n": ["...", "...", "##.", "#.#", "#.#", "#.#"],
    "o": ["...", "...", ".#.", "#.#", "#.#", ".#."],
    "r": ["..", "..", "##", "#.", "#.", "#."],
    "u": ["...", "...", "#.#", "#.#", "#.#", ".##"],
    "y": ["...", "...", "#.#", "#.#", "#.#", ".##", "..#", "##."],
    ",": ["..", "..", "..", "..", "..", ".#", "#."],
    "/": ["..#", "..#", ".#.", ".#.", "#..", "#.."],
}
CREDIT_TOP = 3


def credit_px(data):
    w = 8 * CREDIT_TILES
    px = [[0] * w for _ in range(16)]
    for r, first in enumerate(CREDIT_ROWS):
        for k in range(CREDIT_TILES):
            t = tile_px(data, first + k)
            for y in range(8):
                px[r * 8 + y][k * 8:k * 8 + 8] = t[y]
    return px


def credit_outline(core):
    """Ink 1 / outline 2 / background 0 from an ink mask, the original's rule."""
    h, w = len(core), len(core[0])
    px = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if core[y][x]:
                px[y][x] = 1
            elif any(0 <= y + dy - s < h and 0 <= x + dx - s < w and core[y + dy - s][x + dx - s]
                     for dy in (-1, 0, 1) for dx in (-1, 0, 1) for s in (0, 1)):
                px[y][x] = 2
    return px


def credit_columns(text):
    """Ink columns (lists of 16 bools) for text in CREDIT_GLYPHS, 1 empty column between letters."""
    cols = []
    for i, ch in enumerate(text):
        if ch == " ":
            cols += [[False] * 16] * (CREDIT_SPACE - 1)
            continue
        g = CREDIT_GLYPHS[ch]
        if i and text[i - 1] != " ":
            cols.append([False] * 16)
        for gx in range(len(g[0])):
            col = [False] * 16
            for gy, row in enumerate(g):
                col[CREDIT_TOP + gy] = row[gx] == "#"
            cols.append(col)
    return cols


def sheet_452(orig):
    px = credit_px(orig)
    h, w = 16, 8 * CREDIT_TILES

    def ink(lo, hi):
        cs = [[px[y][x] == 1 for y in range(h)] for x in range(lo, hi)]
        while cs and not any(cs[0]):
            cs.pop(0)
        while cs and not any(cs[-1]):
            cs.pop()
        return cs
    gap = [[False] * h] * CREDIT_SPACE
    cols = ink(*CREDIT_KEEP[0]) + gap + credit_columns(CREDIT_TEXT) + gap + ink(*CREDIT_KEEP[1])
    assert len(cols) + 3 <= w, f"credit line {len(cols)} px does not fit {w}"
    x0 = (w - len(cols) - 1) // 2               # outline: 1 px left, 2 px right
    core = [[False] * w for _ in range(h)]
    for i, c in enumerate(cols):
        for y in range(h):
            core[y][x0 + i] = c[y]
    new = credit_outline(core)
    out = bytearray(orig)
    for r, first in enumerate(CREDIT_ROWS):
        for k in range(CREDIT_TILES):
            put_tile(out, first + k, [row[k * 8:k * 8 + 8] for row in new[r * 8:r * 8 + 8]])
    return bytes(out)


# #433 (raw 4bpp, bookshelf BG tiles at charblock 0, G11): the デスロール spine is 2 x 8 tiles 0x1A9-0x1B8 (row
# major, palette 1) on BG1. Its katakana (spine rows 15-48) and the bottom emblem (49-57) are replaced with
# "DEATH ROLL" in font3 letters turned 90 deg clockwise (read top to bottom, a Western spine), fill 5 / outline 2
# on the spine's plain red background row. The top emblem and frame stay. The バトロラ / バトローラーX stacks on the
# other spines are the series logo and stay (D14).
SHEET_433 = 433
SPINE_FIRST, SPINE_W, SPINE_H = 0x1A9, 2, 8
SPINE_ROWS = (15, 58)                  # rows cleared and used for the title
SPINE_BG = [9, 8, 7, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 8, 9]
SPINE_TEXT = "DEATH ROLL"
SPINE_FILL, SPINE_OUTLINE = 5, 2
SPINE_TOP_COL = 10                     # spine column of a letter's top row (letters 5 px: columns 10..6)


def spine_px(data):
    px = [[0] * 8 * SPINE_W for _ in range(8 * SPINE_H)]
    for ty in range(SPINE_H):
        for tx in range(SPINE_W):
            t = tile_px(data, SPINE_FIRST + ty * SPINE_W + tx)
            for y in range(8):
                px[ty * 8 + y][tx * 8:tx * 8 + 8] = t[y]
    return px


def sheet_433(orig):
    glyphs = tagfont.load_font3()
    px = spine_px(orig)
    lo, hi = SPINE_ROWS
    for y in range(lo, hi):
        px[y] = list(SPINE_BG)
    ink = set()
    r = 0
    for i, ch in enumerate(SPINE_TEXT):
        if ch == " ":
            r += 2
            continue
        if i and SPINE_TEXT[i - 1] != " ":
            r += 1
        g = glyphs[ch]
        w = len(g[0])
        for gy, row in enumerate(g):
            for gx, c in enumerate(row[:w]):
                if c == "#":
                    ink.add((r + gx, SPINE_TOP_COL - gy))
        r += w
    top = lo + (hi - lo - r) // 2
    ink = {(top + y, x) for y, x in ink}
    assert all(lo < y < hi - 1 for y, _ in ink), f"{SPINE_TEXT!r} does not fit the spine"
    for y, x in ink:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if (y + dy, x + dx) not in ink:
                    px[y + dy][x + dx] = SPINE_OUTLINE
    for y, x in ink:
        px[y][x] = SPINE_FILL
    out = bytearray(orig)
    for ty in range(SPINE_H):
        for tx in range(SPINE_W):
            put_tile(out, SPINE_FIRST + ty * SPINE_W + tx, [row[tx * 8:tx * 8 + 8] for row in px[ty * 8:ty * 8 + 8]])
    return bytes(out)


# Map-tileset signs (G7). Each: archive file (raw 4bpp, loaded at tile 0), the sign's tile grid (rows of tile
# numbers, as the room map lays them), the pixel box (x0, y0, x1, y1) inside the sign that is cleared to `bg` and gets the English
# centred in SIGN_FONT, ink colour, and an optional soft-edge colour put right of / below each ink pixel.
SIGN_FONT = {                          # 7 rows
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "L": ["#...", "#...", "#...", "#...", "#...", "#...", "####"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "!": ["#", "#", "#", "#", "#", ".", "#"],
    "G": [".###.", "#...#", "#....", "#..##", "#...#", "#...#", ".###."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "S": [".###.", "#...#", "#....", ".###.", "....#", "#...#", ".###."],
}
SIGNS = [
    # ころがれ! banner on the club-room wall (ending credits room; tileset #647, palette 5): "Roll!" motto
    dict(file=647, grid=[range(0x2F9, 0x2FF), range(0x319, 0x31F)],
         box=(1, 3, 44, 13), bg=8, ink=0xC, soft=0xB, text="ROLL ON!"),
    # こんじょう (根性, "guts") dojo plaque (ending-credits dojo; tileset #658, palette 0); glossary V Skill "Guts"
    dict(file=658, grid=[[0x156, 0x157, 0x158, 0x159, 0x176, 0x177], [0x178, 0x179, 0x196, 0x197, 0x186, 0x187]],
         box=(2, 2, 46, 14), bg=7, ink=0xE, soft=0xB, bold=True, text="GUTS"),
]


def sign_px(data, grid):
    px = [[0] * 8 * len(grid[0]) for _ in range(8 * len(grid))]
    for r, row in enumerate(grid):
        for k, n in enumerate(row):
            t = tile_px(data, n)
            for y in range(8):
                px[r * 8 + y][k * 8:k * 8 + 8] = t[y]
    return px


def draw_sign(data, s):
    px = sign_px(data, s["grid"])
    x0, y0, x1, y1 = s["box"]
    for y in range(y0, y1):
        px[y][x0:x1] = [s["bg"]] * (x1 - x0)
    text, bold = s["text"], int(s.get("bold", False))      # bold: every letter one column wider (doubled stem)
    gap = 1 + bold
    width = sum(len(SIGN_FONT[c][0]) + bold if c != " " else 2 for c in text) + gap * (len(text) - 1)
    h = len(SIGN_FONT["O"])
    x, top = x0 + (x1 - x0 - width) // 2, y0 + (y1 - y0 - h) // 2
    assert x >= x0 and top >= y0, f"{text!r} does not fit the sign"
    ink = set()
    for c in text:
        if c == " ":
            x += 3
            continue
        for gy, row in enumerate(SIGN_FONT[c]):
            for gx, b in enumerate(row):
                if b == "#":
                    ink.update((top + gy, x + gx + d) for d in range(bold + 1))
        x += len(SIGN_FONT[c][0]) + bold + gap
    if s.get("soft") is not None:
        for y, xx in ink:
            for p in ((y, xx + 1), (y + 1, xx)):
                if p not in ink and p[0] < y1 and p[1] < x1:
                    px[p[0]][p[1]] = s["soft"]
    for y, xx in ink:
        px[y][xx] = s["ink"]
    out = bytearray(data)
    for r, row in enumerate(s["grid"]):
        for k, n in enumerate(row):
            put_tile(out, n, [line[k * 8:k * 8 + 8] for line in px[r * 8:r * 8 + 8]])
    return bytes(out)


# #441 (raw 4bpp, OBJ sheet of the VS / battle-rule card, G12): the card's words are sprites whose tile blocks the
# game copies out of #441 (cell lists near ROM 0x273CDE, 12-byte records ending c000 0000 0000 00f0). Layout below
# is the static card frame as OAM shows it (`tools/oamcomp.py`, rpg_tutorial frame 10680): block byte offset,
# sprite w, h, screen x, y. Each line = a front layer (core 2, dark ring 4, white ring 3) and a drop-shadow layer
# (silhouette in 4) shifted by `shadow`. Only rows [y0, y1) of the front (and the same rows + shadow dy of the
# back) are redrawn, so the ・・・ under line 1 stays. The バトルルール header is shared by every rule card.
CARD_FILE = 441
CARD_LINES = [
    dict(text="BATTLE RULE", y0=64, y1=86, shadow=(-1, 4), bold=False,
         front=[(0x0, 64, 32, 77, 64), (0x400, 16, 16, 141, 64), (0x480, 16, 8, 141, 80), (0x4C0, 8, 16, 157, 64),
                (0x500, 8, 8, 157, 80)],
         back=[(0x800, 64, 32, 76, 68), (0xC00, 16, 16, 140, 68), (0xC80, 16, 8, 140, 84), (0xCC0, 8, 16, 156, 68),
               (0xD00, 8, 8, 156, 84)]),
    dict(text="OFFICIAL", y0=97, y1=121, shadow=(1, 4), bold=True,
         front=[(0x520, 32, 16, 76, 97), (0x620, 32, 8, 76, 113), (0x6A0, 32, 16, 108, 97),
                (0x3320, 32, 8, 108, 113), (0x3400, 16, 16, 140, 97), (0x33A0, 16, 8, 140, 113),
                (0x7A0, 8, 8, 156, 113), (0x7C0, 8, 16, 156, 97)],
         back=[(0xD20, 32, 16, 77, 100), (0xE20, 32, 8, 77, 116), (0xEA0, 32, 16, 109, 100),
               (0x1E40, 32, 8, 109, 116), (0x1EC0, 16, 16, 141, 100), (0x1F40, 16, 8, 141, 116),
               (0xFE0, 8, 8, 157, 116), (0xFA0, 8, 16, 157, 100)]),
    # The other five rule words (tools/cardframes.py: final frames 13/16/19/22/25 of the set at ROM 0x273B94).
    # Their blocks hold nothing else, so `clear` blanks them whole; shadow = pixel offset of the JP shadow.
    dict(text="SURVIVAL", y0=99, y1=123, shadow=(0, 4), bold=True, clear=True,       # サバイバル
         front=[(0x40E0, 32, 16, 85, 99), (0x41E0, 32, 8, 85, 115), (0x4260, 32, 16, 117, 99),
                (0x4360, 32, 8, 117, 115), (0x43E0, 8, 16, 149, 99), (0x4420, 8, 8, 149, 115)],
         back=[(0x4440, 32, 16, 85, 103), (0x4540, 8, 8, 149, 119), (0x4560, 32, 8, 85, 119),
               (0x45E0, 32, 16, 117, 103), (0x46E0, 32, 8, 117, 119), (0x4760, 8, 16, 149, 103)]),
    dict(text="GRAB LOTS!!!", y0=97, y1=121, shadow=(1, 5), bold=False, clear=True,   # たくさんとれ!!!
         front=[(0x3480, 32, 16, 76, 97), (0x3580, 32, 8, 76, 113), (0x3600, 32, 16, 108, 97),
                (0x3700, 32, 8, 108, 113), (0x3780, 16, 16, 140, 97), (0x3800, 16, 8, 140, 113),
                (0x3840, 8, 16, 156, 97), (0x3880, 8, 8, 156, 113)],
         back=[(0x38A0, 32, 16, 77, 102), (0x39A0, 32, 8, 77, 118), (0x3A20, 32, 16, 109, 102),
               (0x3B20, 32, 8, 109, 118), (0x3BE0, 8, 8, 157, 118), (0x3BA0, 8, 16, 157, 102),
               (0x3C00, 16, 16, 141, 102), (0x3C80, 16, 8, 141, 118)]),
    dict(text="KNOCK DOWN!!!", y0=99, y1=123, shadow=(-1, 5), bold=False, clear=True,  # いっぱいたおせ!!!
         front=[(0x47A0, 32, 16, 73, 99), (0x48A0, 32, 8, 73, 115), (0x4920, 32, 16, 105, 99),
                (0x4A20, 32, 8, 105, 115), (0x4AA0, 32, 16, 137, 99), (0x6240, 32, 8, 137, 115)],
         back=[(0x4D20, 32, 16, 72, 104), (0x4E20, 32, 8, 72, 120), (0x4EA0, 32, 16, 104, 104),
               (0x5000, 32, 16, 136, 104), (0x62C0, 32, 8, 104, 120), (0x6340, 32, 8, 136, 120)],
         blank=[(0x4BA0, 8, 8, 105, 115)]),       # a stray 8x8 of shadow inside the front rows
    dict(text="DRAIN HP!!!", y0=100, y1=124, shadow=(0, 5), bold=True, clear=True,   # HPをへらせ!!!
         front=[(0x3CC0, 32, 16, 81, 100), (0x3DC0, 32, 8, 81, 116), (0x3E40, 32, 16, 113, 100),
                (0x3F40, 32, 8, 113, 116), (0x3FC0, 16, 16, 145, 100), (0x4040, 16, 8, 145, 116),
                (0x4080, 8, 16, 161, 100), (0x40C0, 8, 8, 161, 116)],
         back=[(0x5520, 32, 16, 81, 103), (0x5620, 32, 8, 81, 119), (0x56A0, 32, 16, 113, 103),
               (0x57A0, 32, 8, 113, 119), (0x5820, 16, 16, 145, 103), (0x58A0, 16, 8, 145, 119),
               (0x58E0, 8, 16, 161, 103), (0x5920, 8, 8, 161, 119)]),
    dict(text="BEAT THE BOSS!", y0=100, y1=124, shadow=(0, 5), bold=False, clear=True, gap=2,  # ボスをたおせ!!!
         front=[(0x5940, 32, 16, 75, 100), (0x5A40, 32, 8, 75, 116), (0x5AC0, 32, 16, 107, 100),
                (0x5BC0, 32, 8, 107, 116), (0x5C40, 32, 16, 139, 100), (0x5D40, 32, 8, 139, 116)],
         back=[(0x5DC0, 32, 16, 75, 103), (0x5EC0, 32, 8, 75, 119), (0x5F40, 32, 16, 107, 103),
               (0x6040, 32, 8, 107, 119), (0x60C0, 32, 16, 139, 103), (0x61C0, 32, 8, 139, 119)]),
]
CARD_CORE, CARD_RING, CARD_OUTER = 2, 4, 3
CARD_FONT = dict(SIGN_FONT, **{        # 5x7, drawn with every row doubled (14 px tall)
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "I": ["###", ".#.", ".#.", ".#.", ".#.", ".#.", "###"],
    "V": ["#...#", "#...#", "#...#", "#...#", ".#.#.", ".#.#.", "..#.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
})


def card_blocks(data, blocks):
    """{(x, y): colour index} over the blocks (1D tile order inside each sprite)."""
    px = {}
    for off, w, h, x0, y0 in blocks:
        for y in range(h):
            for x in range(w):
                t = (y // 8) * (w // 8) + x // 8
                b = data[off + t * 32 + (y % 8) * 4 + (x % 8) // 2]
                px[(x0 + x, y0 + y)] = b >> 4 * (x & 1) & 15
    return px


def card_store(out, blocks, px):
    for off, w, h, x0, y0 in blocks:
        for y in range(h):
            for x in range(0, w, 2):
                t = (y // 8) * (w // 8) + x // 8
                out[off + t * 32 + (y % 8) * 4 + (x % 8) // 2] = px[(x0 + x, y0 + y)] | px[(x0 + x + 1, y0 + y)] << 4


def card_line(data, out, ln):
    front, back = card_blocks(data, ln["front"]), card_blocks(data, ln["back"])
    xs = [x for x, _ in front]
    lo, hi = min(xs), max(xs) + 1
    y0, y1, bold, gap = ln["y0"], ln["y1"], int(ln["bold"]), ln.get("gap", 3)
    core = set()
    widths = [len(CARD_FONT[c][0]) + bold if c != " " else 1 for c in ln["text"]]
    total = sum(widths) + gap * (len(widths) - 1)
    x = lo + (hi - lo - total) // 2
    top = y0 + (y1 - y0 - 14) // 2
    assert x - 2 >= lo and x + total + 2 <= hi and top - 2 >= y0 and top + 16 <= y1, \
        f"{ln['text']!r} does not fit the card"
    for c, w in zip(ln["text"], widths):
        if c != " ":
            for gy, row in enumerate(CARD_FONT[c]):
                for gx, b in enumerate(row):
                    if b == "#":
                        core.update((x + gx + d, top + 2 * gy + e) for d in range(bold + 1) for e in (0, 1))
        x += w + gap

    def ring(s):
        return {(a + dx, b + dy) for a, b in s for dx in (-1, 0, 1) for dy in (-1, 0, 1)} - s
    dark = ring(core)
    white = ring(core | dark)
    if ln.get("clear"):
        y0 = y1 = None
    for (a, b) in [p for p in front if y0 is None or y0 <= p[1] < y1]:
        front[(a, b)] = 0
    for p in white:
        front[p] = CARD_OUTER
    for p in dark:
        front[p] = CARD_RING
    for p in core:
        front[p] = CARD_CORE
    dx, dy = ln["shadow"]
    for (a, b) in [p for p in back if y0 is None or y0 + dy <= p[1] < y1 + dy]:
        back[(a, b)] = 0
    for (a, b) in core | dark | white:
        assert (a + dx, b + dy) in back, "shadow outside the back blocks"
        back[(a + dx, b + dy)] = CARD_RING
    card_store(out, ln["front"], front)
    card_store(out, ln["back"], back)
    for off, w, h, _, _ in ln.get("blank", []):
        out[off:off + w * h // 2] = bytes(w * h // 2)


def sheet_441(orig):
    out = bytearray(orig)
    for ln in CARD_LINES:
        card_line(orig, out, ln)
    return bytes(out)


# #717 (raw 4bpp, V-Pon machine screen, game mode 13; G16): the message かきかえを / かくにんしました!!! over the
# machine's screen is six opaque sprites (OAM of a `md13` dump, 1D mapping) whose tiles are #717 640-679 plus the
# 8x16 piece 254-255 (a kana tail kept in the OBJ strip right of the BG picture). (x, y, w, h, first tile); the
# canvas spans x 69-181, y 0-31. Background 1 (screen grey), ink 3, soft 2 right of / below the ink.
VPON_FILE = 717
VPON_SPRITES = [(85, 16, 8, 16, 254), (93, 0, 32, 32, 640), (69, 16, 16, 16, 656), (125, 0, 16, 32, 660),
                (141, 0, 8, 32, 668), (149, 16, 32, 16, 672)]
# text, centre x, top y (screen pixels); the prize card covers y >= ~24, so line 2 sits as high as its sprites allow
VPON_LINES = [("REWRITE", 121, 4), ("CONFIRMED!!!", 125, 16)]
VPON_BG, VPON_INK, VPON_SOFT = 1, 3, 2
VPON_FONT = {"M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"]}    # added to CARD_FONT


def vpon_cells():
    """{(screen x, y) of each 8x8 cell: #717 tile} for the message sprites (1D: tiles row-major per sprite)."""
    return {(x + 8 * c, y + 8 * r): first + r * (w // 8) + c
            for x, y, w, h, first in VPON_SPRITES for r in range(h // 8) for c in range(w // 8)}


def sheet_717(orig):
    font = dict(CARD_FONT, **VPON_FONT)
    cells = vpon_cells()
    ink = set()
    for text, cx, top in VPON_LINES:
        width = sum(len(font[c][0]) + 1 if c != " " else 3 for c in text) - 1
        x = cx - width // 2
        for c in text:
            if c == " ":
                x += 3
                continue
            ink |= {(x + gx, top + gy) for gy, row in enumerate(font[c]) for gx, b in enumerate(row) if b == "#"}
            x += len(font[c][0]) + 1
    covered = {(cx + i, cy + j) for cx, cy in cells for i in range(8) for j in range(8)}
    assert ink <= covered, "V-Pon text runs off its sprites"
    soft = {(x + 1, y) for x, y in ink} | {(x, y + 1) for x, y in ink}
    out = bytearray(orig)
    for (cx, cy), t in cells.items():
        px = [[VPON_INK if (cx + i, cy + j) in ink else VPON_SOFT if (cx + i, cy + j) in soft else VPON_BG
               for i in range(8)] for j in range(8)]
        put_tile(out, t, px)
    return bytes(out)


# #677 (raw 4bpp, OBJ, 1D, G15): world-map place labels. The game copies each label's tile blocks into VRAM and
# lays them left to right (OAM of an md9 dump), with the place pin (tile 116) below. Kanji ink 1, ring 2 on 0,
# rows 3-13. English: font3 (3 px, advance 4) in 1 with an 8-neighbour ring 2, centred; two lines (tops 1 and 8,
# the rings share row 7) where one does not fit. (blocks as (first tile, columns, rows), lines).
MAP_FILE = 677
MAP_INK, MAP_RING = 1, 2
MAP_LABELS = [
    (((0, 4, 2), (8, 2, 2)), ("Tamari", "Village")),        # 田万里村 48 px
    (((12, 4, 2), (20, 1, 2)), ("Katsutobi", "Middle")),    # 勝飛中 40
    (((22, 4, 2), (30, 1, 2)), ("Katsutobi", "Town")),      # 勝飛町 40
    (((32, 4, 2),), ("Danda-", "hama")),                    # 弾打浜 32: "Dandahama" needs 37
    (((40, 4, 2),), ("Kaiten", "Island")),                  # 界天島 32
    (((48, 4, 2), (56, 2, 2)), ("North", "Mamaru Town")),   # 真丸町北 48
    (((60, 4, 2), (68, 2, 2)), ("South", "Mamaru Town")),   # 真丸町南 48
    (((72, 4, 2), (112, 2, 2)), ("Koenji Town",)),          # 光円寺 32 + 町 16
    (((80, 4, 2), (88, 4, 2), (96, 1, 2)), ("Globe Town",)),  # グローブタウン 72
    (((98, 4, 2),), ("Mamaru", "Middle")),                  # 真丸中 32
]
MAP_TOPS = {1: (6,), 2: (1, 8)}


def map_label(blocks, lines, glyphs):
    """{tile: 8x8 px} for one map label."""
    tiles = tall_tiles(blocks)
    w, h = max(x for _, x, _ in tiles) + 8, max(y for _, _, y in tiles) + 8
    core = set()
    for text, top in zip(lines, MAP_TOPS[len(lines)]):
        width = sum(2 if ch == " " else 4 for ch in text) - 1
        assert width + 2 <= w, f"{text!r} does not fit {w} px"
        x = (w - width) // 2
        for ch in text:
            if ch != " ":
                core |= {(top + gy, x + gx) for gy, row in enumerate(glyphs[ch]) for gx, c in enumerate(row) if c == "#"}
            x += 2 if ch == " " else 4
    px = [[BG] * w for _ in range(h)]
    for y, x in core:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if 0 <= y + dy < h and 0 <= x + dx < w:
                    px[y + dy][x + dx] = MAP_RING
    for y, x in core:
        px[y][x] = MAP_INK
    return {n: [row[x0:x0 + 8] for row in px[y0:y0 + 8]] for n, x0, y0 in tiles}


def sheet_677(orig):
    glyphs = tagfont.load_font3()
    out = bytearray(orig)
    for blocks, lines in MAP_LABELS:
        for n, px in map_label(blocks, lines, glyphs).items():
            put_tile(out, n, px)
    return bytes(out)


def files(ar):
    """{archive file index: new bytes} for every redrawn graphics file."""
    orig, o431, o452, o433 = (ar.file(n) for n in (SHEET, SHEET_431, SHEET_452, SHEET_433))
    assert all(archive.unpack(f)[1] == "raw" for f in (orig, o431, o452, o433))
    out = {SHEET: sheet_446(orig), SHEET_431: sheet_431(o431), SHEET_452: sheet_452(o452),
           SHEET_433: sheet_433(o433)}
    o434 = ar.file(SHEET_434)
    assert archive.unpack(o434)[1] == "raw"
    out434 = bytearray(o434)
    for *args, rows in TAB_434:
        relabel(o434, out434, *args, tagfont.load_font3(), rows=rows)
    out[SHEET_434] = bytes(out434)
    o441 = ar.file(CARD_FILE)
    assert archive.unpack(o441)[1] == "raw"
    out[CARD_FILE] = sheet_441(o441)
    o717 = ar.file(VPON_FILE)
    assert archive.unpack(o717)[1] == "raw"
    out[VPON_FILE] = sheet_717(o717)
    o677 = ar.file(MAP_FILE)
    assert archive.unpack(o677)[1] == "raw"
    out[MAP_FILE] = sheet_677(o677)
    for s in SIGNS:
        n = s["file"]
        data = out.get(n) or ar.file(n)
        assert archive.unpack(ar.file(n))[1] == "raw", n
        out[n] = draw_sign(data, s)
    return out


def preview(path):
    from PIL import Image
    ar = archive.Archive()
    orig, new = ar.file(SHEET), files(ar)[SHEET]
    pal = {0: (152, 200, 192), 1: (248, 248, 248), 2: (224, 232, 232), 3: (176, 176, 176), 5: (56, 56, 56)}
    z = 6
    im = Image.new("RGB", (16 * 8, len(LABELS) * 10), (255, 0, 255))    # original left, English right
    for r, (first, count, _) in enumerate(LABELS):
        for col, data in enumerate((orig, new)):
            for k in range(count):
                px = tile_px(data, first + k)
                for y in range(8):
                    for x in range(8):
                        im.putpixel(((col * 8 + k) * 8 + x, r * 10 + y), pal.get(px[y][x], (255, 0, 0)))
    im.resize((im.width * z, im.height * z), Image.NEAREST).save(path)


if __name__ == "__main__":
    if "--preview" in sys.argv:
        preview(sys.argv[sys.argv.index("--preview") + 1])
