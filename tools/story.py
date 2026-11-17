"""story.py: story-pass chapter files and `codex exec` story reviewers (references/translation.md §Review).

    python -X utf8 tools/story.py chapters                      write work/qa/story/chapters/*.txt
    python -X utf8 tools/story.py review CHAPTER.txt [...] [--jobs 3]
        -> work/qa/story/reports/<stem>.md and work/qa/story/verdicts/<stem>.tsv (`stem<TAB>ok|issue<TAB>note`)

Chapters follow docs/synopsis.md (event file ranges; chapter 7 = ROM strings + credits). Long chapters are cut into
parts of about PART_CHARS characters at event-file boundaries (ROM strings at file/row boundaries), so one reviewer
reads one part whole. Codex's Windows sandbox cannot read files, so each prompt carries the brief, synopsis, style
reference, glossary and the chapter text. Then: `qa_gate.py init work/qa/story/manifest.tsv work/qa/story/chapters
--glob "*.txt"` and `qa_gate.py check work/qa/story/manifest.tsv work/qa/story/verdicts`.
"""
import argparse
import concurrent.futures as cf
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EV = ROOT / "script" / "events"
RS = ROOT / "script" / "rom"
OUT = ROOT / "work" / "qa" / "story"
PART_CHARS = 45000
CHAPTERS = [  # (number, slug, first event file, last event file) from docs/synopsis.md
    (1, "comic", 2475, 2519),
    (2, "club", 2520, 2530),
    (3, "vattleague", 2531, 2549),
    (4, "jin_crossover", 2550, 2562),
    (5, "side_events", 2563, 2602),
    (6, "town", 2603, 2711),
]
DOCS = ["docs/story-reviewer-brief.md", "docs/synopsis.md", "docs/style-reference.md", "glossary.md"]


def entry(r):
    return f">> {r['id']} | {r['jp']}\n   {r['en']}\n"


def parts(blocks):
    """Group (header, text) blocks into parts of about PART_CHARS characters."""
    out, cur = [], ""
    for head, text in blocks:
        block = f"## {head}\n{text}"
        if cur and len(cur) + len(block) > PART_CHARS:
            out.append(cur)
            cur = ""
        cur += block
    if cur:
        out.append(cur)
    return out


def event_blocks(first, last):
    for n in range(first, last + 1):
        p = EV / f"e{n}.json"
        if not p.exists():
            continue
        rows = [r for r in json.loads(p.read_text(encoding="utf-8")) if r.get("en")]
        if rows:
            yield f"e{n}", "".join(entry(r) for r in rows)


def rom_blocks():
    for p in sorted(RS.glob("*.json")):
        rows = [r for r in json.loads(p.read_text(encoding="utf-8")) if r.get("en") and r.get("status") != "data"]
        for i in range(0, len(rows), 400):
            yield f"{p.stem} rows {i}-{i + len(rows[i:i + 400]) - 1}", "".join(entry(r) for r in rows[i:i + 400])


def chapters():
    d = OUT / "chapters"
    d.mkdir(parents=True, exist_ok=True)
    for old in d.glob("*.txt"):
        old.unlink()
    plan = [(n, slug, list(event_blocks(a, b))) for n, slug, a, b in CHAPTERS]
    plan.append((7, "system", list(rom_blocks())))
    for n, slug, blocks in plan:
        ps = parts(blocks)
        for i, text in enumerate(ps, 1):
            name = f"ch{n}_{slug}" + (f"_p{i}" if len(ps) > 1 else "")
            title = f"# Chapter {n} ({slug})" + (f", part {i} of {len(ps)}" if len(ps) > 1 else "")
            (d / f"{name}.txt").write_text(f"{title}\n\n{text}", encoding="utf-8")
            print(f"{name}.txt {len(text)} chars")


def review(path):
    path = Path(path)
    docs = "\n\n".join(f"===== {name} =====\n" + (ROOT / name).read_text(encoding="utf-8") for name in DOCS)
    prompt = (docs + f"\n\n===== chapter file {path.name} =====\n" + path.read_text(encoding="utf-8")
              + "\n\nWrite the report now, as described in the brief. Do not run commands or read files: everything"
              " you need is above. The last line must be the ASSESSMENT line.\n")
    p = subprocess.run(["codex", "exec", "--skip-git-repo-check", "-s", "read-only", "-"], input=prompt,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=3600)
    (OUT / "reports").mkdir(parents=True, exist_ok=True)
    (OUT / "reports" / f"{path.stem}.md").write_text(p.stdout, encoding="utf-8")
    lines = [ln for ln in p.stdout.splitlines() if ln.strip().strip("`").startswith("ASSESSMENT")]
    if not lines:
        return path.stem, None, (p.stdout[-200:] + p.stderr[-300:]).replace("\n", " ")
    parts_ = re.split(r"\t+|\s{2,}", lines[-1].strip().strip("`"), maxsplit=2)
    if len(parts_) < 3 or parts_[1] not in ("ok", "issue"):
        return path.stem, None, lines[-1]
    return path.stem, parts_[1], parts_[2].replace("\t", " ")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["chapters", "review"])
    ap.add_argument("files", nargs="*")
    ap.add_argument("--jobs", type=int, default=3)
    a = ap.parse_args()
    if a.cmd == "chapters":
        return chapters()
    (OUT / "verdicts").mkdir(parents=True, exist_ok=True)
    bad = 0
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        for stem, verdict, note in ex.map(review, a.files):
            if verdict is None:
                bad += 1
                print(f"{stem}: NO VERDICT {note}")
                continue
            (OUT / "verdicts" / f"{stem}.tsv").write_text(f"{stem}\t{verdict}\t{note}\n", encoding="utf-8")
            print(f"{stem}\t{verdict}\t{note}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
