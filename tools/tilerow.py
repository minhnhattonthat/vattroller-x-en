"""tilerow.py: render runs of tiles from an archive file (original), one run per row, zoomed, with grey shades.

    python -X utf8 tools/tilerow.py --file 446 OUT.png 42-45 52-55 97-98 ...
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import archive  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", type=int, required=True)
    ap.add_argument("--zoom", type=int, default=4)
    ap.add_argument("out")
    ap.add_argument("runs", nargs="+")
    a = ap.parse_args()
    from PIL import Image, ImageDraw
    data = archive.unpack(archive.Archive().file(a.file))[0]
    runs = [list(range(int(r.split("-")[0]), int(r.split("-")[-1]) + 1)) for r in a.runs]
    w = 40 + 8 * max(len(r) for r in runs)
    im = Image.new("RGB", (w, 10 * len(runs)), (255, 0, 255))
    dr = ImageDraw.Draw(im)
    for k, run in enumerate(runs):
        dr.text((0, 10 * k), str(run[0]), fill=(0, 0, 0))
        for j, n in enumerate(run):
            t = data[n * 32:n * 32 + 32]
            for y in range(8):
                for x in range(8):
                    v = (t[y * 4 + x // 2] >> 4 * (x & 1)) & 15
                    im.putpixel((40 + 8 * j + x, 10 * k + y), (255 - 16 * v,) * 3 if v else (120, 200, 255))
    im.resize((im.width * a.zoom, im.height * a.zoom), Image.NEAREST).save(a.out)


if __name__ == "__main__":
    main()
