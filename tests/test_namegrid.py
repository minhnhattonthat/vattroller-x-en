"""namegrid: the English name-entry keyboard (D13) keeps page 3, writes only its own table entries, and every new
cell's code is the code of the cell whose glyph it copies."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

if not any((ROOT / "rom").glob("*.gba")):
    pytest.skip("no ROM dump in rom/", allow_module_level=True)

import archive  # noqa: E402
import gfx  # noqa: E402
import namegrid as ng  # noqa: E402
import text  # noqa: E402


@pytest.fixture(scope="module")
def built():
    ar = archive.Archive()
    rom = archive.ROM.read_bytes()
    return ar, rom, ng.files(ar, rom)


def test_page3_map_unchanged(built):
    ar, _, new = built
    m0, m = ar.file(ng.MAP), new[ng.MAP]
    lo, hi = ng.HDR + ng.PAGE_ROW[2] * 64, ng.HDR + (ng.PAGE_ROW[2] + 13) * 64
    for r in range(13):
        row = ng.PAGE_ROW[2] + r
        for c in range(32):
            if r == 1 and c == 18:      # DEL outline tile
                continue
            if r == ng.TAB_ROW and any(c in cols for cols, *_ in ng.TABS):
                continue
            assert ng.entry(m0, row, c) == ng.entry(m, row, c), (r, c)
    assert len(m) == len(m0) and lo < hi


def test_table_writes_avoid_text_pointers(built):
    _, rom, _ = built
    owned = {int(p, 16) for rel, r in text.iter_rows() if rel.startswith("rom/") and r["kind"] != "data"
             for p in r.get("ptrs", [])}
    for a, b in ng.table_writes(rom):
        assert not any(a <= p < a + len(b) for p in owned), hex(a)
        assert (a, a + len(b)) in ng.regions()


def test_cell_codes_follow_their_glyphs(built):
    _, rom, new = built
    rows = ng.code_rows(rom)
    writes = dict(ng.table_writes(rom))
    m0, m = archive.Archive().file(ng.MAP), new[ng.MAP]
    src = {tuple(ng.cell_entries(m0, p, r, c)): ng.code_at(rom, rows, p, r, c)
           for p in range(3) for r in range(5) for c in range(14)}
    for p in range(2):
        for r in range(5):
            ptr = struct.unpack("<I", writes[ng.TABLE + 4 * (1 + 7 * p + r)])[0] - 0x08000000
            codes = writes.get(ptr) or bytes(rom[ptr:ptr + 28])
            for c in range(14):
                es = tuple(ng.cell_entries(m, p, r, c))
                if all(e & 0x3FF == ng.BLANK_TILE for e in es):
                    assert codes[2 * c:2 * c + 2] == "　".encode("cp932"), (p, r, c)
                else:
                    assert src[es] == codes[2 * c:2 * c + 2], (p, r, c)


def test_431_changes_only_box_tiles():
    ar = archive.Archive()
    orig, new = ar.file(gfx.SHEET_431), gfx.files(ar)[gfx.SHEET_431]
    allowed = {t for first, count, _ in gfx.BOXES_431 for t in range(first, first + count)}
    changed = {i // 32 for i in range(len(orig)) if orig[i] != new[i]}
    assert changed and changed <= allowed
