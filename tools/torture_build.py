"""torture_build.py: marker build with the glyph torture lines (phase 5 width gate): every printable ASCII char
plus double spaces, on the rpg_start line e2520_0043c and its two choices e2520_0046c.0/.1.

    python -X utf8 tools/torture_build.py [OUT.gba]      # default work/exp/torture.gba
    then: warp.py mk_ruler_rpg-style state, press A once (see docs/re/font.md §Width gate)"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINES = {
    "e2520_0043c": "Aa  Bb !\"#$%&'()*+,-./0123456789:;",
    "e2520_0046c.0": "<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^",
    "e2520_0046c.1": "_`abcdefghijklmnopqrstuvwxyz{|}~  .",
}


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "work" / "exp" / "torture.gba")
    chars = "".join(LINES.values())
    missing = [chr(c) for c in range(0x20, 0x7F) if chr(c) not in chars]
    assert not missing, missing
    args = [sys.executable, "-X", "utf8", str(ROOT / "tools" / "exp_build.py"), out]
    for k, v in LINES.items():
        args += ["--id", f"{k}={v}"]
    sys.exit(subprocess.run(args).returncode)


if __name__ == "__main__":
    main()
