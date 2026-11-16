"""rooms.py: write tools/debug/rooms.json, the room list the warp tool uses (docs/re/debug.md).

    python -X utf8 tools/debug/rooms.py           # regenerate rooms.json from the ROM
    python -X utf8 tools/debug/rooms.py --list    # print id, name, event file, entry points

Rooms: 236 records of 40 bytes at ROM 0x0BC20 (+0 name pointer, +0x0E map-data file, +0x10 event file).
Entry points: every script teleport (op 0x05: u16 room, x, y, facing|flags<<8) found in the event files, most used
first. A room no teleport targets has no entry; the warp then keeps the spawn of the book it came from.
"""
import json
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from archive import Archive  # noqa: E402

TABLE, COUNT, STRIDE = 0x0BC20, 236, 40
OUT = Path(__file__).with_name("rooms.json")


def rooms(ar):
    rom = ar.rom
    entries = defaultdict(Counter)
    for i in range(2475, 2714):
        b = ar.file(i)
        for o in range(0, len(b) - 12, 4):
            op, sz, room, x, y, f = struct.unpack_from("<6H", b, o)
            if op == 5 and sz == 12 and room < COUNT and x < 256 and y < 256 and (f & 0xFF) < 8 and (x or y):
                entries[room][(x, y, f)] += 1
    out = []
    for r in range(COUNT):
        rec = TABLE + r * STRIDE
        p = struct.unpack_from("<I", rom, rec)[0] - 0x08000000
        name = rom[p:rom.index(b"\0", p)].decode("cp932")
        h = struct.unpack_from("<20H", rom, rec)
        out.append({"id": r, "name": name, "map": h[7], "event": h[8],
                    "entries": [list(k) for k, _ in entries[r].most_common(3)]})
    return out


def main():
    data = rooms(Archive())
    if "--list" in sys.argv:
        for d in data:
            print(d["id"], d["name"], d["event"], d["entries"][:1])
        return
    OUT.write_text("[\n" + ",\n".join(json.dumps(d, ensure_ascii=False) for d in data) + "\n]\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(data)} rooms, {sum(1 for d in data if d['entries'])} with entry points)")


if __name__ == "__main__":
    main()
