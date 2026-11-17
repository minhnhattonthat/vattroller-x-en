"""gfx: graphics-text redraws change only the declared tiles and keep each label's arrow."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

if not any((ROOT / "rom").glob("*.gba")):
    pytest.skip("no ROM dump in rom/", allow_module_level=True)

import archive  # noqa: E402
import gfx  # noqa: E402


def test_446_changes_only_label_tiles():
    ar = archive.Archive()
    orig, new = ar.file(gfx.SHEET), gfx.files(ar)[gfx.SHEET]
    assert len(new) == len(orig)
    allowed = {t for first, count, _ in gfx.LABELS + gfx.PILLS for t in range(first, first + count)}
    allowed |= {n for blocks, _ in gfx.TALL_LABELS for n, _, _ in gfx.tall_tiles(blocks)}
    allowed |= {t for tiles, _ in gfx.SPLIT_LABELS for t in tiles}
    allowed |= {t for head in gfx.SHOP_HEADS for t in head[0]}
    allowed |= {t for row in gfx.SHOP_CANT[0] for t in row} | set(gfx.PAGE_LABEL[0]) | set(gfx.PAGE_LABEL[1])
    allowed |= {t for grid, _, _ in gfx.BUBBLES for row in grid for t in row if t is not None}
    changed = {i // 32 for i in range(len(orig)) if orig[i] != new[i]}
    assert changed and changed <= allowed


def test_bubbles_keep_icons_and_never_touch_the_shared_blank():
    ar = archive.Archive()
    orig, new = ar.file(gfx.SHEET), gfx.files(ar)[gfx.SHEET]
    assert new[313 * 32:314 * 32] == orig[313 * 32:314 * 32]      # blank green tile used by many sprites
    for grid, _, keep in gfx.BUBBLES:
        tiles = [t for row in grid for t in row if t is not None]
        assert any(new[t * 32:t * 32 + 32] != orig[t * 32:t * 32 + 32] for t in tiles)
        if keep and keep != "ink":
            y0, y1, x0, x1 = keep
            for y in range(y0, y1):
                t = grid[y // 8][0]
                assert gfx.tile_px(new, t)[y % 8][x0:min(x1, 8)] == gfx.tile_px(orig, t)[y % 8][x0:min(x1, 8)]


def test_677_redraws_every_map_label_and_keeps_pin_and_cursor():
    ar = archive.Archive()
    orig, new = ar.file(gfx.MAP_FILE), gfx.files(ar)[gfx.MAP_FILE]
    assert len(new) == len(orig)
    label = {n for blocks, _ in gfx.MAP_LABELS for n, _, _ in gfx.tall_tiles(blocks)}
    assert label == set(range(106)) | set(range(112, 116))     # 106-111 cursor, 116 pin: untouched
    changed = {i // 32 for i in range(len(orig)) if orig[i] != new[i]}
    assert changed and changed <= label
    assert {b for i in range(len(new)) if i // 32 in label for b in (new[i] & 15, new[i] >> 4)} <= {0, 1, 2}


def test_717_changes_only_the_vpon_message_sprites():
    ar = archive.Archive()
    orig, new = ar.file(gfx.VPON_FILE), gfx.files(ar)[gfx.VPON_FILE]
    assert len(new) == len(orig)
    changed = {i // 32 for i in range(len(orig)) if orig[i] != new[i]}
    assert changed and changed <= set(gfx.vpon_cells().values())
    assert set(range(640, 680)) <= set(gfx.vpon_cells().values())


def test_shop_heads_keep_their_box_border():
    ar = archive.Archive()
    orig, new = ar.file(gfx.SHEET), gfx.files(ar)[gfx.SHEET]
    for head in gfx.SHOP_HEADS:
        for t in head[0]:
            o, n = gfx.tile_px(orig, t), gfx.tile_px(new, t)
            assert o[7] == n[7]                                   # bottom border row kept
            assert all(v in (0, 0xD, 0xE, 9) for row in n for v in row)


def test_431_changes_only_box_and_status_tiles():
    ar = archive.Archive()
    orig, new = ar.file(gfx.SHEET_431), gfx.files(ar)[gfx.SHEET_431]
    assert len(new) == len(orig)
    allowed = {t for first, count, _ in gfx.BOXES_431 for t in range(first, first + count)}
    allowed |= {t for row in gfx.STATUS_431 + gfx.ARM_431 for t in row[0]} | {dst for _, dst in gfx.COPIES_431}
    allowed |= set(gfx.HEAD_431[0])
    changed = {i // 32 for i in range(len(orig)) if orig[i] != new[i]}
    assert changed and changed <= allowed
    assert new[117 * 32:118 * 32] == new[132 * 32:133 * 32]      # the two copies of the タ end tile stay equal
    corner = gfx.tile_px(orig, 143)
    assert [r[5:] for r in gfx.tile_px(new, 143)] == [r[5:] for r in corner]   # G17 head keeps its box corner


def test_434_changes_only_the_special_tab():
    ar = archive.Archive()
    orig, new = ar.file(gfx.SHEET_434), gfx.files(ar)[gfx.SHEET_434]
    assert len(new) == len(orig)
    allowed = {t for row in gfx.TAB_434 for t in row[0]}
    changed = {i // 32 for i in range(len(orig)) if orig[i] != new[i]}
    assert changed and changed <= allowed


def test_credit_outline_rule_reproduces_original():
    px = gfx.credit_px(archive.Archive().file(gfx.SHEET_452))
    assert gfx.credit_outline([[c == 1 for c in row] for row in px]) == px


def test_452_changes_only_credit_tiles_and_drops_kana():
    ar = archive.Archive()
    orig, new = ar.file(gfx.SHEET_452), gfx.files(ar)[gfx.SHEET_452]
    assert len(new) == len(orig)
    allowed = {f + k for f in gfx.CREDIT_ROWS for k in range(gfx.CREDIT_TILES)}
    changed = {i // 32 for i in range(len(orig)) if orig[i] != new[i]}
    assert changed and changed <= allowed
    ink = lambda px: sum(c == 1 for row in px for c in row)  # noqa: E731
    letters = sum(r.count("#") for ch in gfx.CREDIT_TEXT if ch != " " for r in gfx.CREDIT_GLYPHS[ch])
    keep = sum(1 for row in gfx.credit_px(orig) for lo, hi in gfx.CREDIT_KEEP for c in row[lo:hi] if c == 1)
    assert ink(gfx.credit_px(new)) == keep + letters


def test_433_changes_only_the_death_roll_spine():
    ar = archive.Archive()
    orig, new = ar.file(gfx.SHEET_433), gfx.files(ar)[gfx.SHEET_433]
    assert len(new) == len(orig)
    first = gfx.SPINE_FIRST
    changed = {i // 32 for i in range(len(orig)) if orig[i] != new[i]}
    assert changed and changed <= set(range(first, first + gfx.SPINE_W * gfx.SPINE_H))
    a, b = gfx.spine_px(orig), gfx.spine_px(new)
    assert a[:gfx.SPINE_ROWS[0]] == b[:gfx.SPINE_ROWS[0]] and a[gfx.SPINE_ROWS[1]:] == b[gfx.SPINE_ROWS[1]:]


def test_signs_change_only_their_tiles_inside_the_box():
    ar = archive.Archive()
    new = gfx.files(ar)
    for s in gfx.SIGNS:
        orig = ar.file(s["file"])
        tiles = {n for row in s["grid"] for n in row}
        changed = {i // 32 for i in range(len(orig)) if orig[i] != new[s["file"]][i]}
        assert changed and changed <= tiles, s["text"]
        a, b = gfx.sign_px(orig, s["grid"]), gfx.sign_px(new[s["file"]], s["grid"])
        x0, y0, x1, y1 = s["box"]
        assert all(a[y][x] == b[y][x] for y in range(len(a)) for x in range(len(a[0]))
                   if not (x0 <= x < x1 and y0 <= y < y1)), s["text"]


def test_441_changes_only_card_blocks_and_keeps_the_dots():
    ar = archive.Archive()
    orig, new = ar.file(gfx.CARD_FILE), gfx.files(ar)[gfx.CARD_FILE]
    assert len(new) == len(orig)
    allowed = {off + i for ln in gfx.CARD_LINES for off, w, h, _, _ in ln["front"] + ln["back"] + ln.get("blank", [])
               for i in range(w * h // 2)}
    changed = {i for i in range(len(orig)) if orig[i] != new[i]}
    assert changed and changed <= allowed
    for ln in gfx.CARD_LINES:
        if ln.get("clear"):
            continue
        for layer, dy in (("front", 0), ("back", ln["shadow"][1])):
            a, b = gfx.card_blocks(orig, ln[layer]), gfx.card_blocks(new, ln[layer])
            assert all(a[p] == b[p] for p in a if not ln["y0"] + dy <= p[1] < ln["y1"] + dy)


def test_every_rule_card_word_is_redrawn():
    import cardframes
    rom = (ROOT / "rom" / "Vattroller X (Japan).gba").read_bytes()
    assert len(cardframes.frames(rom)) == 26
    assert cardframes.uncovered(rom) == [0x680]     # one tile of the OFFICIAL block reused in a 1-frame slide-in
    assert {ln["text"] for ln in gfx.CARD_LINES} >= {"OFFICIAL", "SURVIVAL", "GRAB LOTS!!!", "KNOCK DOWN!!!",
                                                     "DRAIN HP!!!", "BEAT THE BOSS!"}


def test_labels_keep_their_arrow():
    ar = archive.Archive()
    orig, new = ar.file(gfx.SHEET), gfx.files(ar)[gfx.SHEET]
    for first, _, _ in gfx.LABELS:
        a, b = gfx.tile_px(orig, first), gfx.tile_px(new, first)
        assert all(a[y][x] == b[y][x] for y in range(8) for x in range(gfx.ARROW_W))


def test_tall_label_keeps_its_arrow_and_drops_the_kana_tail():
    ar = archive.Archive()
    orig, new = ar.file(gfx.SHEET), gfx.files(ar)[gfx.SHEET]
    for blocks, _ in gfx.TALL_LABELS:
        tiles = gfx.tall_tiles(blocks)
        first = tiles[0][0]
        cols = blocks[0][1]                       # the arrow: first ARROW_W columns of the first block's column 0
        for t in (first, first + cols):
            a, b = gfx.tile_px(orig, t), gfx.tile_px(new, t)
            assert all(a[y][x] == b[y][x] for y in range(8) for x in range(gfx.ARROW_W))
        tail = blocks[-1]                         # "Next" is short: the last block (すむ) ends up blank
        for n in range(tail[0], tail[0] + tail[1] * tail[2]):
            assert all(v == gfx.BG for row in gfx.tile_px(new, n) for v in row)
