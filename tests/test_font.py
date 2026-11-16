"""Pair-glyph font (tools/font.py) and the marker build layout."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import font  # noqa: E402
import romtext  # noqa: E402
import text  # noqa: E402


def test_pair_indices_unique_and_past_the_japanese_glyphs():
    idx = font.pair_glyphs_index_range()
    assert len(set(idx)) == len(idx)
    assert min(idx) >= font.N_GLYPHS and max(idx) <= 0xFFFF


def test_glyph_area_clear_of_string_area_and_events():
    import build
    base = 0x3F4E44     # archive file 1135 in the original ROM
    lo, hi = base + min(font.pair_glyphs_index_range()) * 128, base + max(font.pair_glyphs_index_range()) * 128 + 128
    assert font.NEW_WIDTHS + 0x10000 <= romtext.STR_START < romtext.STR_END <= lo
    assert hi <= build.EVENTS_FREE


def test_every_char_has_a_glyph_within_five_columns():
    g = font.load_glyphs()
    assert all(font.glyph_width(g[chr(c)]) <= 5 for c in range(0x20, 0x7F))


def test_encode_aligns_two_byte_chars_and_pads_to_even():
    e = lambda s: font.encode(s, text.encode)   # noqa: E731
    assert e("Hi") == b"Hi"
    assert e("Hey") == b"Hey "
    assert e("A∴!") == b"A \x81\x88! "
    assert e("[5B]x") == b"[x"
    assert font.width_px("Hey") == 24 and font.width_px("A∴") == 24


@pytest.mark.skipif(not any((ROOT / "rom").glob("*.gba")), reason="no ROM dump in rom/")
def test_marker_build_patches_literals_and_repoints():
    import archive
    import build
    rom = archive.ROM.read_bytes()
    out, log = build.build(rom, marker=True)
    for a in font.THRESHOLD_LITS:
        assert struct.unpack_from("<I", out, a)[0] == 0x1F
    for a in font.WIDTH_LITS:
        assert struct.unpack_from("<I", out, a)[0] == 0x08000000 + font.NEW_WIDTHS
    assert out[font.NEW_WIDTHS:font.NEW_WIDTHS + font.N_GLYPHS] == rom[font.WIDTHS:font.WIDTHS + font.N_GLYPHS]
    # the name marker string stays where the typer compares against it
    assert rom[0xE21D8:0xE21DA] == out[0xE21D8:0xE21DA] == "∴".encode("cp932")
    assert struct.unpack_from("<I", out, 0xEC704)[0] == 0x080E21D8
