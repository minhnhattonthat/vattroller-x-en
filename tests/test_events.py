"""Event-file identity and relayout tests (tools/events.py, docs/re/script.md)."""
import re
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

if not any((ROOT / "rom").glob("*.gba")):
    pytest.skip("no ROM dump in rom/", allow_module_level=True)

import archive  # noqa: E402
import events  # noqa: E402


@pytest.fixture(scope="module")
def ar():
    return archive.Archive()


def test_every_event_file_rebuilds_byte_identical(ar):
    bad = [i for i in range(events.FIRST, events.LAST + 1) if events.parse(ar.file(i)).build() != ar.file(i)]
    assert bad == []


def test_every_raw_text_command_is_a_parsed_node(ar):
    """A scan for the op-0 byte pattern finds no text the graph walk missed (hidden in a node's tail)."""
    pat = re.compile(rb"\x00\x00(?=..[\x00-\xff]\x00)", re.S)
    for i in range(events.FIRST, events.LAST + 1):
        b = ar.file(i)
        ev = events.parse(b)
        parsed = sum(1 for _ in ev.text_nodes())
        raw = 0
        for m in pat.finditer(b):
            p = m.start()
            if p % 4 or p + 9 > len(b):
                continue
            size, n = struct.unpack_from("<H", b, p + 2)[0], struct.unpack_from("<H", b, p + 6)[0]
            if n >= 2 and p + 8 + n < len(b) and size == events.text_size(n) and b[p + 8 + n] == 0 \
                    and 0x81 <= b[p + 8] <= 0x9F:
                raw += 1
        assert raw <= parsed, i


def _shape(ev):
    out = []
    for sc in ev.scripts():
        out.append(([n.op for n in sc.nodes], sorted(sc.links)))
    return out


def test_relayout_with_longer_text_keeps_every_link(ar):
    """Grow every text line, rebuild, re-parse: same commands, same links, new text."""
    for i in range(events.FIRST, events.LAST + 1):
        ev = events.parse(ar.file(i))
        before = _shape(ev)
        for _, n in ev.text_nodes():
            n.set_text(n.text + b"\x82\xa0" * 5)
        new = ev.build()
        ev2 = events.parse(new)
        assert _shape(ev2) == before, i
        assert [n.text for _, n in ev2.text_nodes()] == [n.text for _, n in ev.text_nodes()]
