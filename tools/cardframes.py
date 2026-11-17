"""cardframes.py: decode and draw the VS rule-card sprite frames (archive #441, G12).

Animation set at ROM 0x273B94: {u32 #441 ROM ptr, u16 frames=26, u16 8, u32 frame table 0x273BA4, ...}.
Frame = {u16 0, u16 count, u32 0, u32 ptr}; record = 6 x u16 {attr0 shape bits, attr1 size bits, palette,
#441 byte offset, y (8-bit), x (9-bit)}, the same layout as the #437 help bubbles (tools/helpbub.py).

    python -X utf8 tools/cardframes.py --list                  # records per frame
    python -X utf8 tools/cardframes.py --draw OUT.png [--rom build/vattroller_x_en.gba]   # every frame, labelled
"""
import argparse
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import archive  # noqa: E402

SET = 0x273B94
SIZES = {0: [(8, 8), (16, 16), (32, 32), (64, 64)], 1: [(16, 8), (32, 8), (32, 16), (64, 32)],
         2: [(8, 16), (8, 32), (16, 32), (32, 64)]}


def frames(rom):
    ptr, n, _, table = struct.unpack_from("<IHHI", rom, SET)
    out = []
    for i in range(n):
        _, cnt, _, p = struct.unpack_from("<HHII", rom, (table & 0x1FFFFFF) + 12 * i)
        recs = []
        for k in range(cnt):
            a0, a1, pal, off, y, x = struct.unpack_from("<6H", rom, (p & 0x1FFFFFF) + 12 * k)
            if a0 >> 14 == 3:          # prohibited shape: not a sprite (seen at frame ends)
                continue
            w, h = SIZES[a0 >> 14][a1 >> 14]
            x = x & 0x1FF
            x = x - 512 if x >= 256 else x
            y = y & 0xFF
            y = y - 256 if y >= 128 else y
            recs.append(dict(off=off, w=w, h=h, x=x, y=y, pal=pal))
        out.append(recs)
    return out


def draw(rom, data, path, zoom=2):
    from PIL import Image, ImageDraw
    pal = [(255, 0, 255), (40, 40, 40), (250, 250, 250), (200, 200, 200), (20, 20, 120)] + \
          [(min(255, i * 20), max(0, 200 - i * 10), 100) for i in range(5, 16)]
    fr = frames(rom)
    cw, ch = 200, 120
    cols = 4
    im = Image.new("RGB", (cols * cw, (len(fr) + cols - 1) // cols * ch), (255, 0, 255))
    dr = ImageDraw.Draw(im)
    for i, recs in enumerate(fr):
        ox, oy = (i % cols) * cw + 100, (i // cols) * ch + 60
        for r in reversed(recs):       # first record on top
            for y in range(r["h"]):
                for x in range(r["w"]):
                    t = (y // 8) * (r["w"] // 8) + x // 8
                    a = r["off"] + t * 32 + (y % 8) * 4 + (x % 8) // 2
                    if a >= len(data):
                        continue
                    c = data[a] >> 4 * (x & 1) & 15
                    px, py = ox + r["x"] + x, oy + r["y"] + y
                    if c and 0 <= px - (i % cols) * cw < cw and 0 <= py - (i // cols) * ch < ch:
                        im.putpixel((px, py), pal[c])
        dr.text(((i % cols) * cw + 2, (i // cols) * ch + 2), str(i), fill=(255, 255, 0))
    im.resize((im.width * zoom, im.height * zoom), Image.NEAREST).save(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rom", default="rom/Vattroller X (Japan).gba")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--draw")
    ap.add_argument("--gfx", action="store_true", help="draw #441 as gfx.sheet_441 redraws it (no build needed)")
    a = ap.parse_args()
    rom = Path(a.rom).read_bytes()
    if a.list:
        for i, recs in enumerate(frames(rom)):
            print(i, " ".join(f"{r['off']:04x}:{r['w']}x{r['h']}@{r['x']},{r['y']}" for r in recs))
    if a.draw:
        data = archive.Archive(rom).file(441)
        if a.gfx:
            import gfx
            data = gfx.sheet_441(data)
        draw(rom, data, a.draw)
    print("blocks no CARD_LINES entry redraws:", " ".join(f"{o:04x}" for o in uncovered(rom)) or "none")


def uncovered(rom):
    """#441 blocks some frame shows that no gfx.CARD_LINES line owns (the VS letters are art, skipped)."""
    import gfx
    owned = {b[0] for ln in gfx.CARD_LINES for k in ("front", "back", "blank") for b in ln.get(k, [])}
    vs = {r["off"] for i in range(5, 11) for r in frames(rom)[i]}
    return sorted({r["off"] for f in frames(rom) for r in f} - owned - vs)


if __name__ == "__main__":
    main()
