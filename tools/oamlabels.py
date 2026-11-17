"""oamlabels.py: which tiles of a UI sprite sheet each visible sprite shows (to find a label's tile run).

    python -X utf8 tools/oamlabels.py --file 446 DUMPDIR [DUMPDIR..]

DUMPDIR holds ppu.oam.bin + ppu.vram.bin (warp.py SCENE --script work/qa/probe/dumpat.lua --var DUMP_AT=N).
Sprite tiles (1D mapping, OBJ VRAM at 0x10000) are matched by content against the ORIGINAL archive file, so tiles
already redrawn in the build show as "--". Prints one line per distinct run: sheet tile ids | where.
Identical tiles map to the FIRST copy: #446 has "▶けってい" twice (4-7 and 99-102), so a run printed "99 5 6 7"
is really 99-102. Check a run's neighbours before redrawing.
"""
import argparse
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import archive  # noqa: E402

SHAPES = {(0, 0): (8, 8), (0, 1): (16, 16), (0, 2): (32, 32), (0, 3): (64, 64), (1, 0): (16, 8), (1, 1): (32, 8),
          (1, 2): (32, 16), (1, 3): (64, 32), (2, 0): (8, 16), (2, 1): (8, 32), (2, 2): (16, 32), (2, 3): (32, 64)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", type=int, required=True)
    ap.add_argument("dumps", nargs="+")
    a = ap.parse_args()
    src = archive.unpack(archive.Archive().file(a.file))[0]
    tiles = {}
    for i in range(len(src) // 32):
        t = src[i * 32:i * 32 + 32]
        if any(t):
            tiles.setdefault(t, i)
    runs = {}
    pres = []    # a dump dir (ppu.*.bin), a dir of dumpevery.lua dumps (d<frame>.*.bin, any depth) or a prefix
    for d in map(Path, a.dumps):
        if (d / "ppu.oam.bin").exists():
            pres.append(d / "ppu")
        elif d.is_dir():
            pres += sorted(Path(str(p)[:-len(".oam.bin")]) for p in d.rglob("d*.oam.bin"))
        else:
            pres.append(d)
    for pre in pres:
        d = pre.parent if pre.name == "ppu" else pre
        o = Path(f"{pre}.oam.bin").read_bytes()
        v = Path(f"{pre}.vram.bin").read_bytes()
        for i in range(128):
            a0, a1, a2 = struct.unpack_from("<HHH", o, i * 8)
            if (a0 >> 8) & 3 == 2:
                continue
            y, x = a0 & 0xFF, a1 & 0x1FF
            if y >= 160 or x >= 240:
                continue
            w, h = SHAPES[(a0 >> 14, a1 >> 14)]
            t0 = a2 & 0x3FF
            idx = [tiles.get(v[0x10000 + (t0 + k) * 32:0x10000 + (t0 + k + 1) * 32]) for k in range(w * h // 64)]
            if all(j is None for j in idx):
                continue
            runs.setdefault(tuple(idx), set()).add(f"{d.name}@{x},{y} {w}x{h}")
    for key, where in sorted(runs.items(), key=lambda kv: min(j for j in kv[0] if j is not None)):
        print(" ".join("--" if j is None else str(j) for j in key), "|", "; ".join(sorted(where))[:200])


if __name__ == "__main__":
    main()
