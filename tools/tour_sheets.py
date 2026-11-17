"""tour_sheets.py: EN | JP review sheets for the visual-QA gate, one directory per warp scene.

    python -X utf8 tools/tour_sheets.py [--en work/qa/tour] [--jp work/qa/tour_jp] [--out work/qa/tour_sheets]

For every scene in --en, runs the skill's sheet.py on its f*.png frames at full size, keeping only frames that
changed (--changed 0.02), each paired with the same-numbered JP frame (--compare), 8 tiles per page. Frames
before the book opens (log line "fN phase open": logos, title, title menu, shelf) are the same in every scene, so
they are kept only for the scenes in BOOT (--all-frames keeps them everywhere). Then:
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

BOOT = {"title", "titlemenu", "shelf", "prompt_comic", "prompt_deathroll", "prompt_rpg"}


def book_open(scene):
    """Frame of the "phase open" log line (the book starts), or None."""
    log = scene / "log.txt"
    if log.exists():
        for line in log.read_text(encoding="utf8", errors="replace").splitlines():
            parts = line.split()
            if len(parts) >= 3 and parts[1:3] == ["phase", "open"] and parts[0][1:].isdigit():
                return int(parts[0][1:])
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--en", default="work/qa/tour")
    ap.add_argument("--jp", default="work/qa/tour_jp")
    ap.add_argument("--out", default="work/qa/tour_sheets")
    ap.add_argument("--all-frames", action="store_true", help="keep the boot frames in every scene")
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
        start = None if a.all_frames or scene.name in BOOT else book_open(scene)
        if start is not None:
            cmd += ["--from", str(start)]
        if (jp / scene.name).is_dir():
            cmd += ["--compare", str(jp / scene.name)]
        subprocess.run(cmd, check=True, capture_output=True)
        n += len(list(dest.glob("sheet*.png")))
    print(f"{n} sheets in {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
