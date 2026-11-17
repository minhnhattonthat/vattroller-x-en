"""Width lint against the measured budgets (budgets.json, phase 5 width gate)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import lint  # noqa: E402
import text  # noqa: E402

B = lint.load_budgets()
ROWS = {r["id"]: r for _, r in text.iter_rows()}


def errs(rid, s):
    return lint.check_row(ROWS[rid], s, B)[0]


def kind_row(kind):
    return next(r for r in ROWS.values() if r["kind"] == kind)


def test_every_text_kind_has_a_budget():
    kinds = {r["kind"] for r in ROWS.values()} - {"data"}
    assert kinds <= set(B["kinds"]), kinds - set(B["kinds"])


def test_dialogue_line_is_36_chars():
    r = kind_row("line")
    assert not lint.check_row(r, "x" * 36, B)[0]
    assert lint.check_row(r, "x" * 37, B)[0]
    assert lint.check_row(r, "x" * 35 + "…", B)[0]          # a 2-byte char is 12 px


def test_choice_title_credit_budgets():
    for kind, n in (("choice", 35), ("title", 34), ("credit", 20)):
        r = kind_row(kind)
        assert not lint.check_row(r, "x" * n, B)[0], kind
        assert lint.check_row(r, "x" * (n + 1), B)[0], kind


def test_wide_rows_count_characters():
    assert not errs("r077ac4", "Gentar")
    assert errs("r077ac4", "Gentaro")


def test_rom_strings_keep_the_japanese_pixel_width():
    vp = next(r for r in ROWS.values() if r["kind"] == "string" and r["jp"] == "ＶＰ")
    assert lint.jp_px(vp["jp"]) == 16
    assert not lint.check_row(vp, "VP", B)[0]
    assert lint.check_row(vp, "VPs", B)[0]                    # 18 px > 16 px, though 3 bytes <= 4


def test_marker_build_text_fits_every_budget():
    e, _ = lint.lint(text.iter_rows(), B, marker=True)
    assert not e, e[:10]


def test_translations_fit():
    e, _ = lint.lint(text.iter_rows(), B)
    assert not e, e[:10]
