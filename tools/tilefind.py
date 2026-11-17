"""tilefind.py: find a VRAM tile in the unpacked archive files up to a colour remap (same pixel partition, any
palette indices), for sprites/BG tiles stored with other colour numbers than VRAM shows.

    python -X utf8 tools/tilefind.py work/qa/warp/X/ppu.vram.bin 0x10840 [0x10860 ..] [--dir work/gfx/unpacked]
Offsets are byte offsets into the VRAM dump (OBJ tiles start at 0x10000). Prints file@tile and the colour map.
"""
import argparse
from pathlib import Path


def px(t):
    return [(b >> s) & 15 for b in t for s in (0, 4)]


def canon(p):
    m, out = {}, []
    for c in p:
        m.setdefault(c, len(m))
        out.append(m[c])
    return tuple(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vram")
    ap.add_argument("offs", nargs="+")
    ap.add_argument("--dir", default="work/gfx/unpacked")
    a = ap.parse_args()
    v = Path(a.vram).read_bytes()
    want = {}
    for o in a.offs:
        o = int(o, 0)
        p = px(v[o:o + 32])
        if len(set(p)) > 1:
            want.setdefault(canon(p), []).append(o)
    for f in sorted(Path(a.dir).iterdir()):
        d = f.read_bytes()
        for n in range(len(d) // 32):
            p = px(d[n * 32:n * 32 + 32])
            c = canon(p)
            if c in want:
                vp = px(v[want[c][0]:want[c][0] + 32])
                cmap = sorted({(s, t) for s, t in zip(p, vp)})
                print(f"{[hex(o) for o in want[c]]} = {f.name}@{n} colours {cmap}")


if __name__ == "__main__":
    main()
