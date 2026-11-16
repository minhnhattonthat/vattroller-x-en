"""stress_build.py: relayout check ROM. Every text line gets a trailing fullwidth space, so nearly every event file
grows, is relaid by tools/events.py and moves past 8 MiB. Warp into scenes on it to check links survive in game:

    python -X utf8 tools/stress_build.py                       # -> work/stress.gba
    python -X utf8 tools/debug/warp.py rpg_start rpg_tutorial battle_tutorial --rom work/stress.gba --out work/qa/stress
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import archive  # noqa: E402
import events  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    rom = archive.ROM.read_bytes()
    ar = archive.Archive(rom)
    files = {}
    for i in range(events.FIRST, events.LAST + 1):
        ev = events.parse(ar.file(i))
        for _, n in ev.text_nodes():
            n.set_text(n.text + b"\x81\x40")
        files[i] = ev.build()
    out, _ = archive.write_files(rom, files)
    new = archive.Archive(bytes(out))
    moved = sum(1 for i in files if new.offset(i) >= archive.FREE_START)
    dest = ROOT / "work" / "stress.gba"
    dest.parent.mkdir(exist_ok=True)
    dest.write_bytes(out)
    print(f"{dest.relative_to(ROOT)}: {len(out):#x} bytes, {moved} of {len(files)} event files moved")
