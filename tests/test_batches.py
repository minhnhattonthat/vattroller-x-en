"""tools/batches.py: the honorific rule (D1, translation reference §Validation and merge)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import batches  # noqa: E402


def probe(jp, en):
    return [p for p in batches.problems({"id": "review_probe", "jp": jp, "max": 36}, en, []) if "honorific" in p]


def test_dropped_honorific_fails():
    assert probe("コマチさん", "Komachi")
    assert probe("タクミくん　まって", "Wait, Takumi!")
    assert probe("∴ちゃんが１位ね", "∴ is in 1st place.")
    assert probe("トータさまだぞ", "It's the great Totta!")


def test_kept_honorific_passes():
    assert not probe("コマチさん", "Komachi-san")
    assert not probe("タクミくん　まって", "Wait, Takumi-kun!")
    assert not probe("∴ちゃんが１位ね", "∴-chan is in 1st place.")
    assert not probe("トータさまだぞ", "It's Totta-sama!")


def test_common_nouns_are_not_names():
    assert not probe("おじさん　こんにちは", "Hello, mister.")
    assert not probe("おかあさん", "Mom")
