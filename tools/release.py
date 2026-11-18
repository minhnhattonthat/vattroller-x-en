"""release.py: build, gate and package the release (SKILL.md phase 9, references/pipeline.md §Release).

    python -X utf8 tools/release.py [--version 1.0] [--force] [--skip-build]

Stops at the first failing step:
  1. build              tools/build.py -> build/vattroller_x_en.gba (checks the dump against rom.sha1 first)
  2. check              tools/check.py (tests + width lint + batch check)
  3. smoke              emu.py --smoke on the build
  4. debug tool off     the build carries no marker text; the debug tool is emulator-side Lua only (tools/debug/)
  5. jp_left            no Japanese run a pointer still reaches, except the stale copies in docs/jp_known.tsv
  6. visual/story QA    qa_gate.py check on every work/qa/**/manifest.tsv (+ its sibling verdicts/)
  7. text coverage      strings_tsv.py, cover.py, textcover.py --waive docs/text_unshown.tsv
  8. polish             no unticked "- [ ]" line in docs/polish.md
  9. README             no template placeholder in README.md; base ROM SHA-1 present
 10. patch              BPS (tools/bps.py make verifies itself), then re-applied here to a fresh read of the original
                        and compared with the build
 11. zip                release/Vattroller_X_EN_v<ver>.zip = .bps + README.txt (docs/release_readme.txt filled in)

The build is > 16 MiB, and BPS handles that (bps.py's own re-apply check plus step 10), so no xdelta is needed.
Release files are never overwritten without --force. Publishing is the owner's call, never this script's.
"""
import argparse
import hashlib
import re
import subprocess
import sys
import zipfile
import zlib
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

ORIG = ROOT / "rom" / "Vattroller X (Japan).gba"
BUILD = ROOT / "build" / "vattroller_x_en.gba"
REL = ROOT / "release"
PY = [sys.executable, "-X", "utf8"]


def step(name, cmd=None, ok=None):
    print(f"== {name}", flush=True)
    if cmd is not None:
        r = subprocess.run(cmd, cwd=ROOT)
        if r.returncode:
            sys.exit(f"release: '{name}' failed (exit {r.returncode})")
    if ok is not None:
        msg = ok()
        if msg:
            sys.exit(f"release: '{name}' failed: {msg}")


def hashes(b):
    return {"size": len(b), "crc32": f"{zlib.crc32(b):08X}", "md5": hashlib.md5(b).hexdigest(),
            "sha1": hashlib.sha1(b).hexdigest()}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="1.0")
    ap.add_argument("--force", action="store_true", help="overwrite this version's release files")
    ap.add_argument("--skip-build", action="store_true", help="gate the existing build (no rebuild)")
    a = ap.parse_args()

    from skill import SCRIPTS as _scripts
    import bps
    SCRIPTS = Path(_scripts)  # skill.py gives a str

    stem = f"Vattroller_X_EN_v{a.version}"
    out_bps, out_zip = REL / f"{stem}.bps", REL / f"{stem}.zip"
    if not a.force and (out_bps.exists() or out_zip.exists()):
        sys.exit(f"release: {out_zip.name} or {out_bps.name} exists; pass --force to overwrite")

    if not a.skip_build:
        step("build", PY + [str(ROOT / "tools" / "build.py")])
    step("check", PY + [str(ROOT / "tools" / "check.py")])
    step("smoke", PY + [str(SCRIPTS / "emu.py"), str(BUILD), "--out", str(ROOT / "work" / "qa" / "smoke"),
                        "--route", str(ROOT / "tools" / "routes" / "boot.txt"), "--smoke"])

    built = BUILD.read_bytes()
    step("debug tool off", ok=lambda: "marker text in the build (built with --marker?)"
         if b"quick brown fox" in built else None)
    step("jp_left", PY + [str(SCRIPTS / "jp_left.py"), str(BUILD), "--sjis", "--gba-ptrs", "--orig", str(ORIG),
                          "--known", str(ROOT / "docs" / "jp_known.tsv")])

    # work/qa/old_*/ hold manifests archived from superseded builds: not gated
    manifests = sorted(m for m in (ROOT / "work" / "qa").glob("**/manifest.tsv")
                       if not any(p.startswith("old_") for p in m.relative_to(ROOT / "work" / "qa").parts))
    if not manifests:
        sys.exit("release: no QA manifest under work/qa")
    for m in manifests:
        step(f"qa_gate {m.relative_to(ROOT)}",
             PY + [str(SCRIPTS / "qa_gate.py"), "check", str(m), str(m.parent / "verdicts")])

    step("strings.tsv", PY + [str(ROOT / "tools" / "strings_tsv.py")])
    step("cover", PY + [str(ROOT / "tools" / "cover.py")])
    step("textcover", PY + [str(SCRIPTS / "textcover.py"), str(ROOT / "work" / "qa" / "cover_now"),
                            str(ROOT / "build" / "strings.tsv"), "--mask", "0x1FFFFFF",
                            "--waive", str(ROOT / "docs" / "text_unshown.tsv")])

    def polish():
        left = [l for l in (ROOT / "docs" / "polish.md").read_text(encoding="utf8").splitlines()
                if re.match(r"\s*[-*] \[ \]", l)]
        return f"{len(left)} unticked lines, first: {left[0].strip()[:100]}" if left else None
    step("polish", ok=polish)

    orig = ORIG.read_bytes()
    base = hashes(orig)

    def readme():
        t = (ROOT / "README.md").read_text(encoding="utf8")
        ph = re.findall(r"<(?:Game title|platform|publisher|year|repo|file|size|sha1|game|ext)>|<[A-Z][^<>\n]*/[^<>\n]*>", t)
        if ph:
            return f"template placeholders left: {sorted(set(ph))}"
        if base["sha1"] not in t or base["crc32"] not in t:
            return "README.md lacks the base ROM SHA-1/CRC32"
    step("README", ok=readme)

    REL.mkdir(exist_ok=True)
    step("patch", PY + [str(ROOT / "tools" / "bps.py"), "make", str(ORIG), str(BUILD), str(out_bps)])

    def reapply():
        fresh = ORIG.read_bytes()
        if hashlib.sha1(fresh).hexdigest() != base["sha1"]:
            return "original changed while releasing"
        res = bps.apply(fresh, out_bps.read_bytes())
        return None if res == built else "re-applied patch differs from the build"
    step("re-apply and compare", ok=reapply)

    patched = hashes(built)
    tmpl = (ROOT / "docs" / "release_readme.txt").read_text(encoding="utf8")
    text = tmpl.format(version=a.version, date=date.today().isoformat(), patch=out_bps.name,
                       base_size=base["size"], base_crc32=base["crc32"], base_md5=base["md5"], base_sha1=base["sha1"],
                       out_size=patched["size"], out_crc32=patched["crc32"], out_sha1=patched["sha1"])
    print("== zip", flush=True)
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(out_bps, out_bps.name)
        z.writestr("README.txt", text.replace("\n", "\r\n"))
    with zipfile.ZipFile(out_zip) as z:
        names = sorted(z.namelist())
        if names != sorted([out_bps.name, "README.txt"]) or z.testzip() is not None:
            sys.exit(f"release: zip check failed: {names}")
    print(f"release ok: {out_zip.relative_to(ROOT)} ({out_zip.stat().st_size} bytes): {names}\n"
          f"  base   {base['size']} bytes  CRC32 {base['crc32']}  SHA-1 {base['sha1']}\n"
          f"  result {patched['size']} bytes  CRC32 {patched['crc32']}  SHA-1 {patched['sha1']}")


if __name__ == "__main__":
    main()
