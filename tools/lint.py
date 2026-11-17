"""lint.py: width lint for translated text against the measured budgets in budgets.json (phase 5 width gate).

    python -X utf8 tools/lint.py [--all] [--quiet]

Checks every row with English (`en`): px width (ASCII 6 px, other chars 12 px) against its kind's px, wide rows
(fullwidth in game) by character count against `max`, ROM strings and in-place rows by encoded byte length.
--all lints the marker text of every row instead (proves the budgets and the marker build agree).
Errors exit 1; rows whose budget is a guess, or whose kind has none, are warnings."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import font  # noqa: E402
import text  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BUDGETS = ROOT / "budgets.json"


def load_budgets(path=BUDGETS):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def enc(s):
    return font.encode(s, text.encode)


def px(s):
    """Visible width of English text: 6 px per ASCII char, 12 px per other char (2-byte SJIS glyph)."""
    return sum(6 if font.FIRST_CHAR <= ord(c) <= font.LAST_CHAR else 12 for c in s.rstrip(" "))


def jp_px(jp):
    return font.jp_px(text.encode(jp))


def budget(row, b):
    """(kind of limit, limit, source, note) for a row: ('px', n, ..), ('chars', n, ..) or ('bytes', n, ..)."""
    over = b["ids"].get(row["id"])
    if over:
        return over.get("unit", "px"), over["limit"], over.get("source", "measured"), over.get("notes", "")
    if row.get("wide"):
        src = "guess" if "guess" in row.get("notes", "") else b["kinds"]["wide"]["source"]
        return "chars", row["max"], src, "wide row"
    k = b["kinds"].get(row["kind"])
    if k is None:
        return None, None, None, f"no budget for kind {row['kind']}"
    if row["kind"] in ("string", "noptr"):
        n = row["max"] if "max" in row and row["kind"] == "noptr" else len(text.encode(row["jp"]))
        if row["kind"] == "string" and "max" in row:
            n = min(n, row["max"])
        return "bytes", n, k["source"], ""
    return "px", k["px"], k["source"], ""


def check_row(row, s, b):
    """Errors and warnings for English `s` in `row`."""
    errs, warns = [], []
    unit, lim, src, note = budget(row, b)
    if unit is None:
        return errs, [note]
    if "\n" in s:
        errs.append("newline in text: one row is one line")
    if unit == "px":
        w = px(s)
        if w > lim:
            errs.append(f"{w} px > {lim} px ({len(s)} chars, budget {lim // 6})")
        extra = b["kinds"][row["kind"]].get("bytes")
        if extra and len(enc(s)) > extra:
            errs.append(f"{len(enc(s))} bytes > {extra}")
    elif unit == "chars":
        if len(s) > lim:
            errs.append(f"{len(s)} chars > {lim} ({note})")
    else:
        n = len(enc(s))
        if n > lim + lim % 2:                   # the encoder pads to even length; an odd JP length rounds up
            errs.append(f"{n} bytes > {lim} (Japanese byte length: same px)")
        w, jw = px(s), jp_px(row["jp"])
        if w > jw:                              # 8 px JP glyphs (ＶＰ, digits): fewer letters than bytes fit
            errs.append(f"{w} px > {jw} px, the Japanese width ({jw // 6} chars)")
    if src == "guess":
        warns.append(f"budget {lim} {unit} is a guess: measure it before fitting ({note})")
    return errs, warns


def lint(rows, b, marker=False):
    import build
    errs, warns = [], []
    for rel, r in rows:
        if r["kind"] == "data":
            continue
        s = build.marker_text(r) if marker else r.get(text.LANG)
        if not s or (marker and " " not in s):  # a bare id: markers of 2-4 byte strings overflow on purpose
            continue
        e, w = check_row(r, s, b)
        errs += [f"{rel} {r['id']}: {m}  [{s}]" for m in e]
        warns += [f"{rel} {r['id']}: {m}" for m in w]
    return errs, warns


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--all", action="store_true", help="lint the marker text of every row")
    p.add_argument("--quiet", action="store_true", help="print counts only for warnings")
    a = p.parse_args()
    errs, warns = lint(text.iter_rows(), load_budgets(), marker=a.all)
    for m in errs:
        print("ERROR", m)
    if a.quiet:
        print(f"{len(warns)} warnings")
    else:
        for m in warns:
            print("warn ", m)
    print(f"lint: {len(errs)} errors, {len(warns)} warnings")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
