"""polish_view.py: one reading sheet for the polish pass: each unticked docs/polish.md line with its fix-batch box.

    python -X utf8 tools/fixbatch.py NAME --file IDS.txt      (ids of the unticked lines)
    python -X utf8 tools/polish_view.py NAME > work/tl/NAME_view.txt

Prints, per unticked line in polish.md order: `## id` + the note, then the rows of the box that holds it
(`row-id | limit | JP | current EN`, from work/tl/NAME.tsv and NAME.out.tsv). Boxes already shown are printed once.
Read-only.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main(name):
    tl = ROOT / "work" / "tl"
    src = [ln.split("\t") for ln in (tl / f"{name}.tsv").read_text(encoding="utf-8").splitlines() if ln]
    en = dict(ln.split("\t", 1) for ln in (tl / f"{name}.out.tsv").read_text(encoding="utf-8").splitlines() if ln)
    boxes, cur = [], []
    for row in src:
        if row[2] != "+" and cur:
            boxes.append(cur)
            cur = []
        cur.append(row)
    if cur:
        boxes.append(cur)
    where = {row[0]: n for n, b in enumerate(boxes) for row in b}
    shown = set()
    for ln in (ROOT / "docs" / "polish.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"- \[ \] (\S+) - (.*)", ln)
        if not m:
            continue
        i, note = m.groups()
        print(f"## {i} - {note}")
        n = where.get(i)
        if n is None:
            print("   (not in batch)")
        elif n in shown:
            print("   (box above)")
        else:
            shown.add(n)
            for row in boxes[n]:
                print(f"   {row[0]} |{row[3]}| {row[4]} | {en.get(row[0], '')}")
        print()


if __name__ == "__main__":
    main(sys.argv[1])
