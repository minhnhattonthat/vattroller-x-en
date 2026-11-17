"""romcheck.py: phase-7 write check of a built ROM against the original (run by build.py after every build).

    python -X utf8 tools/romcheck.py [BUILT]     (default build/vattroller_x_en.gba + its .writes.tsv)

1. romdiff: the build's write log becomes romdiff writes (orig/new bytes per logged range), so every changed byte
   must be covered by a logged write and no two writes may overlap (a later write silently clobbering an earlier one).
2. Each write must land where its writer is allowed to write:
   - `file N`      : in place inside file N's original extent, or past EVENTS_FREE (relocated event files);
   - `entry N`     : file N's 8-byte record in the archive table;
   - `font: ...`   : the width table, the known literal-pool words (font.WIDTH_LITS / THRESHOLD_LITS), the pair glyphs;
   - `rXXXXXX`     : the ROM-string area (romtext.STR_START-STR_END);
   - `rXXXXXX ptr` : one of that row's recorded pointer slots (script/rom/*.json `ptrs`), 4 bytes;
   - `cXXXXXX` / noptr ids: in place, inside the record (`max` + terminator) at the row's own offset.
Exit 1 on any error."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import archive  # noqa: E402
import font  # noqa: E402
import helpbub  # noqa: E402
import namegrid  # noqa: E402
import romdiff  # noqa: E402
import romtext  # noqa: E402
import tagfont  # noqa: E402
import text  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BUILT = ROOT / "build" / "vattroller_x_en.gba"
EVENTS_FREE = 0xBE8000
GLYPHS = (0x9ACE44, 0xBE4DC4)


def load_log(path):
    log = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        a, b, what = line.split("\t")
        log.append((int(a, 16), int(b, 16), what))
    return log


def region_errors(orig, log):
    ar = archive.Archive(orig)
    rows = {r["id"]: r for rel, r in text.iter_rows() if rel.startswith("rom/")}
    lits = set(font.WIDTH_LITS) | set(font.THRESHOLD_LITS)
    errs = []
    for a, b, what in log:
        ok = False
        m = re.fullmatch(r"(file|entry) (\d+)", what)
        if m:
            i = int(m.group(2))
            if m.group(1) == "file":
                lo, hi = ar.offset(i), ar.offset(i) + ar.size(i)
                ok = (lo <= a and b <= hi) or a >= EVENTS_FREE
            else:
                lo = archive.TABLE + 8 * i
                ok = lo <= a and b <= lo + 8
        elif what.startswith("tagfont:"):
            ok = (a, b) in tagfont.regions()
        elif what.startswith("namegrid:"):
            ok = (a, b) in namegrid.regions()
        elif what.startswith("helpbub:"):
            ok = (a, b) in helpbub.regions()
        elif what.startswith("font:"):
            ok = ((a, b) == (font.NEW_WIDTHS, font.NEW_WIDTHS + 0x10000) or (a in lits and b == a + 4)
                  or (GLYPHS[0] <= a and b <= GLYPHS[1]))
        else:
            rid, _, tag = what.partition(" ")
            r = rows.get(rid)
            if r is None:
                errs.append(f"{a:#x}-{b:#x} {what}: unknown writer")
                continue
            if tag == "ptr":
                ok = b == a + 4 and a in {int(p, 16) for p in r.get("ptrs", [])}
            elif r["kind"] == "string":
                ok = romtext.STR_START <= a and b <= romtext.STR_END
            elif r["kind"] in ("credit", "noptr"):
                at = int(rid[1:], 16)
                ok = a == at and b <= at + r["max"] + 1
        if not ok:
            errs.append(f"{a:#x}-{b:#x} {what}: outside its allowed region")
    return errs


def verify(orig, new, log):
    """Error lines for a build (empty = clean)."""
    padded = orig + b"\xff" * max(0, len(new) - len(orig))
    writes = [(a, padded[a:b], bytes(new[a:b]), what) for a, b, what in log]
    errs, _ = romdiff.check(orig, bytes(new), set(), writes)
    return errs + region_errors(orig, log)


def main():
    built = Path(sys.argv[1]) if len(sys.argv) > 1 else BUILT
    orig, new = archive.ROM.read_bytes(), built.read_bytes()
    log = load_log(built.with_suffix(".writes.tsv"))
    errs = verify(orig, new, log)
    for e in errs[:60]:
        print(e)
    print(f"romcheck: {len(log)} writes, {len(errs)} errors")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
