"""tagfont: the 8x8-blitter hook that draws English pairs in speaker tags and choice headers."""
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


def test_table_tile_holds_both_letters():
    t = tagfont.table()
    assert len(t) == tagfont.TABLE_END - tagfont.TABLE
    i = font.pair_index(ord("K"), ord("o")) - tagfont.FIRST
    tile = t[i * 32:i * 32 + 32]
    px = [[(tile[y * 4 + x // 2] >> 4 * (x & 1)) & 15 for x in range(8)] for y in range(8)]
    assert any(px[y][x] == font.INK for y in range(8) for x in range(3))       # K
    assert any(px[y][x] == font.INK for y in range(8) for x in range(4, 7))    # o
    blank = tagfont.to_tile(tagfont.render_tile(tagfont.load_font3(), None, None))
    assert t[:32] == tagfont.table()[:32] and blank in t                        # unused indices stay blank


def test_hook_disassembles_as_intended():
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    code = tagfont.hook_code()
    ops = [f"{i.mnemonic} {i.op_str}" for i in md.disasm(code[:0x18], 0x08000000 + tagfont.HOOK)]
    assert ops[0] == "ldrh r0, [r5]" and ops[-1] == "bx lr"
    assert struct.unpack_from("<II", code, 0x18) == (tagfont.FIRST, 0x08000000 + tagfont.TABLE)
    # both literal loads point at the pool words
    assert "[pc, #0x14]" in ops[1] and "[pc, #8]" in ops[9]


def test_call_site_branches_to_hook():
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    for site in tagfont.SITES:
        ins = list(md.disasm(tagfont.bl(site, tagfont.HOOK), 0x08000000 + site))
        assert ins[0].mnemonic == "bl" and int(ins[0].op_str.lstrip("#"), 16) == 0x08000000 + tagfont.HOOK
