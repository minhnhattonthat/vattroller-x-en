"""helpbub: the 71 SELECT help bubbles are rebuilt in English within each frame's original sprite/tile budget."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

if not any((ROOT / "rom").glob("*.gba")):
    pytest.skip("no ROM dump in rom/", allow_module_level=True)

import archive  # noqa: E402
import helpbub  # noqa: E402


def test_original_frames_decode():
    rom = archive.ROM.read_bytes()
    assert struct.unpack_from("<I", rom, helpbub.ANIM)[0] == 0x08000000 + archive.Archive(rom).offset(helpbub.FILE)
    frs = helpbub.frames(rom)
    assert len(frs) == helpbub.NFRAMES == len(helpbub.TEXT)
    for _, recs in frs:
        for r in recs:
            assert r[2] == 0xF000 and r[3] % 32 == 0


def test_english_fits_each_frame():
    rom = archive.ROM.read_bytes()
    data = archive.Archive(rom).file(helpbub.FILE)
    for k, (os_, ot, ns, nt, ow, nw) in enumerate(helpbub.budget(rom, data)):
        assert ns <= os_ and nt <= ot and nw <= ow, (k, helpbub.TEXT[k])


def test_patch_points_frames_at_english_records():
    rom = archive.ROM.read_bytes()
    ar = archive.Archive(rom)
    files = helpbub.files(ar)
    out, log = archive.write_files(rom, files)
    helpbub.patch(out, log, rom)
    base = struct.unpack_from("<I", out, helpbub.ANIM)[0]
    assert base == struct.unpack_from("<I", out, archive.TABLE + 8 * helpbub.FILE)[0]
    new = files[helpbub.FILE]
    for k in range(helpbub.NFRAMES):
        _, n, _, p = struct.unpack_from("<HHII", out, helpbub.FRAMES + 12 * k)
        for i in range(n):
            off = struct.unpack_from("<6H", out, p - 0x08000000 + 12 * i)[3]
            assert off + 32 <= len(new)
