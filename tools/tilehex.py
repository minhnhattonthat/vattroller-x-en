"""tilehex.py: print 4bpp tiles of an archive file as colour indices (one hex digit per pixel), tiles side by side.

    python -X utf8 tools/tilehex.py work/gfx/unpacked/0431_raw.bin 166,167,168 160-162
Each argument is one run: comma-separated tile numbers and/or a-b ranges, printed left to right.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402


def tiles(run):
    out = []
    for part in run.split(","):
        a, _, b = part.partition("-")
        out += range(int(a), int(b or a) + 1)
    return out


def main():
    data = Path(sys.argv[1]).read_bytes()
    for run in sys.argv[2:]:
        ts = tiles(run)
        print("run", run)
        for y in range(8):
            print(" ".join("".join("%x" % c for c in gfx.tile_px(data, t)[y]) for t in ts))


if __name__ == "__main__":
    main()
