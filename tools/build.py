"""build.py: build the patched ROM.

    python -X utf8 tools/build.py              # -> build/vattroller_x_en.gba (+ .writes.tsv for romdiff)
    python -X utf8 tools/build.py --identity   # rebuild with no text changes; exit 1 unless byte-identical

Steps: check the dump against rom.sha1, parse every event file (tools/events.py), apply text (phase 4+), rebuild
each event file through the relocating serializer, and write changed files back through archive.write_files.
With no text changes every file is rebuilt and the ROM must come out identical (tests/test_build.py)."""
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import archive  # noqa: E402
import check_rom  # noqa: E402
import events  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "vattroller_x_en.gba"


def apply_text(evs):
    """Phase 4+: replace text in the parsed event files. Nothing yet: the build is the identity build."""
    return evs


def build(rom):
    ar = archive.Archive(rom)
    evs = {i: events.parse(ar.file(i)) for i in range(events.FIRST, events.LAST + 1)}
    evs = apply_text(evs)
    files = {i: ev.build() for i, ev in evs.items()}
    return archive.write_files(rom, files)


def main():
    check_rom.check()
    rom = archive.ROM.read_bytes()
    out, log = build(rom)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_bytes(out)
    OUT.with_suffix(".writes.tsv").write_text(
        "".join(f"{a:#x}\t{b:#x}\t{what}\n" for a, b, what in log), encoding="utf-8")
    same = bytes(out) == rom
    print(f"{OUT.relative_to(ROOT)}: {len(out):#x} bytes, sha1 {hashlib.sha1(out).hexdigest()}, "
          f"{len(log) // 2} files rewritten, {'identical to' if same else 'differs from'} the original")
    if "--identity" in sys.argv and not same:
        sys.exit(1)


if __name__ == "__main__":
    main()
