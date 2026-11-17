"""build.py: build the patched ROM.

    python -X utf8 tools/build.py              # -> build/vattroller_x_en.gba (+ .writes.tsv for romdiff)
    python -X utf8 tools/build.py --marker     # -> build/vattroller_x_marker.gba: every string replaced by its id
    python -X utf8 tools/build.py --identity   # rebuild with no text and no engine; exit 1 unless byte-identical

Steps: check the dump against rom.sha1, parse every event file (tools/events.py), put the English (or the markers)
into the event files, rebuild each through the relocating serializer, write them back (archive.write_files), then
the engine (tools/font.py: pair-glyph font, width table) and the ROM strings (tools/romtext.py).

ROM layout past the original 8 MiB: 0x800000 width table, 0x810000-0x9AC000 ROM strings, 0x9ACE44-0xBE4DC4 pair
glyphs (fixed by the glyph index formula), 0xBE8000+ relocated event files."""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import archive  # noqa: E402
import check_rom  # noqa: E402
import events  # noqa: E402
import font  # noqa: E402
import gfx  # noqa: E402
import helpbub  # noqa: E402
import namegrid  # noqa: E402
import romtext  # noqa: E402
import tagfont  # noqa: E402
import text  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "vattroller_x_en.gba"
MARKER_OUT = ROOT / "build" / "vattroller_x_marker.gba"
EVENTS_FREE = 0xBE8000

FILLER = "The quick brown fox jumps over the lazy dog, then naps by the warm fire. "
# Marker length per kind = the measured budget (budgets.json), so markers fill each box variant exactly.
MARKER_CHARS = {k: v["chars"] for k, v in json.loads((ROOT / "budgets.json").read_text(encoding="utf-8"))["kinds"].items()
                if k in ("choice", "title", "credit")}


def enc(s):
    return font.encode(s, text.encode)


def marker_id(rid):
    """Short on-screen form of an id: e2478_00090 -> 78/90, e2478_00090.1 -> 78/90.1, r073cd8 -> 73CD8."""
    if rid[0] == "e":
        f, rest = rid[1:].split("_")
        off, _, k = rest.partition(".")
        return f"{int(f) - 2400}/{int(off, 16):x}" + (f".{k}" if k else "")
    return rid[1:].lstrip("0").upper() or "0"


def marker_text(row, chars=36):
    """Marker for one row: its short id, then filler up to `chars` (event lines) or the original byte length
    (ROM strings: the game may copy them into buffers sized for the Japanese)."""
    m = marker_id(row["id"]) + " "
    if row["kind"] == "line":
        n = chars
    elif row["kind"] in MARKER_CHARS:
        n = MARKER_CHARS[row["kind"]]
    elif row.get("wide"):
        n = row["max"]
    else:   # ROM strings: the Japanese pixel width (6 px per letter), never more bytes than the Japanese
        raw = text.encode(row["jp"])
        n = max(len(m) - 1, min(len(raw), font.jp_px(raw) // 6))
        if "max" in row:
            n = min(n, row["max"])
    return (m + FILLER * 3)[:n].rstrip() if n > len(m) else m[:n]


def english_rows(marker):
    """{rel: [(row, text)]} of every row with English (or every text row, as markers)."""
    out = {}
    for rel, r in text.iter_rows():
        if r["kind"] == "data":
            continue
        s = marker_text(r) if marker else r.get(text.LANG)
        if s and r.get("wide"):
            s = font.widen(s)
        if s:
            out.setdefault(rel, []).append((r, s))
    return out


def build(rom, marker=False, identity=False):
    ar = archive.Archive(rom)
    evs = {i: events.parse(ar.file(i)) for i in range(events.FIRST, events.LAST + 1)}
    rows = {} if identity else english_rows(marker)
    ev_text = {r["id"]: s for rel, rs in rows.items() if rel.startswith("events/") for r, s in rs}
    text.apply_events(evs, enc, ev_text)
    files = {i: ev.build() for i, ev in evs.items()}
    if identity:
        return archive.write_files(rom, files)
    files.update(gfx.files(ar))
    files.update(namegrid.files(ar, rom))
    files.update(helpbub.files(ar))
    out, log = archive.write_files(rom, files, free=EVENTS_FREE)
    helpbub.patch(out, log, rom)
    font.patch(out, log, ar.offset(font.FONT_FILE))
    rom_rows = [x for rel, rs in rows.items() if rel.startswith("rom/") for x in rs]
    romtext.apply(out, log, rom_rows, enc)
    tagfont.patch(out, log)
    namegrid.patch(out, log, rom)
    return out, log


def main():
    check_rom.check()
    rom = archive.ROM.read_bytes()
    marker, identity = "--marker" in sys.argv, "--identity" in sys.argv
    out, log = build(rom, marker=marker, identity=identity)
    dest = MARKER_OUT if marker else OUT
    dest.parent.mkdir(exist_ok=True)
    dest.write_bytes(out)
    dest.with_suffix(".writes.tsv").write_text(
        "".join(f"{a:#x}\t{b:#x}\t{what}\n" for a, b, what in log), encoding="utf-8")
    same = bytes(out) == rom
    print(f"{dest.relative_to(ROOT)}: {len(out):#x} bytes, sha1 {hashlib.sha1(out).hexdigest()}, "
          f"{len(log)} writes, {'identical to' if same else 'differs from'} the original")
    if identity and not same:
        sys.exit(1)
    if not identity:
        import romcheck
        errs = romcheck.verify(rom, out, log)
        for e in errs[:60]:
            print(e)
        print(f"romcheck: {len(errs)} errors (every changed byte logged, no overlaps, writers in their regions)")
        if errs:
            sys.exit(1)


if __name__ == "__main__":
    main()
