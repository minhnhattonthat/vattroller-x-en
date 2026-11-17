"""exp_build.py: marker build with per-kind overrides, for width experiments (phase 5 width gate).

    python -X utf8 tools/exp_build.py OUT.gba [--kind KIND=CHARS].. [--id ID=TEXT].. [--orig KIND]..

--kind credit=20     marker rows of that kind are cut to CHARS characters
--id c074570=ABC     one row gets exactly TEXT (ASCII; use \\n nowhere)
--orig credit        rows of that kind keep their Japanese (not written)
--fill credit=TEXT   every row of that kind gets TEXT
Everything else is the normal marker build (tools/build.py --marker)."""
import argparse
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import archive  # noqa: E402
import build  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("out")
    p.add_argument("--kind", action="append", default=[])
    p.add_argument("--id", action="append", default=[])
    p.add_argument("--orig", action="append", default=[])
    p.add_argument("--fill", action="append", default=[], help="KIND=TEXT: every row of KIND gets TEXT")
    a = p.parse_args()
    cut = {k: int(v) for k, v in (x.split("=", 1) for x in a.kind)}
    fill = dict(x.split("=", 1) for x in a.fill)
    fixed = dict(x.split("=", 1) for x in a.id)
    base = build.marker_text

    def marker_text(row, chars=36):
        if row["id"] in fixed:
            return fixed[row["id"]]
        if row["kind"] in fill:
            return fill[row["kind"]]
        s = base(row, chars)
        return s[:cut[row["kind"]]].rstrip() if row["kind"] in cut else s

    build.marker_text = marker_text
    orig_rows = build.english_rows

    def english_rows(marker):
        return {rel: [(r, s) for r, s in rs if r["kind"] not in a.orig]
                for rel, rs in orig_rows(marker).items()}

    build.english_rows = english_rows
    out, log = build.build(archive.ROM.read_bytes(), marker=True)
    Path(a.out).write_bytes(out)
    print(f"{a.out}: sha1 {hashlib.sha1(out).hexdigest()}, {len(log)} writes")


if __name__ == "__main__":
    main()
