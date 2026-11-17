"""Fix batch for reviewer findings: the listed ids, each widened to its whole dialogue box, current EN pre-filled.

    python -X utf8 tools/fixbatch.py NAME ID [ID ...]   -> work/tl/NAME.tsv + NAME.out.tsv (current English)
    python -X utf8 tools/fixbatch.py NAME --file IDS.txt (one id per line; text after the id is ignored)

Edit NAME.out.tsv with the file-edit tool, then
    python -X utf8 tools/batches.py check NAME && python -X utf8 tools/batches.py merge NAME --overwrite
Only work/tl/NAME.* is written; NAME must not look like a translation batch (bNNN).
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import batches  # noqa: E402

TL = batches.TL


def boxes(ids, entries):
    order = list(entries)
    pos = {i: n for n, i in enumerate(order)}
    out = []
    for i in ids:
        if i not in pos:
            sys.exit(f"unknown id {i}")
        n = pos[i]
        e = entries[i]
        if e.get("kind") == "line":
            stem = i.split("_")[0]
            while n > 0 and entries[order[n]].get("flags") not in ("0x0000", "0x0400") \
                    and entries[order[n - 1]].get("kind") == "line" and order[n - 1].split("_")[0] == stem:
                n -= 1
            out.append(order[n])
            m = n + 1
            while m < len(order) and entries[order[m]].get("kind") == "line" and order[m].split("_")[0] == stem \
                    and entries[order[m]].get("flags") not in ("0x0000", "0x0400"):
                out.append(order[m])
                m += 1
        else:
            out.append(i)
    seen, uniq = set(), []
    for i in out:
        if i not in seen:
            seen.add(i)
            uniq.append(i)
    return sorted(uniq, key=pos.get)


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    name = argv[0]
    if re.fullmatch(r"b\d{3}", name):
        sys.exit("pick a name that is not bNNN")
    if argv[1] == "--file":
        ids = [line.split()[0] for line in Path(argv[2]).read_text(encoding="utf-8").splitlines() if line.strip()]
    else:
        ids = argv[1:]
    entries = batches.index()
    rows = boxes(ids, entries)
    tsv = [f"{i}\t{entries[i].get('speaker', '')}\t{batches.form_of(entries[i])}\t{batches.limit_label(entries[i])}"
           f"\t{entries[i]['jp']}" for i in rows]
    (TL / f"{name}.tsv").write_text("\n".join(tsv) + "\n", encoding="utf-8", newline="\n")
    (TL / f"{name}.out.tsv").write_text("".join(f"{i}\t{entries[i].get('en', '')}\n" for i in rows),
                                        encoding="utf-8", newline="\n")
    for i in rows:
        print(f"{i}\t{batches.form_of(entries[i])}\t{entries[i]['jp']}")
    print(f"{len(rows)} rows -> work/tl/{name}.out.tsv")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
