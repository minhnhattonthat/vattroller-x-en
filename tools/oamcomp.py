"""oamcomp.py: composite the sprites of a PPU dump (4bpp, 1D mapping, no affine) into a PNG, optionally only some
OAM indices, and say where each sprite's tile block sits in the unpacked archive files.

    python -X utf8 tools/oamcomp.py DUMPDIR OUT.png [--ids 0-25] [--find work/gfx/unpacked] [--zoom 4]

DUMPDIR holds ppu.vram.bin / ppu.pal.bin / ppu.oam.bin (L.dump_ppu("ppu")). Lower OAM index draws on top.
"""
import argparse
import glob
import os
import struct

from PIL import Image

SZ = {(0, 0): (8, 8), (0, 1): (16, 16), (0, 2): (32, 32), (0, 3): (64, 64), (1, 0): (16, 8), (1, 1): (32, 8),
      (1, 2): (32, 16), (1, 3): (64, 32), (2, 0): (8, 16), (2, 1): (8, 32), (2, 2): (16, 32), (2, 3): (32, 64)}


def sprites(oam):
    for i in range(128):
        a0, a1, a2 = struct.unpack_from("<HHH", oam, i * 8)
        if a0 >> 8 & 3 == 2 or a0 >> 13 & 1:          # hidden, or 8bpp (not handled)
            continue
        w, h = SZ[(a0 >> 14, a1 >> 14)]
        y, x = a0 & 255, a1 & 511
        if y >= 160 or x >= 240:
            continue
        yield dict(i=i, x=x, y=y, w=w, h=h, tile=a2 & 1023, pal=a2 >> 12, hf=a1 >> 12 & 1, vf=a1 >> 13 & 1)


def parse_ids(s):
    out = set()
    for part in s.split(","):
        a, _, b = part.partition("-")
        out.update(range(int(a), int(b or a) + 1))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dump")
    ap.add_argument("out")
    ap.add_argument("--ids")
    ap.add_argument("--find")
    ap.add_argument("--zoom", type=int, default=4)
    a = ap.parse_args()
    d = a.dump
    v = open(os.path.join(d, "ppu.vram.bin"), "rb").read()
    p = open(os.path.join(d, "ppu.pal.bin"), "rb").read()
    oam = open(os.path.join(d, "ppu.oam.bin"), "rb").read()
    obj = v[0x10000:]
    ids = parse_ids(a.ids) if a.ids else None
    sps = [s for s in sprites(oam) if ids is None or s["i"] in ids]
    files = {}
    if a.find:
        files = {os.path.basename(f): open(f, "rb").read() for f in glob.glob(os.path.join(a.find, "*.bin"))}
    im = Image.new("RGB", (240, 160), (255, 0, 255))
    for s in reversed(sps):
        n = s["w"] * s["h"] // 64
        block = obj[s["tile"] * 32:(s["tile"] + n) * 32]
        where = [(f, hex(b.find(block))) for f, b in files.items() if block in b][:2]
        print(f"{s['i']:3} x{s['x']:3} y{s['y']:3} {s['w']}x{s['h']} tile {s['tile']} pal {s['pal']} {where}")
        tw = s["w"] // 8
        for yy in range(s["h"]):
            for xx in range(s["w"]):
                sx = s["w"] - 1 - xx if s["hf"] else xx
                sy = s["h"] - 1 - yy if s["vf"] else yy
                t = (sy // 8) * tw + sx // 8
                k = block[t * 32 + (sy % 8) * 4 + (sx % 8) // 2] >> 4 * (sx & 1) & 15
                if k and 0 <= s["x"] + xx < 240 and 0 <= s["y"] + yy < 160:
                    c = struct.unpack_from("<H", p, 0x200 + (s["pal"] * 16 + k) * 2)[0]
                    im.putpixel((s["x"] + xx, s["y"] + yy), ((c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8))
    im.resize((240 * a.zoom, 160 * a.zoom), Image.NEAREST).save(a.out)


if __name__ == "__main__":
    main()
