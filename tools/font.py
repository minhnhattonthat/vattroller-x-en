"""font.py: the English font as pair glyphs (docs/re/font.md).

The game turns each 2-byte code into a glyph index in five copies of one mapper (0x080282B8, 0x0802844C,
0x080285D4.., 0x08028FB4, 0x08029110): codes 0x8140-0x8396 become `(hi-0x81)*192 + lo-0x40`, codes above go
through the kanji list, codes <= 0x813F become glyph 0 (blank). The glyph is drawn from `font + idx*128` (16x16
4bpp, tiles TL BL TR BR) and advances by `width[idx]` (8 or 12 px, table at 0x080008A0).

English is stored as plain ASCII; the mappers read it two bytes at a time. Lowering the five 0x813F thresholds to
0x001F sends an ASCII pair down the same formula, which (u16 arithmetic) lands on a unique index 46,816-65,215.
`patch()` writes a 12 px glyph holding both letters (6 px each) at `font + idx*128`, past the original ROM end,
and moves the width table to a 64 KiB copy where every pair index is 12. No code is changed.

    python -X utf8 tools/font.py --sheet out.png   # every glyph, zoomed, for review
"""
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FONT_TXT = ROOT / "fonts" / "font6.txt"

FONT_FILE = 1135                 # archive file: the 12 px dialogue/menu font (kept in place)
WIDTHS = 0x8A0                   # original width table, 1056 entries
N_GLYPHS = 0x21000 // 128
THRESHOLD_LITS = (0x2836C, 0x284F8, 0x28614, 0x2902C, 0x29180)   # u32 0x813F in the mappers' literal pools
WIDTH_LITS = (0x27D80, 0x28448, 0x28558, 0x28630, 0x28A7C, 0x29108, 0x291E0)  # u32 0x080008A0
NEW_WIDTHS = 0x800000            # 64 KiB width table, indexed by u16 glyph index
FIRST_CHAR, LAST_CHAR = 0x20, 0x7E
BG, INK, SHADOW = 4, 7, 5        # palette indices used by the Japanese glyphs
TOP = 4                          # art row 0 = glyph row 4 (the Japanese glyphs use rows 3-14)


def pair_index(hi, lo):
    """Glyph index the game's mapper computes for the 2-byte code hi:lo once the threshold is 0x1F."""
    return ((hi - 0x81) * 192 + lo - 0x40) & 0xFFFF


LO_SET = [0] + list(range(FIRST_CHAR, LAST_CHAR + 1))   # lo = 0: a char followed by the NUL


def load_glyphs(path=FONT_TXT):
    glyphs, cur = {}, None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("== "):
            name = line[3:]
            cur = glyphs.setdefault(" " if name == "space" else name, [])
        elif line and cur is not None:
            cur.append(line)
    for ch, rows in glyphs.items():
        assert len(rows) == 10, (ch, len(rows))
        assert max(len(r) for r in rows) <= 5, ch
    missing = [chr(c) for c in range(FIRST_CHAR, LAST_CHAR + 1) if chr(c) not in glyphs]
    assert not missing, missing
    return glyphs


def glyph_width(rows):
    """Ink width in px (the art's column count; the space is 3)."""
    return max(len(r) for r in rows) if any("#" in r for r in rows) else 3


def render_pair(glyphs, a, b):
    """16x16 pixel grid (rows of palette indices) for the pair a, b (chars or None)."""
    px = [[BG] * 16 for _ in range(16)]
    for cell, ch in ((0, a), (6, b)):
        if ch is None or ch == " ":
            continue
        rows = glyphs[ch]
        w = glyph_width(rows)
        x0 = cell + (max(0, 4 - w) + 1) // 2 if w < 4 else cell
        for y, r in enumerate(rows):
            for x, c in enumerate(r):
                if c == "#":
                    px[TOP + y][x0 + x] = INK
    for y in range(15, -1, -1):          # shadow right and below, only onto background
        for x in range(15, -1, -1):
            if px[y][x] == BG and ((x and px[y][x - 1] == INK) or (y and px[y - 1][x] == INK)):
                px[y][x] = SHADOW
    for y in range(16):                  # nothing past the 12 px advance
        for x in range(12, 16):
            px[y][x] = BG
    return px


def to_tiles(px):
    """16x16 grid -> 128 bytes, 4bpp, tile order TL BL TR BR (column-major), low nibble = left pixel."""
    out = bytearray()
    for tx, ty in ((0, 0), (0, 1), (1, 0), (1, 1)):
        for y in range(8):
            row = px[ty * 8 + y][tx * 8:tx * 8 + 8]
            out += bytes(row[i] | row[i + 1] << 4 for i in range(0, 8, 2))
    return bytes(out)


def pair_glyphs(glyphs=None):
    """{glyph index: 128 bytes} for every pair hi in 0x20-0x7E, lo in LO_SET."""
    glyphs = glyphs or load_glyphs()
    out = {}
    for hi in range(FIRST_CHAR, LAST_CHAR + 1):
        for lo in LO_SET:
            idx = pair_index(hi, lo)
            assert idx >= N_GLYPHS and idx not in out, (hi, lo, idx)
            out[idx] = to_tiles(render_pair(glyphs, chr(hi), chr(lo) if lo else None))
    return out


def patch(out, log, font_base):
    """Write the width table, the literal changes and every pair glyph into `out` (bytearray, grown as needed).
    font_base: ROM offset of archive file FONT_FILE. Returns the end of the glyph area."""
    orig_w = bytes(out[WIDTHS:WIDTHS + N_GLYPHS])
    assert set(orig_w) == {8, 12}
    table = bytearray([12]) * 0x10000
    table[:N_GLYPHS] = orig_w
    put(out, log, NEW_WIDTHS, bytes(table), "font: width table")
    for a in WIDTH_LITS:
        assert struct.unpack_from("<I", out, a)[0] == 0x08000000 + WIDTHS, hex(a)
        put(out, log, a, struct.pack("<I", 0x08000000 + NEW_WIDTHS), "font: width table pointer")
    for a in THRESHOLD_LITS:
        assert struct.unpack_from("<I", out, a)[0] == 0x813F, hex(a)
        put(out, log, a, struct.pack("<I", 0x1F), "font: mapper threshold")
    end = 0
    for idx, data in sorted(pair_glyphs().items()):
        at = font_base + idx * 128
        assert at >= NEW_WIDTHS + 0x10000
        put(out, log, at, data, None)
        end = max(end, at + 128)
    lo_at = font_base + min(pair_glyphs_index_range()) * 128
    log.append((lo_at, end, "font: pair glyphs"))
    return end


def pair_glyphs_index_range():
    return [pair_index(h, l) for h in range(FIRST_CHAR, LAST_CHAR + 1) for l in LO_SET]


def put(out, log, at, data, what):
    if len(out) < at + len(data):
        out += b"\xff" * (at + len(data) - len(out))
    out[at:at + len(data)] = data
    if what:
        log.append((at, at + len(data), what))


# ---------------------------------------------------------------- encoder
TOKENS = re.compile(r"\[[0-9A-Fa-f]{2}\]|.", re.S)


def encode(s, sjis_encode):
    """English text -> bytes. ASCII is one byte per char; any other char (or [XX] token run) goes through
    `sjis_encode` and is aligned to an even offset (the mappers read 2-byte units). The result has even length
    (a trailing space is added), so the NUL the caller appends starts a unit."""
    out = bytearray()
    for tok in TOKENS.findall(s):
        if len(tok) == 4 and tok[0] == "[":          # raw byte [XX]: kept as is, no alignment
            out.append(int(tok[1:3], 16))
        elif FIRST_CHAR <= ord(tok) <= LAST_CHAR:
            out.append(ord(tok))
        else:
            raw = sjis_encode(tok)
            if len(out) % 2:
                out.append(0x20)
            out += raw
    if len(out) % 2:
        out.append(0x20)
    return bytes(out)


def widen(s):
    """ASCII -> fullwidth SJIS-able text (space -> U+3000), for rows the game reads as 2-byte codes in 8 px slots
    (name-entry grid, default names and words: `"wide": true` in script/rom)."""
    return "".join("　" if c == " " else chr(ord(c) + 0xFEE0) if "!" <= c <= "~" else c for c in s)


def width_px(s):
    """Pixel width of an encoded English string (6 px per ASCII char, 12 per 2-byte char)."""
    n, w = 0, 0
    for ch in s:
        if FIRST_CHAR <= ord(ch) <= LAST_CHAR:
            n += 1
        else:
            n += n % 2
            w += 12
    return w + 6 * (n + n % 2)


def sheet(path):
    from PIL import Image
    g = load_glyphs()
    chars = [chr(c) for c in range(FIRST_CHAR, LAST_CHAR + 1)]
    text = ["".join(chars[i:i + 32]) for i in range(0, len(chars), 32)] + [
        "The quick brown fox jumps over", "the lazy dog. Vattroller X! 12%"]
    pal = {BG: (40, 40, 64), INK: (255, 255, 255), SHADOW: (90, 90, 120)}
    img = Image.new("RGB", (6 * 34, 16 * len(text)), pal[BG])
    for row, t in enumerate(text):
        t = t + " " * (len(t) % 2)
        for i in range(0, len(t), 2):
            px = render_pair(g, t[i], t[i + 1])
            for y in range(16):
                for x in range(12):
                    img.putpixel((i * 6 + x, row * 16 + y), pal[px[y][x]])
    img.resize((img.width * 4, img.height * 4), Image.NEAREST).save(path)


if __name__ == "__main__":
    if "--sheet" in sys.argv:
        sheet(sys.argv[sys.argv.index("--sheet") + 1])
    else:
        print(__doc__)
