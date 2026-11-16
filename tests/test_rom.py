import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))


def test_rom_sha1_matches():
    if not (ROOT / "rom").is_dir() or not any((ROOT / "rom").glob("*.gba")):
        pytest.skip("no ROM dump in rom/ (clone without the game)")
    import check_rom
    check_rom.check()


def test_skill_path_module_imports():
    import skill
    assert skill.SKILL
