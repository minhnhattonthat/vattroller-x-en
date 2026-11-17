"""tagfont.py: English in the narrow-font text paths (speaker tags, headers, VS names; docs/re/font.md §Speaker tags).

Besides the 16x16 dialogue font, both text systems draw codes with narrow blitters that copy one cell per code
with no range check: 8x8 `src = font8 + idx*32` (speaker tags, the "Which?" header) and 8x16
`src = font16 + idx*64` (two fonts: +4 plain, +8 outlined; the VS-screen names). An English ASCII pair has
glyph index 46,848-65,022 (font.pair_index), so those cells were read from archive data: garbage.

Patch (Thumb hooks, no other code changes):
- ROM 0x000: the entry branch `b 0xC0` becomes `b 0x200`. 0xC0-0x1FF were zero words the CPU slid through
  (ARM `andeq` = no-op) on the way to 0x200, so 0x120-0x1FF are now free and BL-reachable from the blitters.
- Every narrow blitter has the same 8 bytes `ldrh r0,[r5]; lsls r0,#S; adds r0,r7; adds r1,r6,#0` (S = 5 or 6,
  r7 = font base) before its CpuFastSet call; they become `bl HOOK; adds r1,r6,#0; nop`.
- HOOK (one per cell format, 0x20 bytes each): idx = [r5]; idx < 46,848 -> r7 + idx<<S (the original);
  else TABLE + (idx - 46,848)<<S.
- TABLE: one cell per pair index, two 3 px letters from fonts/font3.txt (x 0-2 and 4-6, shadow right and below),
  in the palette of the font it stands in for.
"""
import struct
from pathlib import Path

import font

ROOT = Path(__file__).resolve().parents[1]
FONT3 = ROOT / "fonts" / "font3.txt"

ENTRY = 0x0
ENTRY_OLD, ENTRY_NEW = 0xEA00002E, 0xEA00007E      # b 0xC0 -> b 0x200
SITE_OLD5 = bytes.fromhex("28884001c019311c")      # lsls #5 (8x8)
SITE_OLD6 = bytes.fromhex("28888001c019311c")      # lsls #6 (8x16)
FIRST = min(font.pair_glyphs_index_range())          # 46,848
LAST = max(font.pair_glyphs_index_range())           # 65,022
N = LAST - FIRST + 1


class Cell:
    def __init__(self, name, hook, shift, table, sites, colours, top):
        self.name, self.hook, self.shift, self.table, self.sites = name, hook, shift, table, sites
        self.bg, self.ink, self.shadow = colours
        self.top = top                                 # cell row of the font's first row
        self.h = 8 << (shift - 5)                      # 8 or 16 rows
        self.table_end = table + N * (32 << (shift - 5))


CELLS = (
    # 8x8 (font +0): system 1 0x08027BBC (speaker tags), system 2 0x080288B8 ("Which?" header)
    Cell("8x8", 0x140, 5, 0xF00000, (0x27BDA, 0x288D4), (font.BG, font.INK, font.SHADOW), 1),
    # 8x16 plain (font +4, 0x083E5E44): system 1 0x08027BFC, system 2 0x080288F8
    Cell("8x16", 0x160, 6, 0xF90000, (0x27C1A, 0x28914), (font.BG, font.INK, font.SHADOW), 7),
    # 8x16 outlined (font +8, 0x083ED644: bg 0 transparent, ink 4, shadow 0xD): 0x08027C3C, 0x08028938 (VS names)
    Cell("8x16o", 0x180, 6, 0x10B0000, (0x27C5A, 0x28954), (0x0, 0x4, 0xD), 7),
)
TABLE_END = max(c.table_end for c in CELLS)


def load_font3(path=FONT3):
    glyphs, cur = {}, None
    for line in path.read_text(encoding="utf-8").splitlines():
        if cur is None and line.startswith("# "):    # header comment (glyph rows also start with '#')
            continue
        if line.startswith("== "):
            name = line[3:]
            cur = glyphs.setdefault(" " if name == "space" else name, [])
        elif line and cur is not None:
            cur.append(line)
    for ch, rows in glyphs.items():
        assert len(rows) == 6 and all(len(r) == 3 for r in rows), ch
    missing = [chr(c) for c in range(font.FIRST_CHAR, font.LAST_CHAR + 1) if chr(c) not in glyphs]
    assert not missing, missing
    return glyphs


def render_cell(glyphs, a, b, cell=CELLS[0]):
    """cell.h x 8 grid of palette indices for the pair a, b (chars or None)."""
    px = [[cell.bg] * 8 for _ in range(cell.h)]
    for x0, ch in ((0, a), (4, b)):
        if ch is None or ch == " ":
            continue
        for y, r in enumerate(glyphs[ch]):
            for x, c in enumerate(r):
                if c == "#":
                    px[cell.top + y][x0 + x] = cell.ink
    for y in range(cell.h - 1, -1, -1):
        for x in range(7, -1, -1):
            if px[y][x] == cell.bg and ((x and px[y][x - 1] == cell.ink) or (y and px[y - 1][x] == cell.ink)):
                px[y][x] = cell.shadow
    return px


def to_cell(px):
    """Rows of 8 palette indices -> 4bpp tiles stacked top to bottom (32 bytes per 8 rows)."""
    return bytes(px[y][i] | px[y][i + 1] << 4 for y in range(len(px)) for i in range(0, 8, 2))


def table(cell=CELLS[0], glyphs=None):
    glyphs = glyphs or load_font3()
    size = 32 << (cell.shift - 5)
    out = bytearray(to_cell(render_cell(glyphs, None, None, cell)) * N)
    for hi in range(font.FIRST_CHAR, font.LAST_CHAR + 1):
        for lo in font.LO_SET:
            i = font.pair_index(hi, lo) - FIRST
            out[i * size:(i + 1) * size] = to_cell(render_cell(glyphs, chr(hi), chr(lo) if lo else None, cell))
    return bytes(out)


def bl(at, target):
    """Thumb BL at ROM offset `at` to ROM offset `target` (both in the 0x08000000 map)."""
    off = (target - (at + 4)) >> 1
    assert -(1 << 21) <= off < (1 << 21)
    return struct.pack("<HH", 0xF000 | ((off >> 11) & 0x7FF), 0xF800 | (off & 0x7FF))


def hook_code(cell=CELLS[0]):
    lsl = cell.shift << 6                    # lsls r0,r0,#S
    code = struct.pack("<12H",
                       0x8828,               # +00 ldrh r0,[r5]
                       0x4905,               # +02 ldr  r1,[pc,#20] -> +18 FIRST
                       0x4288,               # +04 cmp  r0,r1
                       0xD202,               # +06 bhs  +0E
                       lsl,                  # +08 lsls r0,r0,#S
                       0x19C0,               # +0A adds r0,r0,r7
                       0x4770,               # +0C bx   lr
                       0x1A40,               # +0E subs r0,r0,r1
                       lsl,                  # +10 lsls r0,r0,#S
                       0x4902,               # +12 ldr  r1,[pc,#8] -> +1C TABLE
                       0x1840,               # +14 adds r0,r0,r1
                       0x4770)               # +16 bx   lr
    code += struct.pack("<II", FIRST, 0x08000000 + cell.table)
    assert len(code) == 0x20 and cell.hook % 4 == 0
    return code


def regions():
    """(start, end) of every write patch() makes: romcheck's allowed list."""
    out = {(ENTRY, ENTRY + 4)}
    for c in CELLS:
        out |= {(c.hook, c.hook + 0x20), (c.table, c.table_end)} | {(s, s + 8) for s in c.sites}
    return out


def patch(out, log):
    """Write the entry branch, the hooks, the call sites and the cell tables into `out` (bytearray)."""
    assert struct.unpack_from("<I", out, ENTRY)[0] == ENTRY_OLD
    assert not any(out[0xC0:0x200]), "0xC0-0x1FF expected to be zero"
    assert len(out) <= CELLS[0].table, f"ROM data reaches {len(out):#x}, past the tag tables at {CELLS[0].table:#x}"
    font.put(out, log, ENTRY, struct.pack("<I", ENTRY_NEW), "tagfont: entry branch")
    for c in CELLS:
        old = SITE_OLD5 if c.shift == 5 else SITE_OLD6
        for site in c.sites:
            assert bytes(out[site:site + 8]) == old, hex(site)
            font.put(out, log, site, bl(site, c.hook) + bytes.fromhex("311cc046"), f"tagfont: call site {c.name}")
        font.put(out, log, c.hook, hook_code(c), f"tagfont: hook {c.name}")
        font.put(out, log, c.table, table(c), f"tagfont: cells {c.name}")   # put() pads gaps with 0xFF


def sheet(path):
    """Every printable char in pairs, each cell format, zoomed: a review sheet of font3."""
    from PIL import Image
    glyphs = load_font3()
    chars = [chr(c) for c in range(font.FIRST_CHAR, font.LAST_CHAR + 1)]
    pal = {0x4: (200, 200, 255), 0x0: (240, 240, 240), font.INK: (40, 40, 40), font.SHADOW: (160, 160, 160),
           0xD: (60, 60, 120)}
    pairs = [(chars[i], chars[i + 1] if i + 1 < len(chars) else None) for i in range(0, len(chars), 2)]
    hs = [c.h for c in CELLS]
    im = Image.new("RGB", (16 * 8, sum(((len(pairs) + 15) // 16) * h for h in hs)))
    y0 = 0
    for c in CELLS:
        for k, (a, b) in enumerate(pairs):
            px = render_cell(glyphs, a, b, c)
            for y in range(c.h):
                for x in range(8):
                    im.putpixel((k % 16 * 8 + x, y0 + k // 16 * c.h + y), pal.get(px[y][x], (255, 0, 255)))
        y0 += ((len(pairs) + 15) // 16) * c.h
    im.resize((im.width * 5, im.height * 5), Image.NEAREST).save(path)


if __name__ == "__main__":
    import sys
    if "--sheet" in sys.argv:
        sheet(sys.argv[sys.argv.index("--sheet") + 1])
