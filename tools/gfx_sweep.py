"""gfx_sweep.py: static graphics-text sweep over the resource archive (docs/re/archive.md).

    python -X utf8 tools/gfx_sweep.py --out work/gfx [--fmt gba4|gba8] [--width 64] [--page-h 1024] [--files 100-200]

Renders every archive file (LZ10 ones decompressed) as tiles in a grey ramp, packs them into numbered pages with a
label strip per file, and writes index.tsv (page, y, file, size, how rendered). Files skipped (palettes, scripts,
tiny tables) are listed in skipped.tsv with the reason; none are dropped silently."""
import argparse
import struct
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from archive import Archive, unpack  # noqa: E402


def sjis_density(b):
    n = 0
    i = 0
    while i < len(b) - 1:
        if (0x81 <= b[i] <= 0x9F or 0xE0 <= b[i] <= 0xEF) and 0x40 <= b[i + 1] <= 0xFC:
            n += 1
            i += 2
        else:
            i += 1
    return 2 * n / max(1, len(b))


def render_tiles(data, fmt, cols):
    bpt = 32 if fmt == "gba4" else 64
    nt = len(data) // bpt
    rows = (nt + cols - 1) // cols
    img = Image.new("L", (cols * 8, max(1, rows) * 8), 0)
    px = img.load()
    for t in range(nt):
        tx, ty = (t % cols) * 8, (t // cols) * 8
        base = t * bpt
        for y in range(8):
            for x in range(8):
                if fmt == "gba4":
                    v = data[base + y * 4 + x // 2]
                    v = (v >> 4) if x & 1 else (v & 15)
                    v *= 17
                else:
                    v = data[base + y * 8 + x]
                px[tx + x, ty + y] = v
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--fmt", default="gba4", choices=["gba4", "gba8"])
    ap.add_argument("--width", type=int, default=64, help="tiles per row")
    ap.add_argument("--page-h", type=int, default=1024)
    ap.add_argument("--files", help="index range a-b")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    ar = Archive()
    lo, hi = (0, len(ar)) if not a.files else map(int, a.files.split("-"))
    pages, cur, y = [], None, 0
    index, skipped = [], []

    def new_page():
        nonlocal cur, y
        cur = Image.new("L", (a.width * 8, a.page_h), 40)
        pages.append(cur)
        y = 0

    new_page()
    for i in range(lo, min(hi, len(ar))):
        data, how = unpack(ar.file(i))
        if len(data) <= 0x200:
            skipped.append((i, len(data), "<=0x200 bytes (palette or table)"))
            continue
        dens = sjis_density(data)
        if dens > 0.25:
            skipped.append((i, len(data), f"script/text file (SJIS density {dens:.2f})"))
            continue
        img = render_tiles(data, a.fmt, a.width)
        h = img.height + 9
        if y + h > a.page_h:
            if y == 0:
                pass
            else:
                new_page()
        if h > a.page_h:  # split tall images across pages
            top = 0
            while top < img.height:
                part = img.crop((0, top, img.width, min(img.height, top + a.page_h - 9)))
                if y + part.height + 9 > a.page_h:
                    new_page()
                ImageDraw.Draw(cur).text((1, y - 1), f"#{i} +{top // 8 * a.width * (32 if a.fmt == 'gba4' else 64):x}",
                                         fill=255)
                cur.paste(part, (0, y + 9))
                index.append((len(pages), y, i, len(data), how + f" part@row{top // 8}"))
                y += part.height + 9
                top += part.height
            continue
        ImageDraw.Draw(cur).text((1, y - 1), f"#{i}", fill=255)
        cur.paste(img, (0, y + 9))
        index.append((len(pages), y, i, len(data), how))
        y += h
    for n, p in enumerate(pages, 1):
        p.crop((0, 0, p.width, p.height)).save(out / f"page{n:03d}.png")
    with open(out / "index.tsv", "w", encoding="utf-8") as f:
        f.write("page\ty\tfile\tsize\thow\n")
        for r in index:
            f.write("\t".join(map(str, r)) + "\n")
    with open(out / "skipped.tsv", "w", encoding="utf-8") as f:
        f.write("file\tsize\treason\n")
        for r in skipped:
            f.write("\t".join(map(str, r)) + "\n")
    print(f"pages {len(pages)}  rendered {len(index)}  skipped {len(skipped)}  -> {out}")


if __name__ == "__main__":
    main()
