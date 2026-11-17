"""textsweep.py: draw every event line, choice and chapter title once in the emulator (text-coverage gate).

    python -X utf8 tools/textsweep.py [--jobs 3] [--chunks 6] [--out work/qa/cover/sweep] [--shots]
    python -X utf8 $SKILL/scripts/textcover.py work/qa/cover build/strings.tsv --mask 0x1FFFFFF --waive docs/text_unshown.tsv

Writes build/strings.tsv and the node list (tools/strings_tsv.py), splits the list at event-file boundaries into
--chunks lists, and runs each from the comic_jin1 state (work/states/comic_jin1.mss, `warp.py comic_jin1 --state`)
with tools/lua/textsweep.lua (redirects the interpreter through the box commands) and the skill's textcover.lua
probe (ROM reads). Each chunk: OUT/chunk_NN/log.txt. Prints per-chunk progress and every SWEEP STALL.
--shots keeps one shot per command (n#####.png) for spot checks.
"""
import argparse
import hashlib
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from skill import SKILL  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build" / "vattroller_x_en.gba"
STATE = ROOT / "work" / "states" / "comic_jin1.mss"
PER_CMD = 45  # frames budget per command (measured ~25)


def split(nodes, n):
    """Chunks of about len/n lines, cut only where the event file changes."""
    size = -(-len(nodes) // n)
    out, cur = [], []
    for k, (addr, f) in enumerate(nodes):
        if len(cur) >= size and f != nodes[k - 1][1]:
            out.append(cur)
            cur = []
        cur.append((addr, f))
    if cur:
        out.append(cur)
    return out


def run(chunk_dir, lst, shots):
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(BUILD),
           "--out", str(chunk_dir), "--state-in", str(STATE), "--mash", "8",
           "--frames", str(len(lst) * PER_CMD + 3000), "--timeout", "3600",
           "--script", str(ROOT / "tools" / "lua" / "textsweep.lua"),
           "--var", f"LIST='{(chunk_dir / 'nodes.txt').as_posix()}'",
           "--script", str(Path(SKILL) / "scripts" / "lua" / "probes" / "textcover.lua"),
           "--var", "RANGES='8000000-91CBFC0'"]
    if shots:
        cmd += ["--var", "SHOT=1"]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log = (chunk_dir / "log.txt").read_text(encoding="utf-8", errors="replace") if (chunk_dir / "log.txt").exists() else ""
    done = "SWEEP DONE" in log
    taken = sum(1 for l in log.splitlines() if l.startswith("SWEEP ") and l.split()[1].isdigit())
    stalls = [l for l in log.splitlines() if l.startswith("SWEEP STALL")]
    return chunk_dir.name, r.returncode, done, taken, len(lst), stalls


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--chunks", type=int, default=6)
    ap.add_argument("--out", default=str(ROOT / "work" / "qa" / "cover" / "sweep"))
    ap.add_argument("--shots", action="store_true")
    ap.add_argument("--only", type=int, nargs="*", help="run only these chunk numbers (others keep their logs)")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    stamp = hashlib.sha1(BUILD.read_bytes()).hexdigest() + "\n"  # per chunk run: tools/cover.py maps logs by it
    nodes_file = out / "nodes_all.txt"
    subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools" / "strings_tsv.py"), "--nodes", str(nodes_file)],
                   check=True)
    nodes = [(l.split("\t")[0], l.split("\t")[1]) for l in nodes_file.read_text(encoding="utf-8").splitlines()]
    jobs = []
    for k, ch in enumerate(split(nodes, a.chunks)):
        d = out / f"chunk_{k:02d}"
        d.mkdir(exist_ok=True)
        (d / "nodes.txt").write_text("".join(f"{addr}\n" for addr, _ in ch), encoding="utf-8")
        if a.only is None or k in a.only:
            (d / "build.sha1").write_text(stamp, encoding="utf-8")
            jobs.append((d, ch))
    with ThreadPoolExecutor(a.jobs) as ex:
        for name, rc, done, taken, total, stalls in ex.map(lambda j: run(j[0], j[1], a.shots), jobs):
            print(f"{name}: exit {rc}, {taken}/{total} commands, {'done' if done else 'NOT DONE'}, "
                  f"{len(stalls)} stalls")
            for s in stalls[:20]:
                print("   ", s)


if __name__ == "__main__":
    main()
