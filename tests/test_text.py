"""Phase 4 extract: codec roundtrip, coverage against the original ROM, dump never clobbers English, apply hook."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import text  # noqa: E402


@pytest.mark.parametrize("raw", [
    "バトローラー　ジン！".encode("cp932"),
    b"\x82\xa0[\x00\xff\x81",           # literal '[', control byte, bad lead, lone lead at the end
    b"Hello \x0a\x82\xa0",
    b"\x81\xde\x81\x63",               # ∇ heart, ……
])
def test_codec_roundtrip(raw):
    assert text.encode(text.decode(raw)) == raw


def test_decode_marks_unknown_bytes():
    assert text.decode(b"\x82\xa0\xff") == "あ[FF]"
    assert text.decode(b"[") == "[5B]"


rom_needed = pytest.mark.skipif(not any((ROOT / "rom").glob("*.gba")), reason="no ROM dump in rom/")


@rom_needed
def test_roundtrip_and_coverage_against_original():
    """Every extracted string re-encodes to its bytes, script/ matches the ROM, no text run is left uncovered."""
    assert text.check() == []


@rom_needed
def test_dump_keeps_english(tmp_path, monkeypatch):
    monkeypatch.setattr(text, "SCRIPT", tmp_path)
    text.dump()
    rel = "events/e2485.json"
    rows = json.loads((tmp_path / rel).read_text(encoding="utf-8"))
    rows[0]["en"], rows[0]["status"], rows[0]["notes"] = "Hi!", "draft", "kept"
    rows[1]["en"], rows[1]["jp"] = "Stale", "old jp"
    (tmp_path / rel).write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    text.dump()
    again = json.loads((tmp_path / rel).read_text(encoding="utf-8"))
    assert (again[0]["en"], again[0]["status"], again[0]["notes"]) == ("Hi!", "draft", "kept")
    assert again[1]["en"] == "Stale" and again[1]["status"] == "jp-changed" and again[1]["jp"] != "old jp"


@rom_needed
def test_apply_events_rebuilds_lines_choices_and_titles(tmp_path, monkeypatch):
    import archive
    import events
    rom = archive.ROM.read_bytes()
    ar = archive.Archive(rom)
    monkeypatch.setattr(text, "SCRIPT", tmp_path)
    text.dump()
    # one line, one choice field and one title field get longer English
    picks = {}
    for i in (2479, 2485):
        rel = f"events/e{i}.json"
        rows = json.loads((tmp_path / rel).read_text(encoding="utf-8"))
        for kind in ("line", "choice", "title"):
            r = next((r for r in rows if r["kind"] == kind and r["id"] not in picks), None)
            if r:
                r["en"] = "ＥＮＧＬＩＳＨ　" + r["jp"]
                picks[r["id"]] = r["en"]
        (tmp_path / rel).write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    assert {k for k in ("line", "choice", "title")} <= {
        r["kind"] for i in (2479, 2485)
        for r in json.loads((tmp_path / f"events/e{i}.json").read_text(encoding="utf-8")) if r["en"]}
    evs = {i: events.parse(ar.file(i)) for i in (2479, 2485)}
    assert text.apply_events(evs) == len(picks)
    for i, ev in evs.items():
        again = events.parse(ev.build())          # the rebuilt file parses, links intact
        got = {e[0]: text.decode(e[2]) for e in text.event_entries(i, again)}
        n_old = len(text.event_entries(i, events.parse(ar.file(i))))
        assert len(got) == n_old
        for id_, en in picks.items():
            if id_.startswith(f"e{i}_"):
                # ids are original offsets, so look the value up by order instead
                assert en in got.values()
