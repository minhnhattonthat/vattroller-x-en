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


def files(ar):
    """{archive file index: new bytes} for every redrawn graphics file."""
    orig, o431 = ar.file(SHEET), ar.file(SHEET_431)
    assert archive.unpack(orig)[1] == "raw" and archive.unpack(o431)[1] == "raw"
    return {SHEET: sheet_446(orig), SHEET_431: sheet_431(o431)}


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
