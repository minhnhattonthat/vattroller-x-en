"""Self-contained reviewer prompts for `codex exec` (its Windows sandbox cannot read files) and a coverage gate.

    python -X utf8 tools/review_prompts.py build OUTDIR NAME bNNN [bNNN ...]   write OUTDIR/NAME.prompt
    python -X utf8 tools/review_prompts.py coverage DIR [DIR ...]              every translated id in some prompt?

A prompt = reviewer brief + glossary + translator brief + decisions (+ style reference / synopsis when present)
+ one pairs section per batch (tools/pairs.py format, current EN from script/). `build` refuses to write a prompt
whose pairs sections do not hold exactly the batch's ids, so an empty or cut batch can't slip through again.
`coverage` lists the translated ids (status done) found in no `>> id` row of any *.prompt under the given dirs and
exits 1 if any are missing. Read-only on the repo: writes only OUTDIR.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pairs  # noqa: E402

ROOT = pairs.ROOT
DOCS = ["docs/reviewer-brief.md", "glossary.md", "docs/style-reference.md", "docs/synopsis.md",
        "docs/translator-brief.md", "docs/decisions.md"]
ROW = re.compile(r"^>> (\S+)", re.M)


def batch_ids(batch):
    text = (pairs.TL / f"{batch}.tsv").read_text(encoding="utf-8")
    return [line.split("\t")[0] for line in text.splitlines() if line]


def build(outdir, name, batches):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    index = pairs.entries()
    tmp = outdir / "_pairs"
    tmp.mkdir(exist_ok=True)
    head = ("You are a translation reviewer. You have NO file or shell access: everything you need is below. "
            "Do not try to run commands. Follow the reviewer brief exactly and return the report as your final "
            f"message. Batches: {' '.join(batches)}.\n")
    parts = [head]
    for doc in DOCS:
        p = ROOT / doc
        if p.exists():
            parts.append(f"\n===== {doc} =====\n" + p.read_text(encoding="utf-8"))
    for b in batches:
        pairs.write(b, index, tmp)
        body = (tmp / f"{b}.txt").read_text(encoding="utf-8")
        got, want = ROW.findall(body), batch_ids(b)
        if got != want:
            sys.exit(f"{b}: pairs rows ({len(got)}) != batch ids ({len(want)})")
        parts.append(f"\n===== pairs file {b} ({len(want)} rows) =====\n" + body)
    out = outdir / f"{name}.prompt"
    out.write_text("".join(parts), encoding="utf-8", newline="\n")
    print(f"{out}: {len(batches)} batches, {sum(len(batch_ids(b)) for b in batches)} rows")


def coverage(dirs):
    seen = set()
    for d in dirs:
        for p in Path(d).rglob("*.prompt"):
            seen |= set(ROW.findall(p.read_text(encoding="utf-8")))
    need = [i for i, (_, e) in pairs.entries().items() if e.get("status") == "done"]
    missing = [i for i in need if i not in seen]
    print(f"{len(need)} translated ids, {len(need) - len(missing)} in prompts, {len(missing)} missing")
    for i in missing[:20]:
        print("  missing", i)
    return 1 if missing else 0


def main(argv):
    if len(argv) >= 4 and argv[0] == "build":
        build(argv[1], argv[2], argv[3:])
        return 0
    if len(argv) >= 2 and argv[0] == "coverage":
        return coverage(argv[1:])
    sys.exit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
