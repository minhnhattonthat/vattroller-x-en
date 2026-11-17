"""Compact view of a translation batch, and the English back by row order (saves writing every id).

    python -X utf8 tools/tl_pair.py show bNNN [FROM [TO]]   rows as  n form/limit | JP  (1-based)
    python -X utf8 tools/tl_pair.py put bNNN EN.txt          EN.txt: one English row per batch row, in order
                                                              -> work/tl/bNNN.out.tsv
"""
import sys
from pathlib import Path

TL = Path(__file__).resolve().parents[1] / "work/tl"


def rows(batch):
    return [line.split("\t") for line in (TL / f"{batch}.tsv").read_text(encoding="utf-8").splitlines() if line]


def main(argv):
    cmd, batch = argv[0], argv[1]
    rs = rows(batch)
    if cmd == "show":
        a = int(argv[2]) if len(argv) > 2 else 1
        b = int(argv[3]) if len(argv) > 3 else len(rs)
        prev = None
        for n, r in enumerate(rs[a - 1:b], a):
            f = r[0].split("_")[0]
            if f != prev:
                print(f"## {f}")
                prev = f
            print(f"{n} {r[2]}/{r[3]}|{r[4]}")
        return 0
    if cmd == "put":
        en = Path(argv[2]).read_text(encoding="utf-8").splitlines()
        if len(en) != len(rs):
            sys.exit(f"{len(en)} English rows for {len(rs)} batch rows")
        out = "".join(f"{r[0]}\t{e}\n" for r, e in zip(rs, en))
        (TL / f"{batch}.out.tsv").write_text(out, encoding="utf-8", newline="\n")
        print(f"wrote {len(rs)} rows")
        return 0
    sys.exit(__doc__)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
