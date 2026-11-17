"""Render each enabled text BG of a PPU dump (ppu.vram/pal/io.bin) to DIR/bgN.png (256x256, map as stored, 4bpp)
and print the screen origin (scroll). Usage: python bgrender.py DIR"""
import struct
import sys
from PIL import Image

d = sys.argv[1].rstrip("/") + "/"
io = open(d + "ppu.io.bin", "rb").read()
v = open(d + "ppu.vram.bin", "rb").read()
p = open(d + "ppu.pal.bin", "rb").read()


def rgb(i):
    c = struct.unpack_from("<H", p, i * 2)[0]
    return ((c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8)


disp = struct.unpack_from("<H", io, 0)[0]
for b in range(4):
    if not disp >> (8 + b) & 1:
        continue
    c = struct.unpack_from("<H", io, 8 + 2 * b)[0]
    cb, sb = (c >> 2 & 3) * 0x4000, (c >> 8 & 31) * 0x800
    hof, vof = struct.unpack_from("<HH", io, 0x10 + 4 * b)
    print(f"bg{b} prio {c & 3} cb {cb:#x} sb {sb:#x} scroll {hof & 511},{vof & 511}")
    im = Image.new("RGB", (256, 256), (255, 0, 255))
    for ty in range(32):
        for tx in range(32):
            e = struct.unpack_from("<H", v, sb + (ty * 32 + tx) * 2)[0]
            t, hf, vf, pal = e & 1023, e >> 10 & 1, e >> 11 & 1, e >> 12
            for y in range(8):
                for x in range(8):
                    sx, sy = (7 - x if hf else x), (7 - y if vf else y)
                    a = cb + t * 32 + sy * 4 + sx // 2
                    if a >= 0x10000:
                        continue
                    k = v[a] >> 4 * (sx & 1) & 15
                    if k:
                        im.putpixel((tx * 8 + x, ty * 8 + y), rgb(pal * 16 + k))
    im.save(d + f"bg{b}.png")
