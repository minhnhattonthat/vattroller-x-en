"""romtext.py: write the ROM strings of script/rom/ (docs/re/text.md) into a built ROM.

- `r<addr>` strings (kind string): the new bytes go to free space and every pointer word in `ptrs` is repointed
  (each word is first checked to hold the string's original address).
- `c<addr>` credits: in place, in the 0x28-byte slot of the fixed record (`max` bytes + NUL).
- `n<addr>` no-pointer strings: in place, at most `max` bytes, padded with NUL.
Rows of kind `data` are never written.
"""
import struct

STR_START, STR_END = 0x810000, 0x9AC000    # between the font width table and the pair glyphs (font.py)


class Alloc:
    def __init__(self, start=STR_START, end=STR_END):
        self.at, self.end = start, end

    def take(self, n):
        at = self.at
        self.at = (at + n + 3) & ~3
        if self.at > self.end:
            raise SystemExit(f"romtext: string area full ({self.end:#x})")
        return at


def put(out, log, at, data, what):
    if len(out) < at + len(data):
        out += b"\xff" * (at + len(data) - len(out))
    out[at:at + len(data)] = data
    log.append((at, at + len(data), what))


def apply(out, log, rows, enc, alloc=None):
    """rows: [(row, new text)] from script/rom/*.json. Returns the number written."""
    alloc = alloc or Alloc()
    n = 0
    for r, s in rows:
        kind, rid = r["kind"], r["id"]
        if kind == "data":
            continue
        raw = enc(s)
        if kind == "string":
            orig = int(rid[1:], 16)
            data = raw + b"\0"
            at = alloc.take(len(data))
            put(out, log, at, data, rid)
            for p in r["ptrs"]:
                p = int(p, 16)
                assert struct.unpack_from("<I", out, p)[0] == 0x08000000 + orig, (rid, hex(p))
                put(out, log, p, struct.pack("<I", 0x08000000 + at), f"{rid} ptr")
        elif kind in ("credit", "noptr"):
            at, cap = int(rid[1:], 16), r["max"]
            if len(raw) > cap:
                raise SystemExit(f"romtext: {rid} is {len(raw)} bytes, max {cap}")
            put(out, log, at, raw + b"\0" * (cap + 1 - len(raw)) if kind == "credit" else
                raw + b"\0" * (cap - len(raw)), rid)
        else:
            raise SystemExit(f"romtext: unknown kind {kind} ({rid})")
        n += 1
    return n
