"""romctx.py: show ROM strings around given ids with their JP px, EN px and budget (for sibling budgets).

    python -X utf8 tools/romctx.py r00e1d8 r0093e4 [--n 4]

For each id: the rows `--n` before and after it in the same script/rom file, each with
`id  jp_px  en_px/limit(source)  jp | en`. The widest JP px in the neighbourhood is the candidate sibling budget
(same table field); confirm the field is shared before writing a `budgets.json` `ids` entry."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lint  # noqa: E402
import text  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("ids", nargs="+")
    p.add_argument("--n", type=int, default=4)
    a = p.parse_args()
    b = lint.load_budgets()
    rows = [(rel, r) for rel, r in text.iter_rows() if rel.startswith("rom/")]
    pos = {r["id"]: i for i, (_, r) in enumerate(rows)}
    for want in a.ids:
        if want not in pos:
            print(f"{want}: not found")
            continue
        i = pos[want]
        print(f"== {want}")
        for rel, r in rows[max(0, i - a.n): i + a.n + 1]:
            if r["kind"] == "data":
                continue
            jp = lint.jp_px(r["jp"])
            en = r.get(text.LANG) or ""
            unit, lim, src, _ = lint.budget(r, b)
            mark = ">" if r["id"] == want else " "
            print(f"{mark}{r['id']} jp{jp:4d} en{lint.px(en):4d}/{lim}{unit[0] if unit else '?'}({src})  "
                  f"{r['jp']} | {en}")


if __name__ == "__main__":
    main()
