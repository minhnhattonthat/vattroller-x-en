"""Debug tool data: scenes.json is well formed, rooms.json matches the ROM; one warp runs in the emulator (slow)."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DEBUG = ROOT / "tools" / "debug"
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(DEBUG))
HAVE_ROM = any((ROOT / "rom").glob("*.gba"))
FIELDS = {"name", "book", "room", "post", "hold", "stop_at", "csteps", "mashpost", "frames", "desc", "from_room",
          "from_nth", "expect", "x", "y", "face", "entry", "via", "unlock", "premash", "node", "scripts"}


def test_scenes_are_well_formed():
    scenes = json.loads((DEBUG / "scenes.json").read_text(encoding="utf-8"))["scenes"]
    names = [s["name"] for s in scenes]
    assert len(names) == len(set(names))
    for s in scenes:
        assert set(s) <= FIELDS, s["name"]
        assert -1 <= s["book"] <= 15
        assert 0 <= s.get("room", 0) < 236
        assert s.get("stop_at", "title") in ("title", "titlemenu", "shelf", "prompt", "creation")
        for step in s.get("post", "").split(";") if s.get("post") else []:
            n, keys = step.split()
            assert int(n) > 0 and keys


@pytest.mark.skipif(not HAVE_ROM, reason="no ROM dump in rom/")
def test_rooms_json_matches_rom():
    import rooms
    from archive import Archive
    saved = json.loads((DEBUG / "rooms.json").read_text(encoding="utf-8"))
    assert saved == rooms.rooms(Archive())


@pytest.mark.slow
@pytest.mark.skipif(not HAVE_ROM, reason="no ROM dump in rom/")
def test_warp_reaches_a_comic_chapter():
    r = subprocess.run([sys.executable, "-X", "utf8", str(DEBUG / "warp.py"), "comic_gekitou2",
                        "--out", str(ROOT / "work" / "qa" / "test_warp")], cwd=ROOT)
    assert r.returncode == 0
