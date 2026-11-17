"""Row-kind rules found in the marker tour (phase 5): table bases and blank fills are data, name-entry rows are wide."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build  # noqa: E402
import font  # noqa: E402
import text  # noqa: E402

ROWS = {r["id"]: r for _, r in text.iter_rows()}


def test_credits_table_base_is_not_repointed():
    assert ROWS["r074570"]["kind"] == "data"


def test_fullwidth_space_strings_are_data():
    blanks = [r for r in ROWS.values() if r["id"][0] == "r" and set(r["jp"]) <= {"　"}]
    assert blanks and all(r["kind"] == "data" for r in blanks)


def test_wide_rows_build_as_fullwidth_sjis():
    grid, name = ROWS["r077798"], ROWS["r077ac4"]
    assert grid["wide"] and grid["max"] == 14 and name["wide"] and name["max"] == 6
    assert font.widen("Gen 1!") == "Ｇｅｎ　１！"
    s = font.widen(build.marker_text(grid))
    assert len(s) == 14 and all(ord(c) > 0x7F for c in s)
    raw = text.encode(s)
    assert len(raw) == 28 and all(raw[i] >= 0x81 for i in range(0, 28, 2))
