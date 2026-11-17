"""tour_sheets.py: EN | JP review sheets for the visual-QA gate, one directory per warp scene.

    python -X utf8 tools/tour_sheets.py [--en work/qa/tour] [--jp work/qa/tour_jp] [--out work/qa/tour_sheets]

For every scene in --en, runs the skill's sheet.py on its f*.png frames at full size, keeping only frames that
changed (--changed 0.02), each paired with the same-numbered JP frame (--compare), 8 tiles per page. Then:
    qa_gate.py init work/qa/manifest.tsv work/qa/tour_sheets --glob "*sheet*.png" --build build/vattroller_x_en.gba
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SCRIPTS  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--en", default="work/qa/tour")
    ap.add_argument("--jp", default="work/qa/tour_jp")
    ap.add_argument("--out", default="work/qa/tour_sheets")
    a = ap.parse_args()
    sheet = Path(SCRIPTS) / "sheet.py"
    en, jp, out = ROOT / a.en, ROOT / a.jp, ROOT / a.out
    n = 0
    for scene in sorted(p for p in en.iterdir() if p.is_dir()):
        frames = sorted(scene.glob("f*.png"))
        if not frames:
            continue
        dest = out / scene.name
        if dest.exists():
            shutil.rmtree(dest)
        dest.mkdir(parents=True)
        cmd = [sys.executable, "-X", "utf8", str(sheet), str(scene), "--div", "1", "--cols", "2", "--max", "8",
               "--changed", "0.02", "--out", str(dest / "sheet.png")]
        if (jp / scene.name).is_dir():
            cmd += ["--compare", str(jp / scene.name)]
        subprocess.run(cmd, check=True, capture_output=True)
        n += len(list(dest.glob("sheet*.png")))
    print(f"{n} sheets in {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
