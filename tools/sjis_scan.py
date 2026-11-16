"""sjis_scan.py: find Shift-JIS text runs in the ROM and summarise where they cluster.

    python -X utf8 tools/sjis_scan.py [--min 3] [--bin 0x10000] [--dump START END]

A run = consecutive valid 2-byte SJIS chars (lead 0x81-0x9F/0xE0-0xEF) plus ASCII printables, >= --min SJIS chars.
--dump prints each run in START..END with its offset, terminator byte and any 0x08xxxxxx pointers to it."""
import argparse
import struct
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Vattroller X (Japan).gba"


def is_lead(b):
    return 0x81 <= b <= 0x9F or 0xE0 <= b <= 0xEF


def runs(d, min_sjis=3):
    i, n = 0, len(d)
    while i < n - 1:
        if is_lead(d[i]) and 0x40 <= d[i + 1] <= 0xFC and d[i + 1] != 0x7F:
            start, j, cnt = i, i, 0
            while j < n - 1:
                if is_lead(d[j]) and 0x40 <= d[j + 1] <= 0xFC and d[j + 1] != 0x7F:
                    try:
                        d[j:j + 2].decode("shift_jis")
                    except UnicodeDecodeError:
                        break
                    j += 2
                    cnt += 1
                elif 0x20 <= d[j] < 0x7F or d[j] in (0x0A,):
                    j += 1
                else:
                    break
            if cnt >= min_sjis:
                yield start, j, cnt
                i = j
                continue
        i += 1


def pointer_index(d):
    idx = {}
    for o in range(0, len(d) - 3, 4):
        v = struct.unpack_from("<I", d, o)[0]
        if 0x08000000 <= v < 0x08000000 + len(d):
            idx.setdefault(v - 0x08000000, []).append(o)
    return idx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=int, default=3)
    ap.add_argument("--bin", type=lambda s: int(s, 0), default=0x10000)
    ap.add_argument("--dump", nargs=2, type=lambda s: int(s, 0))
    a = ap.parse_args()
    d = ROM.read_bytes()
    rs = list(runs(d, a.min))
    if a.dump:
        ptrs = pointer_index(d)
        for s, e, c in rs:
            if a.dump[0] <= s < a.dump[1]:
                txt = d[s:e].decode("shift_jis", "replace")
                p = ",".join(hex(x) for x in ptrs.get(s, [])[:3])
                print(f"{s:06x} {e - s:4d} term={d[e]:02x} ptr=[{p}] {txt}")
        return
    bins = Counter()
    for s, e, c in rs:
        bins[s // a.bin] += c
    print(f"runs: {len(rs)}  sjis chars: {sum(c for _, _, c in rs)}")
    for k in sorted(bins):
        print(f"{k * a.bin:07x}  {bins[k]:6d}")


if __name__ == "__main__":
    main()
