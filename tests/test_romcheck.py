"""romcheck: every changed byte logged, no overlapping writes, each writer inside its region."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

if not any((ROOT / "rom").glob("*.gba")):
    pytest.skip("no ROM dump in rom/", allow_module_level=True)

import archive  # noqa: E402
import romcheck  # noqa: E402
import romtext  # noqa: E402
import text  # noqa: E402

ORIG = archive.ROM.read_bytes()


def string_row():
    return next(r for rel, r in text.iter_rows() if rel.startswith("rom/") and r["kind"] == "string" and r["ptrs"])


def test_clean_string_write_passes():
    r = string_row()
    new = bytearray(ORIG) + b"\xff" * (romtext.STR_START + 16 - len(ORIG))
    new[romtext.STR_START:romtext.STR_START + 3] = b"Hi\0"
    p = int(r["ptrs"][0], 16)
    new[p:p + 4] = struct.pack("<I", 0x08000000 + romtext.STR_START)
    log = [(romtext.STR_START, romtext.STR_START + 3, r["id"]), (p, p + 4, f"{r['id']} ptr")]
    assert romcheck.verify(ORIG, new, log) == []


def test_unlogged_byte_fails():
    new = bytearray(ORIG)
    new[0x200] ^= 0xFF
    assert any("outside writes" in e for e in romcheck.verify(ORIG, new, []))


def test_overlap_and_wrong_region_fail():
    r = string_row()
    new = bytearray(ORIG)
    p = int(r["ptrs"][0], 16)
    new[p:p + 4] = b"\x00\x00\x00\x09"
    errs = romcheck.verify(ORIG, new, [(p, p + 4, r["id"]), (p + 2, p + 4, f"{r['id']} ptr")])
    assert any("overlaps" in e for e in errs)
    assert any("outside its allowed region" in e for e in errs)     # a string body written over a pointer slot
