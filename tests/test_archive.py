import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

if not any((ROOT / "rom").glob("*.gba")):
    pytest.skip("no ROM dump in rom/", allow_module_level=True)

import archive  # noqa: E402


def test_files_are_contiguous():
    ar = archive.Archive()
    assert ar.offset(0) == archive.DATA_START
    for i in range(len(ar) - 1):
        assert ar.offset(i) + ar.size(i) == ar.offset(i + 1)
    assert ar.offset(len(ar) - 1) + ar.size(len(ar) - 1) == archive.DATA_END


def test_huffman_files_decode_to_header_size():
    ar = archive.Archive()
    for i in (1317, 1352, 1358):
        src = ar.file(i)
        out, how = archive.unpack(src)
        assert how == "huff"
        assert len(out) == src[1] | src[2] << 8 | src[3] << 16
