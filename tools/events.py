"""events.py: parse and rebuild event files (archive #2475-2711, one per room; docs/re/script.md).

File:   u16 page count, 10 header bytes, then pages.
Page:   u32 size (counted from this field), 8 bytes, then scripts back to back.
Script: header (+2 u16 = 0x24; +4 u32 = offset of the first command, 0x24 except one script in #2604 that keeps
a 0x60-byte data block in its header; +8 u32 = script size), then commands.
Command: u8 op, u8 0, u16 NEXT, args. NEXT is the relative offset of the next command, usually the command's
length, but patched to jump over an else-branch at the end of a then-branch. Op 0x06 (if) also holds +4 THEN
and +6 ELSE (used when +0xA & 0x8000) relative targets. NEXT = 0 on a data-only "script" (move routes).

Commands are nodes reached from the first command through those links; a node's bytes run to the next node
start. Rebuilding lays nodes out in order and recomputes every link. Op 0x06 NEXT with the else flag set is
not a link (never read) and stays as it is. END's NEXT is its length (4), not a link.

    python -X utf8 tools/events.py stats          # scripts, commands, links, text lines
    python -X utf8 tools/events.py lines N        # text commands of file N"""
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from archive import Archive  # noqa: E402

FIRST, LAST = 2475, 2711
HDR = 0x24
OP_TEXT, OP_IF, OP_END = 0x00, 0x06, 0x0C
OP_CHOICE, OP_TITLE = 0x01, 0x13
FIELD_OPS = (OP_CHOICE, OP_TITLE)


def u16(b, o):
    return struct.unpack_from("<H", b, o)[0]


def u32(b, o):
    return struct.unpack_from("<I", b, o)[0]


def link_fields(node):
    """Offsets of the relative-link fields in a command. END's NEXT (always 4) and a data block's 0 are not links."""
    op = node[0]
    if op == OP_END or u16(node, 2) == 0:
        return []
    if op == OP_IF:
        # 0x08031328: true -> +4; false -> +6 if +0xA & 0x8000, else fall through to NEXT. With an else, NEXT is
        # never read (it holds stale values) and is kept as it is.
        return [4, 6] if u16(node, 0xA) & 0x8000 else [2, 4]
    return [2]


def text_size(n):
    return (8 + n + 1 + 3) & ~3


@dataclass
class Node:
    off: int        # offset inside the script, as parsed (0 = first command)
    data: bytearray  # bytes up to the next node

    @property
    def op(self):
        return self.data[0]

    # op 0x00 text line: u16 flags at +4, u16 length at +6, SJIS, NUL, padding
    @property
    def text(self):
        n = u16(self.data, 6)
        return bytes(self.data[8:8 + n])

    def set_text(self, raw: bytes):
        assert self.op == OP_TEXT
        if raw == self.text:
            return
        head = bytes(self.data[:6]) + struct.pack("<H", len(raw))
        body = raw + b"\0"
        self.data = bytearray(head + body + b"\0" * (text_size(len(raw)) - 8 - len(body)))

    # op 0x01 choice / op 0x13 chapter title: u16 op, u16 NEXT, u16 off2, u16 off3, then NUL-terminated SJIS
    # fields, each padded to 4. Field 1 is at +8, field 2 at off2; op 0x13 always has a third (empty) field at
    # off3, op 0x01 has off3 = 0 (no third field). The command ends after the last field's padding.
    def field_offsets(self):
        assert self.op in FIELD_OPS
        offs = [8, u16(self.data, 4)]
        if u16(self.data, 6):
            offs.append(u16(self.data, 6))
        return offs

    @property
    def fields(self):
        return [bytes(self.data[o:self.data.index(0, o)]) for o in self.field_offsets()]

    def layout_fields(self, raws):
        """The command rebuilt with these field bytes (same count as fields)."""
        raws = list(raws)
        assert len(raws) == len(self.field_offsets())
        out = bytearray(self.data[:8])
        offs = []
        for r in raws:
            offs.append(len(out))
            out += r + b"\0" * (4 - len(r) % 4)
        struct.pack_into("<HH", out, 4, offs[1], offs[2] if len(offs) == 3 else 0)
        return out

    def set_fields(self, raws):
        if list(raws) != self.fields:
            self.data = self.layout_fields(raws)


@dataclass
class Script:
    header: bytearray
    nodes: list
    links: list = field(default_factory=list)  # (node index, field offset, target node index or len(nodes) = end)
    pos: int = 0     # offset of the script in the original file (ids for extracted text)

    def node_pos(self, n):
        """Offset of a node in the original file."""
        return self.pos + len(self.header) + n.off

    def build(self):
        pos, o = [], len(self.header)
        for n in self.nodes:
            pos.append(o)
            o += len(n.data)
        pos.append(o)
        out = [bytes(self.header)]
        data = [bytearray(n.data) for n in self.nodes]
        for ni, f, ti in self.links:
            rel = pos[ti] - pos[ni]
            if not 0 <= rel <= 0xFFFF:
                raise ValueError(f"link from node {ni} out of u16 range: {rel}")
            struct.pack_into("<H", data[ni], f, rel)
        out += data
        b = bytearray(b"".join(out))
        struct.pack_into("<I", b, 8, len(b))
        return bytes(b)


def parse_script(b, s):
    size = u32(b, s + 8)
    first = u32(b, s + 4)
    if first < HDR or first % 4 or first >= size:
        raise ValueError(f"script at {s:#x}: command offset {first:#x}")
    e = s + size
    start = s + first
    seen, stack = set(), [start]
    while stack:
        p = stack.pop()
        if p in seen or p == e:
            continue
        if not start <= p < e or p % 4:
            raise ValueError(f"script at {s:#x}: link to {p:#x} outside")
        seen.add(p)
        stack.extend(p + u16(b, p + f) for f in link_fields(b[p:p + 0xC]))
    starts = sorted(seen)
    index = {p: k for k, p in enumerate(starts)}
    index[e] = len(starts)
    nodes, links = [], []
    for k, p in enumerate(starts):
        q = starts[k + 1] if k + 1 < len(starts) else e
        nodes.append(Node(p - start, bytearray(b[p:q])))
        links += [(k, f, index[p + u16(b, p + f)]) for f in link_fields(b[p:p + 0xC])]
    return Script(bytearray(b[s:start]), nodes, links, s), e


@dataclass
class Page:
    header: bytes        # the 8 bytes after the size field
    scripts: list


@dataclass
class EventFile:
    header: bytes        # u16 count + 10 bytes
    pages: list

    def build(self):
        out = bytearray(self.header)
        for pg in self.pages:
            body = pg.header + b"".join(s.build() for s in pg.scripts)
            out += struct.pack("<I", 4 + len(body)) + body
        return bytes(out)

    def scripts(self):
        for pg in self.pages:
            yield from pg.scripts

    def text_nodes(self):
        for si, sc in enumerate(self.scripts()):
            for n in sc.nodes:
                if n.op == OP_TEXT and len(n.data) >= 8:
                    yield si, n


def parse(b):
    count = u16(b, 0)
    o = 0xC
    pages = []
    for _ in range(count):
        size = u32(b, o)
        end = o + size
        s = o + 12
        scripts = []
        while s < end:
            sc, s = parse_script(b, s)
            scripts.append(sc)
        if s != end:
            raise ValueError(f"page at {o:#x}: scripts end at {s:#x}, page at {end:#x}")
        pages.append(Page(bytes(b[o + 4:o + 12]), scripts))
        o = end
    if o != len(b):
        raise ValueError(f"pages end at {o:#x}, file at {len(b):#x}")
    return EventFile(bytes(b[:0xC]), pages)


def load_all(ar=None):
    ar = ar or Archive()
    return {i: parse(ar.file(i)) for i in range(FIRST, LAST + 1)}


def main():
    ar = Archive()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"
    if cmd == "stats":
        nodes = links = lines = scripts = 0
        for i, ev in load_all(ar).items():
            for sc in ev.scripts():
                scripts += 1
                nodes += len(sc.nodes)
                links += len(sc.links)
            lines += sum(1 for _ in ev.text_nodes())
        print(f"files {LAST - FIRST + 1} scripts {scripts} commands {nodes} links {links} text {lines}")
    elif cmd == "lines":
        ev = parse(ar.file(int(sys.argv[2], 0)))
        for si, n in ev.text_nodes():
            print(si, hex(n.off), hex(u16(n.data, 4)), n.text.decode("cp932", "replace"))


if __name__ == "__main__":
    main()
