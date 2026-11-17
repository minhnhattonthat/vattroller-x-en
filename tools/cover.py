"""cover.py: text coverage across builds. Maps every textcover log to the build it ran on, then to string ids.

    python -X utf8 tools/cover.py [ROOT..] [--out work/qa/cover_now]
    python -X utf8 $SKILL/scripts/textcover.py work/qa/cover_now build/strings.tsv --mask 0x1FFFFFF --waive docs/text_unshown.tsv

Why: the probe logs ROM addresses, and any English length change moves every repointed string and event file
after it, so a log from an older build names the wrong strings in build/strings.tsv. Here each log is matched to
its own build's layout and read as ids, so probe passes from earlier builds still count after a text edit.

- Layouts: work/layouts/<rom sha1>.tsv (+ .gba), one per build. The current build's is added on every run
  (tools/strings_tsv.py). Older ones: build the commit in a scratch worktree and add its strings.tsv and ROM
  (git history keeps them reproducible: the rebuilt sha1s match the ones in docs/status.md).
- Which build a log ran on: a `build.sha1` file next to log.txt or in a parent dir wins; else every layout
  ROM is scored by the read runs at or past 0x800000 (relocated text): a run the renderer made ends on the
  string's NUL in the right ROM. Best score wins; layouts tied on the score count only for ids they agree on.
- ROOTs (default work/qa/cover): searched for log.txt. OUT/log.txt gets one "TEXT <addr> f0" line per id shown,
  at its address in the CURRENT build, so the skill's textcover.py reads it unchanged. OUT/logs.tsv lists each
  log with its layout, score and id count; a score under 0.7 is flagged LOW (a build no layout covers; the right
  layout scores 0.8-1.0 and a wrong one 0.2-0.6 on the logs checked 2026-11-17).
"""
import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build" / "vattroller_x_en.gba"
LAYOUTS = ROOT / "work" / "layouts"
MASK = 0x1FFFFFF
RELOC = 0x800000


def sha1(path):
    return hashlib.sha1(Path(path).read_bytes()).hexdigest()


def save_current():
    """Make sure the current build has a layout; return its sha1."""
    LAYOUTS.mkdir(parents=True, exist_ok=True)
    s = sha1(BUILD)
    tsv, gba = LAYOUTS / f"{s}.tsv", LAYOUTS / f"{s}.gba"
    if not tsv.exists():
        subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools" / "strings_tsv.py"), "--rom", str(BUILD),
                        "--out", str(tsv)], check=True, cwd=ROOT)
    if not gba.exists():
        gba.write_bytes(BUILD.read_bytes())
    return s


def load_layout(s):
    ids = {}
    for line in (LAYOUTS / f"{s}.tsv").read_text(encoding="utf-8").splitlines():
        if line.strip():
            i, a = line.split("\t")[:2]
            ids[i] = int(a, 16) & MASK
    return ids


def read_log(path):
    addrs = set()
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("TEXT "):
                addrs.add(int(line.split()[1], 16) & MASK)
    return addrs


def runs_past(addrs, lo=RELOC):
    """Last halfword of each maximal run of read halfwords at or past lo (the text loop reads halfwords and
    stops on the one holding the NUL; repointed strings are 4-aligned with 0xFF fill, so runs split)."""
    xs = sorted({a & ~1 for a in addrs if a >= lo})
    ends = []
    for k, a in enumerate(xs):
        if k + 1 == len(xs) or xs[k + 1] != a + 2:
            ends.append(a)
    return ends


def score(ends, rom, span):
    """Share of runs inside the repointed-string block whose last halfword holds a NUL in this ROM."""
    lo, hi = span
    ends = [e for e in ends if lo <= e <= hi]
    if not ends:
        return None
    return sum(1 for e in ends if 0 in rom[e:e + 2]) / len(ends)


def string_span(ids):
    """The block the build repoints ROM strings into (r ids past RELOC)."""
    xs = [a for i, a in ids.items() if i.startswith("r") and a >= RELOC]
    return (min(xs), max(xs) + 256) if xs else (0, -1)


def stamp_for(log, top):
    d = log.parent
    while True:
        f = d / "build.sha1"
        if f.exists():
            return f.read_text(encoding="utf-8").split()[0].lower()
        if d == top or d.parent == d:
            return None
        d = d.parent


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("roots", nargs="*", default=[str(ROOT / "work" / "qa" / "cover")])
    ap.add_argument("--out", default=str(ROOT / "work" / "qa" / "cover_now"))
    args = ap.parse_args()

    cur = save_current()
    shas = sorted(p.stem for p in LAYOUTS.glob("*.tsv") if (LAYOUTS / f"{p.stem}.gba").exists())
    layouts = {s: load_layout(s) for s in shas}
    roms = {s: (LAYOUTS / f"{s}.gba").read_bytes() for s in shas}
    spans = {s: string_span(ids) for s, ids in layouts.items()}
    by_addr = {s: {} for s in shas}
    for s, ids in layouts.items():
        for i, a in ids.items():
            by_addr[s].setdefault(a, []).append(i)

    shown, report, flagged = set(), [], 0
    for top in (Path(r).resolve() for r in args.roots):
        for log in sorted(top.rglob("log.txt")):
            addrs = read_log(log)
            st = stamp_for(log, top)
            if st and st in layouts:
                best, sc = [st], 1.0
            else:
                ends = runs_past(addrs)
                scores = {s: score(ends, roms[s], spans[s]) for s in shas}
                if all(v is None for v in scores.values()):
                    best, sc = list(shas), None  # nothing relocated read: in-place ids agree everywhere
                else:
                    sc = max(v for v in scores.values() if v is not None)
                    best = [s for s in shas if scores[s] == sc]
            sets = [{i for a in addrs for i in by_addr[s].get(a, ())} for s in best]
            got = set.intersection(*sets)
            shown |= got
            low = sc is not None and sc < 0.7
            flagged += low
            report.append(f"{log.relative_to(ROOT)}\t{best[0][:8] if len(best) == 1 else '%d tied' % len(best)}"
                          f"\t{'-' if sc is None else '%.3f' % sc}\t{len(got)}{'\tLOW' if low else ''}")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    cur_ids = layouts[cur]
    lines = sorted(f"TEXT {0x8000000 + cur_ids[i]:X} f0" for i in shown if i in cur_ids)
    (out / "log.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out / "logs.tsv").write_text("log\tlayout\tscore\tids\n" + "\n".join(report) + "\n", encoding="utf-8")
    print(f"{len(report)} logs, {flagged} with a low layout score; {len(shown & cur_ids.keys())}/{len(cur_ids)} ids "
          f"shown on the current build {cur[:8]} -> {out / 'log.txt'}")


if __name__ == "__main__":
    main()
