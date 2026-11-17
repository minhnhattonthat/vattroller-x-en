"""Reviewer pairs files: JP and current EN of each batch, in game order, grouped by script.

    python -X utf8 tools/pairs.py OUTDIR [bNNN ...]     one OUTDIR/bNNN.txt per batch (default: all in work/tl)

Format: '## <file> script <n>' headers, then per entry
    >> <id> [kind] | <JP>
       <EN>
Read-only: reads script/ and work/tl/bNNN.tsv, writes only OUTDIR.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TL = ROOT / "work/tl"


def entries():
    out = {}
    for path in sorted((ROOT / "script").rglob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        rows = data if isinstance(data, list) else data.get("entries", [])
        for e in rows:
            if isinstance(e, dict) and "id" in e:
                out[e["id"]] = (path.stem, e)
    return out


def write(batch, index, outdir):
    ids = [line.split("\t")[0] for line in (TL / f"{batch}.tsv").read_text(encoding="utf-8").splitlines() if line]
    lines, prev = [], None
    for i in ids:
        stem, e = index[i]
        group = (stem, e.get("script"))
        if group != prev:
            lines.append(f"\n## {stem}" + (f" script {e['script']}" if e.get("script") is not None else ""))
            prev = group
        kind = e.get("kind", "")
        tag = "" if kind == "line" else f" [{kind}]"
        note = f"   (note: {e['notes']})" if e.get("notes") else ""
        lines.append(f">> {i}{tag} | {e['jp']}{note}")
        lines.append(f"   {e.get('en', '')}")
    (outdir / f"{batch}.txt").write_text("\n".join(lines).lstrip() + "\n", encoding="utf-8", newline="\n")


def main(argv):
    if not argv:
        sys.exit(__doc__)
    outdir = Path(argv[0])
    outdir.mkdir(parents=True, exist_ok=True)
    batches = argv[1:] or sorted(p.name[:-4] for p in TL.glob("b[0-9][0-9][0-9].tsv"))
    index = entries()
    for b in batches:
        write(b, index, outdir)
    print(f"wrote {len(batches)} pairs files to {outdir}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
