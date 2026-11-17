"""gfx: graphics-text redraws change only the declared tiles and keep each label's arrow."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

if not any((ROOT / "rom").glob("*.gba")):
    pytest.skip("no ROM dump in rom/", allow_module_level=True)

import archive  # noqa: E402
import gfx  # noqa: E402


def test_446_changes_only_label_tiles():
    ar = archive.Archive()
    orig, new = ar.file(gfx.SHEET), gfx.files(ar)[gfx.SHEET]
    assert len(new) == len(orig)
    allowed = {t for first, count, _ in gfx.LABELS for t in range(first, first + count)}
    changed = {i // 32 for i in range(len(orig)) if orig[i] != new[i]}
    assert changed and changed <= allowed


def test_credit_outline_rule_reproduces_original():
    px = gfx.credit_px(archive.Archive().file(gfx.SHEET_452))
    assert gfx.credit_outline([[c == 1 for c in row] for row in px]) == px


def test_452_changes_only_credit_tiles_and_drops_kana():
    ar = archive.Archive()
    orig, new = ar.file(gfx.SHEET_452), gfx.files(ar)[gfx.SHEET_452]
    assert len(new) == len(orig)
    allowed = {f + k for f in gfx.CREDIT_ROWS for k in range(gfx.CREDIT_TILES)}
    changed = {i // 32 for i in range(len(orig)) if orig[i] != new[i]}
    assert changed and changed <= allowed
    ink = lambda px: sum(c == 1 for row in px for c in row)  # noqa: E731
    letters = sum(r.count("#") for ch in gfx.CREDIT_TEXT if ch != " " for r in gfx.CREDIT_GLYPHS[ch])
    keep = sum(1 for row in gfx.credit_px(orig) for lo, hi in gfx.CREDIT_KEEP for c in row[lo:hi] if c == 1)
    assert ink(gfx.credit_px(new)) == keep + letters


def test_433_changes_only_the_death_roll_spine():
    ar = archive.Archive()
    orig, new = ar.file(gfx.SHEET_433), gfx.files(ar)[gfx.SHEET_433]
    assert len(new) == len(orig)
    first = gfx.SPINE_FIRST
    changed = {i // 32 for i in range(len(orig)) if orig[i] != new[i]}
    assert changed and changed <= set(range(first, first + gfx.SPINE_W * gfx.SPINE_H))
    a, b = gfx.spine_px(orig), gfx.spine_px(new)
    assert a[:gfx.SPINE_ROWS[0]] == b[:gfx.SPINE_ROWS[0]] and a[gfx.SPINE_ROWS[1]:] == b[gfx.SPINE_ROWS[1]:]


def test_signs_change_only_their_tiles_inside_the_box():
    ar = archive.Archive()
    new = gfx.files(ar)
    for s in gfx.SIGNS:
        orig = ar.file(s["file"])
        tiles = {n for row in s["grid"] for n in row}
        changed = {i // 32 for i in range(len(orig)) if orig[i] != new[s["file"]][i]}
        assert changed and changed <= tiles, s["text"]
        a, b = gfx.sign_px(orig, s["grid"]), gfx.sign_px(new[s["file"]], s["grid"])
        x0, y0, x1, y1 = s["box"]
        assert all(a[y][x] == b[y][x] for y in range(len(a)) for x in range(len(a[0]))
                   if not (x0 <= x < x1 and y0 <= y < y1)), s["text"]


def test_441_changes_only_card_blocks_and_keeps_the_dots():
    ar = archive.Archive()
    orig, new = ar.file(gfx.CARD_FILE), gfx.files(ar)[gfx.CARD_FILE]
    assert len(new) == len(orig)
    allowed = {off + i for ln in gfx.CARD_LINES for off, w, h, _, _ in ln["front"] + ln["back"]
               for i in range(w * h // 2)}
    changed = {i for i in range(len(orig)) if orig[i] != new[i]}
    assert changed and changed <= allowed
    for ln in gfx.CARD_LINES:
        for layer, dy in (("front", 0), ("back", ln["shadow"][1])):
            a, b = gfx.card_blocks(orig, ln[layer]), gfx.card_blocks(new, ln[layer])
            assert all(a[p] == b[p] for p in a if not ln["y0"] + dy <= p[1] < ln["y1"] + dy)


def test_labels_keep_their_arrow():
    ar = archive.Archive()
    orig, new = ar.file(gfx.SHEET), gfx.files(ar)[gfx.SHEET]
    for first, _, _ in gfx.LABELS:
        a, b = gfx.tile_px(orig, first), gfx.tile_px(new, first)
        assert all(a[y][x] == b[y][x] for y in range(8) for x in range(gfx.ARROW_W))
