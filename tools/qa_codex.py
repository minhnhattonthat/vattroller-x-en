"""qa_codex.py: visual-QA verdicts from independent `codex exec` reviewers (Orca forbids nested subagents).

    python -X utf8 tools/qa_codex.py work/qa/chunks/chunk_001.txt work/qa/verdicts/chunk_001.tsv [--jobs 4]

Each sheet in the chunk file (one path per line, from `qa_gate.py todo --out-dir`) is sent alone to
`codex exec -s read-only -i SHEET` with docs/visual-qa-brief.md; the sheets are EN | JP pairs (left English build,
right original), so the reviewer can tell the game's own behaviour from a translation bug. The reviewer answers one
line `VERDICT<TAB>ok|issue<TAB>note`; it is written as `id<TAB>verdict<TAB>note` (id = path relative to the tour dir
without extension, as qa_gate uses). Sheets whose reviewer gave no parseable line are listed and left out.
"""
import argparse
import concurrent.futures as cf
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIEF = ROOT / "docs" / "visual-qa-brief.md"

PROMPT = """{brief}

---
You are the read-only visual-QA reviewer for ONE contact sheet, attached as an image. Do not run commands or
read files; judge only from the image. Each tile pairs a frame of the English build (LEFT half) with the frame of
the original Japanese ROM at the same frame number (RIGHT half). Timing can drift a little between the two, so the
right half is context only: judge the LEFT (English) half. Japanese on the right is expected.
Sheet id: {sid}

Look at every English tile for the issues listed under "Judge". Graphics text (title logos, chapter cards,
pictures with Japanese lettering, the kana name-entry grid) still in Japanese counts as an issue: name it.
Answer with exactly one final line, tab-separated, nothing after it:
VERDICT<TAB>ok<TAB><one-sentence note>
or
VERDICT<TAB>issue<TAB><which tile (row, column), which text, what is wrong; several issues separated by ' | '>
"""


def review(sheet, sid, brief):
    prompt = PROMPT.format(brief=brief, sid=sid)
    p = subprocess.run(["codex", "exec", "--skip-git-repo-check", "-s", "read-only", "-i", str(sheet), "-"],
                       input=prompt, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=900)
    lines = [ln for ln in p.stdout.splitlines() if ln.startswith("VERDICT")]
    if not lines:
        return sid, None, (p.stdout[-300:] + p.stderr[-300:]).replace("\n", " ")
    parts = re.split(r"\t+|\s{2,}", lines[-1].strip(), maxsplit=2)
    if len(parts) < 3 or parts[1] not in ("ok", "issue"):
        return sid, None, lines[-1]
    return sid, parts[1], parts[2].replace("\t", " ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("chunk")
    ap.add_argument("out")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--root", default="work/qa/tour_sheets", help="tour dir the ids are relative to")
    a = ap.parse_args()
    brief = BRIEF.read_text(encoding="utf-8")
    root = (ROOT / a.root).resolve()
    sheets = []
    for line in Path(a.chunk).read_text(encoding="utf-8").splitlines():
        path = line.split("\t")[-1].strip()
        if path:
            p = (ROOT / path).resolve()
            sheets.append((p, p.relative_to(root).with_suffix("").as_posix()))
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out.exists():  # resume: a killed run keeps the verdicts it already wrote
        done = {ln.split("\t")[0] for ln in out.read_text(encoding="utf-8").splitlines() if ln.strip()}
    sheets = [s for s in sheets if s[1] not in done]
    rows, bad = [], []
    with cf.ThreadPoolExecutor(a.jobs) as ex, out.open("a", encoding="utf-8") as f:
        for sid, verdict, note in ex.map(lambda s: review(s[0], s[1], brief), sheets):
            (rows if verdict else bad).append((sid, verdict, note))
            print(f"{sid}\t{verdict}\t{note}", flush=True)
            if verdict:
                f.write(f"{sid}\t{verdict}\t{note}\n")
                f.flush()
    print(f"{len(rows)} verdicts ({sum(v == 'issue' for _, v, _ in rows)} issue), {len(bad)} unparsed", file=sys.stderr)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
