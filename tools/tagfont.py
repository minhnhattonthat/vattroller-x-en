"""tagfont.py: English in the 8x8-font text path (speaker name tags, small headers; docs/re/font.md §Speaker tags).

The speaker tag (0x08072F18) maps its name with mapper A at 8 px per code and draws each glyph index with the
8x8 blitter 0x08027BBC: `src = *(0x030028C0) + idx*32`, one 8x8 4bpp tile per code, no range check. An English
ASCII pair has index 46,848-65,022 (font.pair_index), so the tile was read from archive data: garbage tags.

Patch (one hook, Thumb):
- ROM 0x000: the entry branch `b 0xC0` becomes `b 0x200`. 0xC0-0x1FF were zero words the CPU slid through
  (ARM `andeq` = no-op) on the way to 0x200, so 0x120-0x1FF are now free and BL-reachable from the blitter.
- 0x27BDA and 0x288D4 (the same 8x8 blitter in text systems 1 and 2: speaker tags; choice headers such as
  "Which?"): `ldrh r0,[r5]; lsls r0,#5; adds r0,r7; adds r1,r6,#0` -> `bl HOOK; adds r1,r6,#0; nop`.
- HOOK (0x140): idx = [r5]; idx < 46,848 -> r7 + idx*32 (the original); else TABLE + (idx - 46,848)*32.
- TABLE: one 8x8 tile per pair index, two 3 px letters from fonts/font3.txt (x 0-2 and 4-6, shadow right/below).
"""
import struct
from pathlib import Path

import font

ROOT = Path(__file__).resolve().parents[1]
FONT3 = ROOT / "fonts" / "font3.txt"

ENTRY = 0x0
ENTRY_OLD, ENTRY_NEW = 0xEA00002E, 0xEA00007E      # b 0xC0 -> b 0x200
HOOK = 0x140
SITES = (0x27BDA, 0x288D4)   # 8x8 blitters of text system 1 (0x08027BBC, tags) and 2 (0x080288B8, headers)
SITE_OLD = bytes.fromhex("28884001c019311c")
FIRST = min(font.pair_glyphs_index_range())          # 46,848
LAST = max(font.pair_glyphs_index_range())           # 65,022
TABLE = 0xF00000
TABLE_END = TABLE + (LAST - FIRST + 1) * 32
BG, INK, SHADOW = font.BG, font.INK, font.SHADOW


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


def render_tile(glyphs, a, b):
    """8x8 grid of palette indices for the pair a, b (chars or None): rows 1-6 ink, shadow right and below."""
    px = [[BG] * 8 for _ in range(8)]
    for x0, ch in ((0, a), (4, b)):
        if ch is None or ch == " ":
            continue
        for y, r in enumerate(glyphs[ch]):
            for x, c in enumerate(r):
                if c == "#":
                    px[1 + y][x0 + x] = INK
    for y in range(7, -1, -1):
        for x in range(7, -1, -1):
            if px[y][x] == BG and ((x and px[y][x - 1] == INK) or (y and px[y - 1][x] == INK)):
                px[y][x] = SHADOW
    return px


def to_tile(px):
    return bytes(px[y][i] | px[y][i + 1] << 4 for y in range(8) for i in range(0, 8, 2))


def table(glyphs=None):
    glyphs = glyphs or load_font3()
    blank = to_tile(render_tile(glyphs, None, None))
    out = bytearray(blank * (LAST - FIRST + 1))
    for hi in range(font.FIRST_CHAR, font.LAST_CHAR + 1):
        for lo in font.LO_SET:
            i = font.pair_index(hi, lo) - FIRST
            out[i * 32:i * 32 + 32] = to_tile(render_tile(glyphs, chr(hi), chr(lo) if lo else None))
    return bytes(out)


def bl(at, target):
    """Thumb BL at ROM offset `at` to ROM offset `target` (both in the 0x08000000 map)."""
    off = (target - (at + 4)) >> 1
    assert -(1 << 21) <= off < (1 << 21)
    return struct.pack("<HH", 0xF000 | ((off >> 11) & 0x7FF), 0xF800 | (off & 0x7FF))


def hook_code():
    code = struct.pack("<11H",
                       0x8828,   # 140 ldrh r0,[r5]
                       0x4905,   # 142 ldr  r1,[pc,#20] -> 158 FIRST
                       0x4288,   # 144 cmp  r0,r1
                       0xD202,   # 146 bhs  14E
                       0x0140,   # 148 lsls r0,r0,#5
                       0x19C0,   # 14A adds r0,r0,r7
                       0x4770,   # 14C bx   lr
                       0x1A40,   # 14E subs r0,r0,r1
                       0x0140,   # 150 lsls r0,r0,#5
                       0x4902,   # 152 ldr  r1,[pc,#8] -> 15C TABLE
                       0x1840)   # 154 adds r0,r0,r1
    code += struct.pack("<H", 0x4770)                                     # 156 bx lr
    code += struct.pack("<II", FIRST, 0x08000000 + TABLE)                 # 158, 15C
    assert len(code) == 0x20
    return code


def patch(out, log):
    """Write the entry branch, the hook, the call site and the tile table into `out` (bytearray)."""
    assert struct.unpack_from("<I", out, ENTRY)[0] == ENTRY_OLD
    assert not any(out[0xC0:0x200]), "0xC0-0x1FF expected to be zero"
    for site in SITES:
        assert bytes(out[site:site + 8]) == SITE_OLD, hex(site)
    assert len(out) <= TABLE, f"ROM data reaches {len(out):#x}, past the tag table at {TABLE:#x}"
    font.put(out, log, ENTRY, struct.pack("<I", ENTRY_NEW), "tagfont: entry branch")
    font.put(out, log, HOOK, hook_code(), "tagfont: hook")
    for site in SITES:
        font.put(out, log, site, bl(site, HOOK) + bytes.fromhex("311cc046"), "tagfont: call site")
    font.put(out, log, TABLE, table(), "tagfont: tiles")


def sheet(path):
    """Every printable pair's first letter alone, zoomed: a review sheet of font3."""
    from PIL import Image
    glyphs = load_font3()
    chars = [chr(c) for c in range(font.FIRST_CHAR, font.LAST_CHAR + 1)]
    pal = {BG: (240, 240, 240), INK: (40, 40, 40), SHADOW: (160, 160, 160)}
    im = Image.new("RGB", (16 * 8, ((len(chars) + 31) // 32) * 8))
    for i in range(0, len(chars), 2):
        px = render_tile(glyphs, chars[i], chars[i + 1] if i + 1 < len(chars) else None)
        for y in range(8):
            for x in range(8):
                im.putpixel(((i // 2) % 16 * 8 + x, (i // 2) // 16 * 8 + y), pal[px[y][x]])
    im.resize((im.width * 6, im.height * 6), Image.NEAREST).save(path)


if __name__ == "__main__":
    import sys
    if "--sheet" in sys.argv:
        sheet(sys.argv[sys.argv.index("--sheet") + 1])
