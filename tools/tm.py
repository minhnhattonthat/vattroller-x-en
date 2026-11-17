"""Translation memory for batch work: rows whose exact JP already has an English line in script/events.

    python -X utf8 tools/tm.py show bNNN [FROM TO]   rows WITHOUT a TM hit (n form/limit|jp) + hit count
    python -X utf8 tools/tm.py put bNNN miss.txt      miss.txt = English for the missing rows, in order;
                                                      writes work/tl/bNNN.en.txt (TM + miss), then
                                                      tl_pair.py put and batches.py check

Lines holding the player-name code are never taken from memory. Read the filled en.txt around TM hits that
continue a sentence (a TM line is context-free): fix with the edit tool, then tl_pair.py put again.
"""
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def memory():
    m = defaultdict(Counter)
    for f in (REPO / "script/events").glob("*.json"):
        for r in json.loads(f.read_text(encoding="utf-8")):
            if r.get("en") and r.get("jp") and "∴" not in r["jp"]:
                m[r["jp"]][r["en"]] += 1
    return {k: c.most_common(1)[0][0] for k, c in m.items()}


def rows(batch):
    text = (REPO / f"work/tl/{batch}.tsv").read_text(encoding="utf-8")
    return [line.split("\t") for line in text.splitlines() if line]


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    cmd, batch = argv[0], argv[1]
    rs, tm = rows(batch), memory()
    if cmd == "show":
        a = int(argv[2]) if len(argv) > 2 else 1
        z = int(argv[3]) if len(argv) > 3 else len(rs)
        hits = 0
        for n, r in enumerate(rs, 1):
            if r[4] in tm:
                hits += 1
            elif a <= n <= z:
                print(f"{n} {r[2]}/{r[3]}|{r[4]}")
        print(f"[TM hits {hits}, missing {len(rs) - hits}]")
        return 0
    if cmd == "put":
        miss = Path(argv[2]).read_text(encoding="utf-8").splitlines()
        out, i = [], 0
        for r in rs:
            if r[4] in tm:
                out.append(tm[r[4]])
            else:
                out.append(miss[i] if i < len(miss) else "")
                i += 1
        if i != len(miss):
            sys.exit(f"{len(miss)} lines for {i} missing rows")
        p = REPO / f"work/tl/{batch}.en.txt"
        p.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
        py = [sys.executable, "-X", "utf8"]
        subprocess.run(py + ["tools/tl_pair.py", "put", batch, str(p)], cwd=REPO, check=True)
        return subprocess.run(py + ["tools/batches.py", "check", batch], cwd=REPO).returncode
    sys.exit(__doc__)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
