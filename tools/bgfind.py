"""bgfind.py: which BG map entries cover a screen rectangle, and where their tiles come from in the archive.

    python -X utf8 tools/bgfind.py DUMPDIR x,y,w,h [--bg N]

DUMPDIR holds ppu.vram.bin + ppu.io.bin (warp.py SCENE --script tools/lua/dumpscene.lua). For each enabled text BG
(or only --bg N) prints the map rows under the rectangle (tile id, palette, flips) and, for every distinct
non-empty tile, the archive files in work/gfx/unpacked/ that hold the same 32 bytes (file name @ tile index).
"""
import argparse
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dump")
    ap.add_argument("rect")
    ap.add_argument("--bg", type=int)
    a = ap.parse_args()
    d = Path(a.dump)
    io = (d / "ppu.io.bin").read_bytes()
    v = (d / "ppu.vram.bin").read_bytes()
    x0, y0, w, h = (int(s) for s in a.rect.split(","))
    disp = struct.unpack_from("<H", io, 0)[0]
    unpacked = [(f.name, f.read_bytes()) for f in sorted((ROOT / "work" / "gfx" / "unpacked").glob("*.bin"))]
    for b in range(4):
        if not disp >> (8 + b) & 1 or (a.bg is not None and b != a.bg):
            continue
        cnt = struct.unpack_from("<H", io, 8 + 2 * b)[0]
        sx, sy = (s & 0x1FF for s in struct.unpack_from("<HH", io, 0x10 + 4 * b))
        cb, sb, size = (cnt >> 2 & 3) * 0x4000, (cnt >> 8 & 31) * 0x800, cnt >> 14
        tiles = {}
        print(f"bg{b} cb {cb:#x} sb {sb:#x} scroll {sx},{sy}")
        for ty in range((y0 + sy) // 8, (y0 + h - 1 + sy) // 8 + 1):
            row = []
            for tx in range((x0 + sx) // 8, (x0 + w - 1 + sx) // 8 + 1):
                mx, my = tx % (64 if size & 1 else 32), ty % (64 if size & 2 else 32)
                blk = (mx // 32) + (my // 32) * (2 if size & 1 else 1)
                e = struct.unpack_from("<H", v, sb + blk * 0x800 + ((my % 32) * 32 + mx % 32) * 2)[0]
                t = e & 0x3FF
                data = v[cb + t * 32:cb + t * 32 + 32]
                row.append(f"{t:03x}p{e >> 12:x}{'h' if e & 0x400 else ''}{'v' if e & 0x800 else ''}")
                if any(data):
                    tiles[t] = data
            print(f"  y{ty:02d}: " + " ".join(row))
        for t, data in sorted(tiles.items()):
            hits = [f"{n}@{i // 32}" for n, buf in unpacked for i in range(0, len(buf) - 31, 32) if buf[i:i + 32] == data]
            print(f"  tile {t:03x}: {' '.join(hits[:6]) or 'not found raw'}")


if __name__ == "__main__":
    sys.exit(main())
