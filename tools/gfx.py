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
]


def tile_px(data, n):
    t = data[n * 32:n * 32 + 32]
    return [[(t[y * 4 + x // 2] >> 4 * (x & 1)) & 15 for x in range(8)] for y in range(8)]


def put_tile(buf, n, px):
    buf[n * 32:n * 32 + 32] = bytes(px[y][i] | px[y][i + 1] << 4 for y in range(8) for i in range(0, 8, 2))


def render_label(orig, first, count, text, glyphs):
    """8 x (8*count) pixel rows for one label: original arrow, English cores, outline."""
    w = 8 * count
    px = [[BG] * w for _ in range(8)]
    arrow = tile_px(orig, first)
    for y in range(8):
        for x in range(ARROW_W):
            px[y][x] = arrow[y][x]
    core = [[False] * w for _ in range(8)]
    x = ARROW_W + 2
    for ch in text:
        if ch == " ":
            x += 2
            continue
        for gy, row in enumerate(glyphs[ch]):
            for gx, c in enumerate(row):
                if c == "#":
                    assert x + gx + 1 < w, f"{text!r} does not fit {count} tiles"
                    core[1 + gy][x + gx] = True
        x += 4
    for y in range(8):
        for xx in range(ARROW_W, w):
            if core[y][xx]:
                px[y][xx] = FILL
            elif any(0 <= y + dy < 8 and ARROW_W <= xx + dx < w and core[y + dy][xx + dx]
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


def sheet_431(orig):
    glyphs = tagfont.load_font3()
    out = bytearray(orig)
    for first, count, text in BOXES_431:
        px = render_box(orig, first, count, text, glyphs)
        for k in range(count):
            put_tile(out, first + k, [row[k * 8:k * 8 + 8] for row in px])
    return bytes(out)


def sheet_446(orig):
    glyphs = tagfont.load_font3()
    out = bytearray(orig)
    for first, count, text in LABELS:
        px = render_label(orig, first, count, text, glyphs)
        for k in range(count):
            put_tile(out, first + k, [row[k * 8:k * 8 + 8] for row in px])
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


def files(ar):
    """{archive file index: new bytes} for every redrawn graphics file."""
    orig, o431, o452, o433 = (ar.file(n) for n in (SHEET, SHEET_431, SHEET_452, SHEET_433))
    assert all(archive.unpack(f)[1] == "raw" for f in (orig, o431, o452, o433))
    out = {SHEET: sheet_446(orig), SHEET_431: sheet_431(o431), SHEET_452: sheet_452(o452),
           SHEET_433: sheet_433(o433)}
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
