"""Identity build: unpack and repack every event file with no edits; the ROM must be byte-identical."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

if not any((ROOT / "rom").glob("*.gba")):
    pytest.skip("no ROM dump in rom/", allow_module_level=True)

import archive  # noqa: E402
import build  # noqa: E402
import events  # noqa: E402


def test_identity_build_is_byte_identical():
    rom = archive.ROM.read_bytes()
    out, log = build.build(rom)
    assert log == []
    assert bytes(out) == rom


def test_write_files_in_place_and_relocated():
    rom = archive.ROM.read_bytes()
    ar = archive.Archive(rom)
    small = ar.file(2475)[:-4]
    big = ar.file(2476) + b"\0" * 64
    out, log = archive.write_files(rom, {2475: small, 2476: big})
    ar2 = archive.Archive(bytes(out))
    assert ar2.offset(2475) == ar.offset(2475) and ar2.file(2475) == small
    assert ar2.offset(2476) == archive.FREE_START and ar2.file(2476) == big
    untouched = [i for i in range(len(ar)) if i not in (2475, 2476)]
    assert all(ar2.file(i) == ar.file(i) and ar2.offset(i) == ar.offset(i) for i in untouched)
    assert {what for _, _, what in log} == {"file 2475", "entry 2475", "file 2476", "entry 2476"}


def test_grown_event_file_round_trips_through_rom():
    rom = archive.ROM.read_bytes()
    ev = events.parse(archive.Archive(rom).file(2475))
    for _, n in ev.text_nodes():
        n.set_text(n.text + b"\x82\xa0" * 8)
    new = ev.build()
    out, _ = archive.write_files(rom, {2475: new})
    assert archive.Archive(bytes(out)).file(2475) == new
