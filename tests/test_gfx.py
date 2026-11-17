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


def test_labels_keep_their_arrow():
    ar = archive.Archive()
    orig, new = ar.file(gfx.SHEET), gfx.files(ar)[gfx.SHEET]
    for first, _, _ in gfx.LABELS:
        a, b = gfx.tile_px(orig, first), gfx.tile_px(new, first)
        assert all(a[y][x] == b[y][x] for y in range(8) for x in range(gfx.ARROW_W))
