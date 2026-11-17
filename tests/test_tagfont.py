"""tagfont: the narrow-blitter hooks that draw English pairs in speaker tags, headers and VS names."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import font  # noqa: E402
import tagfont  # noqa: E402

capstone = pytest.importorskip("capstone")


def test_font3_has_every_printable_char():
    g = tagfont.load_font3()
    assert all(chr(c) in g for c in range(font.FIRST_CHAR, font.LAST_CHAR + 1))


@pytest.mark.parametrize("cell", tagfont.CELLS, ids=lambda c: c.name)
def test_cell_holds_both_letters(cell):
    t = tagfont.table(cell)
    size = 32 * cell.h // 8
    assert len(t) == cell.table_end - cell.table == tagfont.N * size
    i = font.pair_index(ord("K"), ord("o")) - tagfont.FIRST
    data = t[i * size:(i + 1) * size]
    px = [[(data[y * 4 + x // 2] >> 4 * (x & 1)) & 15 for x in range(8)] for y in range(cell.h)]
    assert any(px[y][x] == cell.ink for y in range(cell.h) for x in range(3))       # K
    assert any(px[y][x] == cell.ink for y in range(cell.h) for x in range(4, 7))    # o
    assert {v for row in px for v in row} <= {cell.bg, cell.ink, cell.shadow}


def test_tables_and_hooks_do_not_overlap():
    spans = sorted(tagfont.regions())
    assert all(a[1] <= b[0] for a, b in zip(spans, spans[1:]))
    assert all(0x120 <= c.hook and c.hook + 0x20 <= 0x200 for c in tagfont.CELLS)


@pytest.mark.parametrize("cell", tagfont.CELLS, ids=lambda c: c.name)
def test_hook_disassembles_as_intended(cell):
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    code = tagfont.hook_code(cell)
    ops = [f"{i.mnemonic} {i.op_str}" for i in md.disasm(code[:0x18], 0x08000000 + cell.hook)]
    assert ops[0] == "ldrh r0, [r5]" and ops[-1] == "bx lr"
    assert ops[4] == f"lsls r0, r0, #{cell.shift}" and ops[8] == f"lsls r0, r0, #{cell.shift}"
    assert "[pc, #0x14]" in ops[1] and "[pc, #8]" in ops[9]
    assert struct.unpack_from("<II", code, 0x18) == (tagfont.FIRST, 0x08000000 + cell.table)


def test_call_sites_branch_to_their_hook():
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    for cell in tagfont.CELLS:
        for site in cell.sites:
            ins = list(md.disasm(tagfont.bl(site, cell.hook), 0x08000000 + site))
            assert ins[0].mnemonic == "bl" and int(ins[0].op_str.lstrip("#"), 16) == 0x08000000 + cell.hook
