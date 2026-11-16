"""archive.py: the game's resource archive (docs/re/archive.md).

Table at ROM 0x100000: 2714 entries of (u32 GBA pointer, u32 size); files are stored back to back from 0x1054D0 to
0x7FF268 in table order. Code reaches the table through literal pointers at 0xEC740, 0xFC4D8 and 0x312D10.

    python -X utf8 tools/archive.py info N        # pointer, size, first bytes
    python -X utf8 tools/archive.py dump N OUT    # write one file (LZ10 decompressed with --lz)"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Vattroller X (Japan).gba"
TABLE = 0x100000
COUNT = 2714
DATA_START = 0x1054D0
DATA_END = 0x7FF268


class Archive:
    def __init__(self, rom=None):
        self.rom = rom if rom is not None else ROM.read_bytes()
        self.entries = [struct.unpack_from("<II", self.rom, TABLE + 8 * i) for i in range(COUNT)]

    def __len__(self):
        return COUNT

    def offset(self, i):
        return self.entries[i][0] - 0x08000000

    def size(self, i):
        return self.entries[i][1]

    def file(self, i):
        o = self.offset(i)
        return self.rom[o:o + self.size(i)]


def lz10_decompress(src):
    if src[0] != 0x10:
        raise ValueError("not LZ10")
    size = src[1] | src[2] << 8 | src[3] << 16
    out = bytearray()
    i = 4
    while len(out) < size:
        flags = src[i]
        i += 1
        for bit in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> bit):
                b1, b2 = src[i], src[i + 1]
                i += 2
                n = (b1 >> 4) + 3
                disp = ((b1 & 15) << 8 | b2) + 1
                if disp > len(out):
                    raise ValueError("back-reference before start")
                for _ in range(n):
                    out.append(out[-disp])
            else:
                out.append(src[i])
                i += 1
    return bytes(out[:size])


def huff_decompress(src):
    """GBA BIOS Huffman (type 0x24 = 4-bit, 0x28 = 8-bit)."""
    bits = src[0] & 15
    if src[0] & 0xF0 != 0x20 or bits not in (4, 8):
        raise ValueError("not Huffman")
    size = src[1] | src[2] << 8 | src[3] << 16
    tree_size = (src[4] + 1) * 2
    tree = 4  # tree[0] = size byte; root node at offset 5
    pos = 4 + tree_size
    out = bytearray()
    acc, nacc = 0, 0
    node = 5
    while len(out) < size:
        word = int.from_bytes(src[pos:pos + 4], "little")
        pos += 4
        for b in range(31, -1, -1):
            bit = word >> b & 1
            n = src[node]
            child = (node & ~1) + (n & 0x3F) * 2 + 2 + bit
            is_data = n & (0x80 if bit == 0 else 0x40)
            if is_data:
                val = src[child]
                if bits == 8:
                    out.append(val)
                else:
                    acc |= val << (4 * nacc)
                    nacc += 1
                    if nacc == 2:
                        out.append(acc)
                        acc, nacc = 0, 0
                node = 5
                if len(out) >= size:
                    break
            else:
                node = child
    del tree
    return bytes(out[:size])


def unpack(data):
    """Decompress a file if it carries a BIOS LZ10 or Huffman header; return (bytes, how)."""
    try:
        if data[:1] == b"\x10":
            return lz10_decompress(data), "lz10"
        if data[:1] in (b"\x24", b"\x28"):
            return huff_decompress(data), "huff"
    except (ValueError, IndexError):
        pass
    return data, "raw"


if __name__ == "__main__":
    ar = Archive()
    cmd, n = sys.argv[1], int(sys.argv[2], 0)
    if cmd == "info":
        print(hex(ar.offset(n)), hex(ar.size(n)), ar.file(n)[:32].hex(" "))
    elif cmd == "dump":
        data = ar.file(n)
        if "--lz" in sys.argv:
            data = lz10_decompress(data)
        Path(sys.argv[3]).write_bytes(data)
