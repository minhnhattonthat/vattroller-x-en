"""script_fmt.py: event-script command streams inside archive files (docs/re/script.md).

A stream is a run of 4-byte-aligned commands: u16 op, u16 size (bytes, header included, multiple of 4), args.
Op 0 is a text line: u16 0, u16 size, u16 flags, u16 len, then `len` bytes of Shift-JIS, a NUL, padding to 4.

    python -X utf8 tools/script_fmt.py survey        # find every stream that walks cleanly to its file end
    python -X utf8 tools/script_fmt.py ops           # opcode histogram with sizes"""
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from archive import Archive  # noqa: E402


def walk(b, start, end=None):
    """Commands from start; returns list of (off, op, size) or None if the walk does not land exactly on end."""
    end = len(b) if end is None else end
    o, out = start, []
    while o < end:
        if o + 4 > end:
            return None
        op, size = struct.unpack_from("<HH", b, o)
        if size < 4 or size % 4 or o + size > end or op > 0xFF:
            return None
        if op == 0:
            if size < 8:
                return None
            n = struct.unpack_from("<H", b, o + 6)[0]
            if 8 + n + 1 > size or b[o + 8 + n] != 0:
                return None
        out.append((o, op, size))
        o += size
    return out if o == end else None


def find_stream(b):
    """Smallest 4-aligned start whose walk lands on the file end and holds at least one text command."""
    for s in range(0, len(b) - 8, 4):
        w = walk(b, s)
        if w and any(op == 0 for _, op, _ in w):
            return s, w
    return None, None


def text_files(ar):
    for i in range(len(ar)):
        b = ar.file(i)
        if b.count(b"\x00\x00") and any(0x81 <= x <= 0x83 for x in b[:: max(1, len(b) // 64)]):
            yield i, b


def main():
    ar = Archive()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "survey"
    found, ops, sizes = {}, Counter(), defaultdict(Counter)
    for i in range(len(ar)):
        b = ar.file(i)
        if b.find(b"\x82") < 0:
            continue
        s, w = find_stream(b)
        if w:
            found[i] = (s, w)
            for _, op, sz in w:
                ops[op] += 1
                sizes[op][sz] += 1
    if cmd == "survey":
        starts = Counter(s for s, _ in found.values())
        print(f"files with a clean stream: {len(found)}; text commands: {sum(c for o, c in ops.items() if o == 0)}")
        print("stream start offsets:", starts.most_common(10))
        print("files:", min(found), "..", max(found))
    else:
        for op, n in sorted(ops.items()):
            print(f"op {op:02x} x{n:6d} sizes {dict(sizes[op].most_common(4))}")


if __name__ == "__main__":
    main()
