"""cardtest.py: show any VS rule-card word in game without reaching its battle (G12 check).

Writes work/qa/g12/card_<frame>.gba = the built ROM with frame-table entries 3 and 4 (the OFFICIAL slide-in and
final frame, the card `rpg_tutorial` plays) pointing at another word's final frame, then warps to rpg_tutorial and
dumps the screen at the card (frame ~10560; the run lands at 10500-10620, f010680 is already the battle). Final frames: 13 SURVIVAL, 16 GRAB LOTS, 19 KNOCK DOWN, 22 DRAIN HP,
25 BEAT THE BOSS (tools/cardframes.py).

    python -X utf8 tools/cardtest.py 13 16 19 22 25 [--frames 10620,10680]
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import cardframes  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("frames", type=int, nargs="+")
    ap.add_argument("--rom", default=str(ROOT / "build" / "vattroller_x_en.gba"))
    ap.add_argument("--at", default="10500,10560,10620")
    a = ap.parse_args()
    rom = bytearray(Path(a.rom).read_bytes())
    table = int.from_bytes(rom[cardframes.SET + 8:cardframes.SET + 12], "little") & 0x1FFFFFF
    out = ROOT / "work" / "qa" / "g12"
    out.mkdir(parents=True, exist_ok=True)
    for n in a.frames:
        test = bytearray(rom)
        for i in (3, 4):
            test[table + 12 * i:table + 12 * i + 12] = rom[table + 12 * n:table + 12 * n + 12]
        path = out / f"card_{n}.gba"
        path.write_bytes(test)
        cmd = [sys.executable, "-X", "utf8", str(ROOT / "tools" / "debug" / "warp.py"), "rpg_tutorial",
               "--rom", str(path), "--out", str(out / f"run_{n}"), "--set", "frames=" + str(max(map(int, a.at.split(","))) + 60),
               "--script", str(ROOT / "tools" / "lua" / "dumpframes.lua"), "--var", "DUMP_FRAMES={" + a.at + "}"]
        r = subprocess.run(cmd, cwd=ROOT)
        print(n, "exit", r.returncode, out / f"run_{n}")


if __name__ == "__main__":
    main()
