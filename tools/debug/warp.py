"""warp.py: reach any scene in tools/debug/scenes.json from a cold boot (phase 2 debug tool, docs/re/debug.md).

    python -X utf8 tools/debug/warp.py SCENE [SCENE..] [--rom ROM] [--out DIR] [--state] [--sheet]
    python -X utf8 tools/debug/warp.py --all [--jobs 3] [--state]     # every scene; also the "regen all states" command
    python -X utf8 tools/debug/warp.py --list

Each scene runs tools/debug/warp.lua in emu.py with the scene's vars, lands in work/qa/warp/<scene>/scene.png and,
with --state, saves work/states/<scene>.mss. warp.lua asserts the room id before the shot, so a run that ends in the
wrong place fails (exit 1). Default ROM: build/vattroller_x_en.gba if it exists, else the original dump.
"""
import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

SCENES = ROOT / "tools" / "debug" / "scenes.json"
ROOMS = ROOT / "tools" / "debug" / "rooms.json"
WARP = ROOT / "tools" / "debug" / "warp.lua"
MASH = ROOT / "tools" / "lua" / "mash2.lua"
ORIG = ROOT / "rom" / "Vattroller X (Japan).gba"
BUILD = ROOT / "build" / "vattroller_x_en.gba"
VARS = ("BOOK", "ROOM", "HOLD", "UNLOCK", "MASHPOST", "EXPECT", "X", "Y", "FACE", "FROM_ROOM", "FROM_NTH", "CSTEPS")
STRVARS = ("POST", "STOP_AT", "VIA")
EXTRA = []  # extra emu.py args from --script / --var


def load():
    return {s["name"]: s for s in json.loads(SCENES.read_text(encoding="utf-8"))["scenes"]}


def lua_str(s):
    return "[[" + s + "]]"


def with_entry(scene):
    """RPG-slot scenes with a room and no x/y get the room's most used entry point from rooms.json."""
    if "room" not in scene or "x" in scene or scene.get("book", 8) >= 8:
        return scene
    rooms = json.loads(ROOMS.read_text(encoding="utf-8"))
    e = rooms[scene["room"]]["entries"]
    if not e:
        return scene
    x, y, f = e[scene.get("entry", 0)]
    return {**scene, "x": x, "y": y, "face": f}


def with_premash(scene):
    """premash N: tap A (8 frames on, 8 off) for N frames before the scene's post route (RPG intro to free control)."""
    n = scene.get("premash", 0)
    if not n:
        return scene
    post = ";".join(["8 a;8 -"] * (n // 16))
    if scene.get("post"):
        post += ";" + scene["post"]
    return {**scene, "post": post}


def run(scene, rom, outroot, state, sheet):
    scene = with_premash(with_entry(scene))
    out = outroot / scene["name"]
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(rom), "--out", str(out),
           "--script", WARP.as_posix(), "--frames", str(scene.get("frames", 12000)), "--timeout", "600"]
    for k in VARS:
        if k.lower() in scene:
            cmd += ["--var", f"{k}={scene[k.lower()]}"]
    for k in STRVARS:
        if k.lower() in scene:
            cmd += ["--var", f"{k}={lua_str(scene[k.lower()])}"]
    if state:
        cmd += ["--var", f"STATE_OUT={lua_str((ROOT / 'work' / 'states' / (scene['name'] + '.mss')).as_posix())}"]
    if sheet:
        cmd += ["--shot-every", "120", "--sheet"]
    for extra in EXTRA:
        cmd += extra
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "emu.out", "w", encoding="utf-8") as f:
        r = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, cwd=ROOT)
    log = (out / "log.txt").read_text(encoding="utf-8", errors="replace") if (out / "log.txt").exists() else ""
    ok = r.returncode == 0 and " done room=" in log and (out / "scene.png").exists()
    return scene["name"], ok, r.returncode, out


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("scenes", nargs="*")
    p.add_argument("--all", action="store_true")
    p.add_argument("--list", action="store_true")
    p.add_argument("--rom")
    p.add_argument("--out", default=str(ROOT / "work" / "qa" / "warp"))
    p.add_argument("--state", action="store_true", help="save work/states/<scene>.mss")
    p.add_argument("--sheet", action="store_true", help="also shoot every 120 frames and make a contact sheet")
    p.add_argument("--jobs", type=int, default=1)
    p.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                   help="override a scene field (book, room, post, hold, ...); with an unknown scene name, "
                        "defines an ad-hoc scene: warp.py try1 --set book=0 --set room=27")
    p.add_argument("--script", action="append", default=[], help="extra Lua probe for emu.py (repeatable)")
    p.add_argument("--var", action="append", default=[], help="extra emu.py --var (repeatable)")
    a = p.parse_args()
    EXTRA.extend(["--script", s] for s in a.script)
    EXTRA.extend(["--var", v] for v in a.var)
    scenes = load()
    over = {}
    for kv in a.set:
        k, v = kv.split("=", 1)
        over[k.lower()] = int(v, 0) if v.lstrip("-").isdigit() or v.startswith("0x") else v
    if over:
        for n in a.scenes:
            scenes[n] = {**scenes.get(n, {"name": n}), **over}
    if a.list:
        for s in scenes.values():
            print(f"{s['name']:24} {s.get('desc', '')}")
        return 0
    names = list(scenes) if a.all else a.scenes
    unknown = [n for n in names if n not in scenes]
    if unknown or not names:
        p.error(f"unknown scene(s): {unknown}" if unknown else "name a scene, or --all")
    rom = Path(a.rom) if a.rom else (BUILD if BUILD.exists() else ORIG)
    outroot = Path(a.out)
    with ThreadPoolExecutor(max(1, a.jobs)) as ex:
        results = list(ex.map(lambda n: run(scenes[n], rom, outroot, a.state, a.sheet), names))
    bad = 0
    for name, ok, rc, out in results:
        print(f"{'ok  ' if ok else 'FAIL'} {name:24} exit {rc}  {out / 'scene.png'}")
        bad += not ok
    print(f"{len(results) - bad}/{len(results)} scenes reached on {rom.name}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
