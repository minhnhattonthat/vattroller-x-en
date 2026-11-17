"""strings_tsv.py: build/strings.tsv for the text-coverage gate ($SKILL/scripts/textcover.py).

    python -X utf8 tools/strings_tsv.py [--rom build/vattroller_x_en.gba] [--out build/strings.tsv]

One "id<TAB>hex ROM offset" line per shown text row (kind != data): the offset the game reads the string's first
byte from in the BUILT ROM, so it follows the relocated event files and repointed ROM strings.
- event lines / choices / titles: the built event file is parsed again and walked in step with the original
  (same scripts, same nodes; only lengths and positions change), so each id lands on its new text offset;
- ROM strings: the build's write log entry `rXXXXXX` (repointed), else the original offset (kept in place);
- credits (c) and no-pointer strings (n): in place.
Probe with `$SKILL/scripts/lua/probes/textcover.lua --var "RANGES='8000000-91CBFC0'"` and report with
`textcover.py LOGDIR build/strings.tsv --mask 0x1FFFFFF` (the mask turns a CPU address into a ROM offset).
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import archive  # noqa: E402
import events  # noqa: E402
import text  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def event_offsets(orig, built):
    """{id: built ROM offset} for every event text node and choice/title field."""
    a, b = archive.Archive(orig), archive.Archive(built)
    out = {}
    for i in range(events.FIRST, events.LAST + 1):
        e0, e1 = events.parse(a.file(i)), events.parse(b.file(i))
        base_off = b.offset(i)
        s0, s1 = list(e0.scripts()), list(e1.scripts())
        assert len(s0) == len(s1), f"file {i}: script count differs"
        for sa, sb in zip(s0, s1):
            assert len(sa.nodes) == len(sb.nodes), f"file {i}: node count differs"
            for na, nb in zip(sa.nodes, sb.nodes):
                if len(na.data) < 8:
                    continue
                rid = f"e{i}_{sa.node_pos(na):05x}"
                at = base_off + sb.node_pos(nb)
                if na.op == events.OP_TEXT:
                    out[rid] = at + 8
                elif na.op in events.FIELD_OPS:
                    for k, o in enumerate(nb.field_offsets()):
                        out[f"{rid}.{k}"] = at + o
    return out


SWEEP_OPS = (0x0A, events.OP_TEXT, 0x0B) + tuple(events.FIELD_OPS)  # box open, text, box close, choice/title


def sweep_nodes(built):
    """[(file, CPU address)] of every box command (open 0x0A, text, close 0x0B, choice, title) in script order,
    for tools/lua/textsweep.lua. Scripts with no text are skipped."""
    b = archive.Archive(built)
    out = []
    for i in range(events.FIRST, events.LAST + 1):
        base_off = b.offset(i)
        for sc in events.parse(b.file(i)).scripts():
            ns = [n for n in sc.nodes if len(n.data) >= 4 and n.op in SWEEP_OPS]
            if any(n.op != 0x0A and n.op != 0x0B for n in ns):
                out += [(i, 0x08000000 + base_off + sc.node_pos(n)) for n in ns]
    return out


def rom_offsets(log_path):
    """{id: offset} of repointed ROM strings from the build's write log."""
    out = {}
    for line in Path(log_path).read_text(encoding="utf-8").splitlines():
        a, _, what = line.split("\t")
        if what[:1] == "r" and " " not in what:
            out[what] = int(a, 16)
    return out


def rows(orig, built, log_path):
    ev = event_offsets(orig, built)
    rs = rom_offsets(log_path)
    for rel, r in text.iter_rows():
        if r["kind"] == "data":
            continue
        rid = r["id"]
        if rel.startswith("events/"):
            if rid in ev:
                yield rid, ev[rid]
        elif rid in rs:
            yield rid, rs[rid]
        elif rid[:1] in "rcn":
            yield rid, int(rid[1:], 16)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rom", default=str(ROOT / "build" / "vattroller_x_en.gba"))
    ap.add_argument("--out", default=str(ROOT / "build" / "strings.tsv"))
    ap.add_argument("--nodes", help="also write the textsweep node list (file<TAB>hex CPU address) here")
    args = ap.parse_args()
    built = Path(args.rom).read_bytes()
    if args.nodes:
        ns = sweep_nodes(built)
        Path(args.nodes).write_text("".join(f"{a:X}\t{i}\n" for i, a in ns), encoding="utf-8")
        print(f"{args.nodes}: {len(ns)} box commands")
    orig = archive.ROM.read_bytes()
    lines = [f"{rid}\t{off:X}\n" for rid, off in rows(orig, built, Path(args.rom).with_suffix(".writes.tsv"))]
    Path(args.out).write_text("".join(lines), encoding="utf-8")
    print(f"{args.out}: {len(lines)} strings")


if __name__ == "__main__":
    main()
