"""namegrid.py: the name-entry keyboard in English (graphics.md G2, decisions.md D13).

The keyboard (create_name / create_word) is BG2: tiles from archive #432 (raw 4bpp, 812 tiles) and a 32x64
tilemap in archive #893 (raw, 16-byte header, then 32x64 u16 entries). Each page is 13 map rows: rows 5-6 hold the
name-field keys (けす, arrows, END), rows 7-16 the 5x14 grid (2x2 tiles per cell, map col 1+2c), row 17 the page
tabs. Pages start at map rows 5, 25 and 45 (かな, カナ, ABC). The code a cell enters comes from a pointer table
at ROM 0xEEC4C: 22 entries, page p row r -> entry 1+7p+r, each pointing at a 14-code fullwidth SJIS row.

English layout, built only from glyphs the game already has (cells copied map entry by map entry):
  page 1, tab "abc": a-m x, n-z=, A-M+, N-Z-, 0-9.@  (the ABC page, lower case first)
  page 2, tab "!?":  0-9.@, symbols ! ? & ~ - . + - x =, three blank rows
  page 3, tab "ABC": unchanged (its table entries belong to the text writer: the Latin rows are repointed rows)
Tab labels and the DEL key (was けす; letters copied from END) are redrawn in #432; spare tiles come from the
page-1 kana cells no longer on any map.

    python -X utf8 tools/namegrid.py --preview OUT.png
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import archive  # noqa: E402
import font  # noqa: E402

TILES, MAP = 432, 893
HDR = 16
TABLE = 0xEEC4C
SYM_ROW = 0x77798            # storage for the new symbol row: the old あかさ row (28 bytes, no longer pointed at)
BLANK_ROW = 0x80777B8
PAGE_ROW = (5, 25, 45)       # first map row of each page
GRID_ROW = 2                 # grid starts 2 map rows below the page start
BLANK_TILE = 0xBB

# source cells: (page 0-2, grid row 0-4, grid col 0-13) in the ORIGINAL layout
SYMBOLS = [(0, 3, 13), (0, 2, 13), (0, 4, 13), (0, 0, 12), (0, 1, 12), (1, 4, 12),   # ! ? & ~ ー ・
           (2, 0, 13), (2, 1, 13), (2, 2, 13), (2, 3, 13)]                            # + - x =

# new pages: each row is ("copy", page, row) = a whole original row, "sym" or "blank"
PAGES = [   # pages 1 and 2; page 3 stays
    [("copy", 2, 2), ("copy", 2, 3), ("copy", 2, 0), ("copy", 2, 1), ("copy", 2, 4)],
    [("copy", 2, 4), ("sym",), ("blank",), ("blank",), ("blank",)],
]

# tab row (page start + 12): tab k spans map cols 6+6k .. 11+6k. Original entries (tile ids):
#   tab 1 inactive 24f 250 251 252 250 24f, active 0d3 0d4 0d5 0d6 0d9 0d3
#   tab 2 inactive 24f 250 253 254 250 24f, active 0d3 0d9 0d7 0d8 0d9 0d3
TAB_ROW = 12
SPARE = (0x002, 0x003, 0x004)        # freed kana tiles (page 1's あ cell)
# (map cols, inactive tiles, active tiles, text): the label is drawn over those cols in both states
TABS = [((7, 8, 9, 10), (SPARE[0], 0x251, 0x252, SPARE[1]), (0xD4, 0xD5, 0xD6, SPARE[2]), "abc"),
        ((14, 15), (0x253, 0x254), (0xD7, 0xD8), "!?")]
INACTIVE_BG, ACTIVE_BG = 3, 0xF
INACTIVE_INK, INACTIVE_SHADOW = 0xD, 2
ACTIVE_INK, ACTIVE_OUTLINE = 3, 7

# DEL key: けす tiles 327 328 329 (letters) over 32a 32b (outline row); END = 0bc 0bd 0be over 324 325 326
DEL_TILES = (0x327, 0x328, 0x329)
DEL_UNDER = (0x32A, 0x32B)
END_E, END_D, END_UNDER = 0xBC, 0xBE, 0x324
KESU_BG, KESU_OUT, KESU_INK = 2, 6, 4
UNDER_SPARE = 0x001          # a freed kana tile (page 1 no longer shows it) for the outline under "L"

GLYPHS = {
    "a": [".....", ".ddd.", "....d", ".dddd", "d...d", ".dddd"],
    "b": ["d....", "d....", "dddd.", "d...d", "d...d", "dddd."],
    "c": [".....", ".ddd.", "d....", "d....", "d....", ".ddd."],
    "!": [".d.", ".d.", ".d.", ".d.", "...", ".d."],
    "?": [".ddd.", "d...d", "...d.", "..d..", ".....", "..d.."],
}


def tile_px(data, n):
    t = data[n * 32:n * 32 + 32]
    return [[(t[y * 4 + x // 2] >> 4 * (x & 1)) & 15 for x in range(8)] for y in range(8)]


def put_tile(buf, n, px):
    buf[n * 32:n * 32 + 32] = bytes(px[y][i] | px[y][i + 1] << 4 for y in range(8) for i in range(0, 8, 2))


def render(text, ntiles, active):
    """8 x 8*ntiles pixels: the label centred, glyph rows at y 1-6."""
    w = 8 * ntiles
    ink = [[False] * w for _ in range(8)]
    width = sum(len(GLYPHS[c][0]) for c in text) + len(text) - 1
    x = (w - width - 1) // 2 + (1 if active else 0)
    for c in text:
        g = GLYPHS[c]
        for gy, row in enumerate(g):
            for gx, v in enumerate(row):
                if v == "d":
                    ink[1 + gy][x + gx] = True
        x += len(g[0]) + 1
    bg = ACTIVE_BG if active else INACTIVE_BG
    px = [[bg] * w for _ in range(8)]
    for y in range(8):
        for xx in range(w):
            if ink[y][xx]:
                px[y][xx] = ACTIVE_INK if active else INACTIVE_INK
            elif active and any(0 <= y + dy < 8 and 0 <= xx + dx < w and ink[y + dy][xx + dx]
                                for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
                px[y][xx] = ACTIVE_OUTLINE
            elif not active and any(0 <= y - dy < 8 and 0 <= xx - dx < w and ink[y - dy][xx - dx]
                                    for dy, dx in ((0, 1), (1, 0), (1, 1))):
                px[y][xx] = INACTIVE_SHADOW
    return px


def recolor(px, m):
    return [[m.get(v, v) for v in row] for row in px]


def del_tiles(orig):
    """D, E (from END) and an L made from the E, in the けす colours; plus the outline row under them."""
    to_kesu = {0xF: KESU_INK, 7: KESU_OUT, 2: KESU_BG}
    e, d = tile_px(orig, END_E), tile_px(orig, END_D)
    assert e[1] == [2, 7, 0xF, 0xF, 0xF, 0xF, 0xF, 7] and e[2] == [2, 7, 0xF, 7, 7, 7, 7, 7], "END's E moved"
    # L = the E's stem and bottom bar, in END's style (bg 2, outline 7, ink f)
    l = [[int(v, 16) for v in row] for row in
         ("27772222", "27f72222", "27f72222", "27f72222", "27f72222", "27f72222", "27f77777", "27fffff7")]
    under = tile_px(orig, END_UNDER)
    return [recolor(t, to_kesu) for t in (d, e, l)], recolor(under, to_kesu)


def entry(m, row, col):
    return struct.unpack_from("<H", m, HDR + (row * 32 + col) * 2)[0]


def set_entry(m, row, col, v):
    struct.pack_into("<H", m, HDR + (row * 32 + col) * 2, v)


def cell_entries(m, page, r, c):
    top, x = PAGE_ROW[page] + GRID_ROW + 2 * r, 1 + 2 * c
    return [entry(m, top, x), entry(m, top, x + 1), entry(m, top + 1, x), entry(m, top + 1, x + 1)]


def put_cell(m, page, r, c, es):
    top, x = PAGE_ROW[page] + GRID_ROW + 2 * r, 1 + 2 * c
    for (dy, dx), v in zip(((0, 0), (0, 1), (1, 0), (1, 1)), es):
        set_entry(m, top + dy, x + dx, v)


def code_rows(rom):
    """Original pointer table: page p row r -> ROM address of its 14-code row."""
    return {(p, r): struct.unpack_from("<I", rom, TABLE + 4 * (1 + 7 * p + r))[0] for p in range(3) for r in range(5)}


def code_at(rom, rows, p, r, c):
    a = rows[(p, r)] - 0x08000000 + 2 * c
    return bytes(rom[a:a + 2])


def build_map(m0, rom):
    m = bytearray(m0)
    blank_es = cell_entries(m0, 0, 1, 7)          # い row, col 7 is a blank cell
    assert all(e & 0x3FF == BLANK_TILE for e in blank_es), blank_es
    for p, rows in enumerate(PAGES):
        for r, spec in enumerate(rows):
            for c in range(14):
                if spec[0] == "copy":
                    es = cell_entries(m0, spec[1], spec[2], c)
                elif spec[0] == "sym" and c < len(SYMBOLS):
                    es = cell_entries(m0, *SYMBOLS[c])
                else:
                    es = blank_es
                put_cell(m, p, r, c, es)
    # tabs: tab k is active on page k; point its label cols at the label tiles of that state
    for p in range(3):
        row = PAGE_ROW[p] + TAB_ROW
        for k, (cols, inactive, active, _) in enumerate(TABS):
            for col, n in zip(cols, active if p == k else inactive):
                set_entry(m, row, col, (entry(m0, row, col) & 0xFC00) | n)
    # DEL key: outline tile under the L (map col 18 of row 6 was empty)
    for p in range(3):
        row = PAGE_ROW[p] + 1
        assert entry(m0, row, 18) == 0, hex(entry(m0, row, 18))
        set_entry(m, row, 18, (entry(m0, row, 17) & 0xF000) | UNDER_SPARE)
    return bytes(m)


def build_tiles(t0):
    t = bytearray(t0)
    for _, inactive, active, text in TABS:
        for tiles, on in ((inactive, False), (active, True)):
            px = render(text, len(tiles), on)
            for k, n in enumerate(tiles):
                put_tile(t, n, [row[8 * k:8 * k + 8] for row in px])
    letters, under = del_tiles(t0)
    for n, px in zip(DEL_TILES, letters):
        put_tile(t, n, px)
    for n in DEL_UNDER + (UNDER_SPARE,):
        put_tile(t, n, under)
    return bytes(t)


def files(ar, rom):
    t0, m0 = ar.file(TILES), ar.file(MAP)
    assert archive.unpack(t0)[1] == "raw" and archive.unpack(m0)[1] == "raw"
    return {TILES: build_tiles(t0), MAP: build_map(m0, rom)}


def table_writes(rom):
    """[(address, bytes)]: the new pointer table entries and the symbol code row."""
    rows = code_rows(rom)
    out = []
    sym = b"".join(code_at(rom, rows, *s) for s in SYMBOLS) + "　".encode("cp932") * (14 - len(SYMBOLS))
    out.append((SYM_ROW, sym))
    for p, prow in enumerate(PAGES):
        for r, spec in enumerate(prow):
            if spec[0] == "copy":
                ptr = rows[(spec[1], spec[2])]
            elif spec[0] == "sym":
                ptr = 0x08000000 + SYM_ROW
            else:
                ptr = BLANK_ROW
            out.append((TABLE + 4 * (1 + 7 * p + r), struct.pack("<I", ptr)))
    return out


def regions():
    return {(TABLE + 4 * i, TABLE + 4 * i + 4) for i in range(22)} | {(SYM_ROW, SYM_ROW + 28)}


def patch(out, log, orig):
    for a, b in table_writes(orig):
        font.put(out, log, a, b, "namegrid: table" if a >= TABLE else "namegrid: symbol row")


def preview(path):
    """Each new page drawn from the new map + tiles (palette ignored, index shades), originals below."""
    from PIL import Image
    ar = archive.Archive()
    rom = archive.ROM.read_bytes()
    new = files(ar, rom)
    shade = lambda v: (255 - v * 15,) * 3  # noqa: E731
    im = Image.new("RGB", (240, 13 * 8 * 6), (255, 0, 255))
    for half, (tiles, m) in enumerate(((new[TILES], new[MAP]), (ar.file(TILES), ar.file(MAP)))):
        for p in range(3):
            for ry in range(13):
                for cx in range(30):
                    e = entry(m, PAGE_ROW[p] + ry, cx)
                    px = tile_px(tiles, e & 0x3FF)
                    for y in range(8):
                        for x in range(8):
                            xx = 7 - x if e & 0x400 else x
                            yy = 7 - y if e & 0x800 else y
                            im.putpixel((cx * 8 + x, (half * 3 + p) * 104 + ry * 8 + y), shade(px[yy][xx]))
    im.resize((im.width * 3, im.height * 3), Image.NEAREST).save(path)


if __name__ == "__main__":
    if "--preview" in sys.argv:
        preview(sys.argv[sys.argv.index("--preview") + 1])
