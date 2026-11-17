"""polish_apply.py: apply polish-pass decisions to a fix batch and tick docs/polish.md.

    python -X utf8 tools/polish_apply.py NAME [--tick]

Reads work/tl/NAME_dec.txt, one decision per line, `id || new English` or `id || WAIVE: reason` (the last line for
an id wins). Sets the English of each fixed id in work/tl/NAME.out.tsv (the fix batch from tools/fixbatch.py; any
row of a fixed box may be changed). With --tick, also ticks every unticked docs/polish.md line whose id has a
decision: `[x] ... (fixed: polish pass)` or `[x] ... (waived: reason)`. Then run
`batches.py check NAME && batches.py merge NAME --overwrite`.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main(argv):
    name, tick = argv[0], "--tick" in argv
    tl = ROOT / "work" / "tl"
    dec = {}
    for ln in (tl / f"{name}_dec.txt").read_text(encoding="utf-8").splitlines():
        if " || " in ln:
            i, v = ln.split(" || ", 1)
            dec[i.strip()] = v
    out = tl / f"{name}.out.tsv"
    rows = [ln.split("\t", 1) for ln in out.read_text(encoding="utf-8").splitlines() if ln]
    have = {r[0] for r in rows}
    missing = [i for i, v in dec.items() if not v.startswith("WAIVE:") and i not in have]
    if missing:
        sys.exit(f"not in {out.name}: {' '.join(missing)}")
    n = 0
    for r in rows:
        v = dec.get(r[0])
        if v is not None and not v.startswith("WAIVE:") and r[1] != v:
            r[1] = v
            n += 1
    out.write_text("".join(f"{a}\t{b}\n" for a, b in rows), encoding="utf-8")
    print(f"{n} rows changed in {out.name}")
    if not tick:
        return
    pol = ROOT / "docs" / "polish.md"
    lines = pol.read_text(encoding="utf-8").splitlines()
    t = 0
    for k, ln in enumerate(lines):
        m = re.match(r"- \[ \] (\S+) (.*)", ln)
        if m and m.group(1) in dec:
            v = dec[m.group(1)]
            note = f"(waived: {v[6:].strip()})" if v.startswith("WAIVE:") else "(fixed: polish pass)"
            lines[k] = f"- [x] {m.group(1)} {m.group(2)} {note}"
            t += 1
    pol.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{t} polish lines ticked")


if __name__ == "__main__":
    main(sys.argv[1:])
