"""Read words from a GBA RAM dump written by L.dump_ram (EWRAM 256 KB then IWRAM 32 KB).

    python -X utf8 tools/ramview.py RAM.bin ADDR [COUNT] [--size 1|2|4]
    python -X utf8 tools/ramview.py RAM.bin --ptr 0x02009D54 --stride 40 --count 300 --field 0x10:2

--ptr reads a pointer word at that address and walks COUNT records of --stride bytes from it, printing
the --field offset:size of each (several --field allowed).
"""
import argparse
import struct


def load(path):
    with open(path, "rb") as f:
        return f.read()


def addr_to_off(a):
    if 0x02000000 <= a < 0x02040000:
        return a - 0x02000000
    if 0x03000000 <= a < 0x03008000:
        return 0x40000 + (a - 0x03000000)
    raise ValueError(f"not in EWRAM/IWRAM: {a:08X}")


def rd(ram, a, size):
    off = addr_to_off(a)
    return int.from_bytes(ram[off:off + size], "little")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("ram")
    p.add_argument("addr", nargs="?")
    p.add_argument("count", nargs="?", type=int, default=16)
    p.add_argument("--size", type=int, default=4)
    p.add_argument("--ptr")
    p.add_argument("--stride", type=int, default=4)
    p.add_argument("--field", action="append", default=[])
    a = p.parse_args()
    ram = load(a.ram)
    if a.ptr:
        base = rd(ram, int(a.ptr, 16), 4)
        print(f"base {base:08X}")
        for i in range(a.count):
            rec = base + i * a.stride
            vals = []
            for fld in a.field:
                o, s = fld.split(":")
                vals.append(f"{rd(ram, rec + int(o, 16), int(s)):X}")
            print(i, " ".join(vals))
        return
    x = int(a.addr, 16)
    for i in range(a.count):
        print(f"{x + i * a.size:08X} {rd(ram, x + i * a.size, a.size):0{a.size * 2}X}")


if __name__ == "__main__":
    main()
