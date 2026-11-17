"""helpbub.py: the SELECT ▶Help bubbles (G14). They are sprites built from archive #437 (raw 4bpp OBJ tiles): an
animation set at ROM 0x271E60 = {u32 ROM address of #437, u16 71, u16 71, u32 ptr to the frame table, u32 ?}; the
frame table at 0x271E70 holds 71 entries of 12 bytes {u16 0, u16 count, u32 0, u32 ROM ptr to records}; a record is 6 x u16
{shape, size, palette, #437 byte offset, y, x}: shape 0x1000 square / 0x5000 wide / 0x9000 tall (OAM attr0 bits
14-15 plus bit 12), size = OAM attr1 bits 14-15 (+ 0x1000 h-flip, 0x2000 v-flip), palette 0xF000 = OBJ palette 15,
x/y signed 9/8-bit offsets from the bubble centre. The help bubble rows: 9 background, 5 border, 1 ink.

    python -X utf8 tools/helpbub.py --render work/gfx/help    # each frame as PNG (original ROM) + frames.tsv
"""
import argparse
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import archive  # noqa: E402

FILE = 437
ANIM = 0x271E60
FRAMES = 0x271E70
NFRAMES = 71
SIZES = {  # (shape bits 14-15, size bits 14-15) -> (w, h)
    (0, 0): (8, 8), (0, 1): (16, 16), (0, 2): (32, 32), (0, 3): (64, 64),
    (1, 0): (16, 8), (1, 1): (32, 8), (1, 2): (32, 16), (1, 3): (64, 32),
    (2, 0): (8, 16), (2, 1): (8, 32), (2, 2): (16, 32), (2, 3): (32, 64),
}
# OBJ palette 15 on the Armalet Data help (work/qa/warp/arm_sel dump), BGR555 -> RGB
PAL = [0x0000, 0x7FFF, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000,
       0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000]


def s9(v):
    v &= 0x1FF
    return v - 0x200 if v & 0x100 else v


def s8(v):
    v &= 0xFF
    return v - 0x100 if v & 0x80 else v


def frames(rom):
    out = []
    for k in range(NFRAMES):
        _, n, _, p = struct.unpack_from("<HHII", rom, FRAMES + 12 * k)
        recs = [struct.unpack_from("<6H", rom, p - 0x08000000 + 12 * r) for r in range(n)]
        out.append((p - 0x08000000, recs))
    return out


def wh(rec):
    return SIZES[(rec[0] >> 14 & 3, rec[1] >> 14 & 3)]


def tile_px(data, n):
    t = data[n * 32:n * 32 + 32]
    return [[(t[y * 4 + x // 2] >> 4 * (x & 1)) & 15 for x in range(8)] for y in range(8)]


def compose(data, recs):
    """{(x, y): colour} of one frame, later records under earlier ones (OAM order: lower index on top)."""
    px = {}
    for rec in reversed(recs):
        _, size, _, off, y0, x0 = rec
        w, h = wh(rec)
        hf, vf = size & 0x1000, size & 0x2000
        x0, y0 = s9(x0), s8(y0)
        for ty in range(h // 8):
            for tx in range(w // 8):
                t = tile_px(data, off // 32 + ty * (w // 8) + tx)
                for y in range(8):
                    for x in range(8):
                        c = t[y][x]
                        if not c:
                            continue
                        X, Y = tx * 8 + x, ty * 8 + y
                        if hf:
                            X = w - 1 - X
                        if vf:
                            Y = h - 1 - Y
                        px[(x0 + X, y0 + Y)] = c
    return px


def render(px, zoom=3):
    from PIL import Image
    shades = {0: (255, 0, 255), 1: (250, 250, 250), 5: (20, 20, 20), 9: (60, 110, 40)}
    xs = [x for x, _ in px] or [0]
    ys = [y for _, y in px] or [0]
    x0, y0 = min(xs), min(ys)
    im = Image.new("RGB", (max(xs) - x0 + 1, max(ys) - y0 + 1), (255, 0, 255))
    for (x, y), c in px.items():
        im.putpixel((x - x0, y - y0), shades.get(c, (128 + 8 * c, 0, 0)))
    return im.resize((im.width * zoom, im.height * zoom))


# English, one entry per frame (index = frame), "/" = new line. Glossary terms: Arm types (Blade ... Reeve),
# Arm Set, Box, Tool, V Skill, aura, Heal Roll, Attack Roll, Character Data / Armalet Data (menu page names).
TYPES = ["Blade", "Ex-Blade", "Strike", "Ex-Strike", "Hunt", "Ex-Hunt", "Bounder", "Ex-Bounder", "Assist"]
TEXT = [
    "L: previous page/R: next page",            # 0  Lで ひとつまえの ページ / Rで つぎの ページ
    "Size you can/fill with Arms",              # 1  アームが セットできる / サイズ
    "Armalet's traits",                         # 2  アーマレットの とくちょう
    "Armalet's name",                           # 3  アーマレットの なまえ
    "Character's HP",                           # 4  キャラクターの たいりょく
    "Character's aura",                         # 5  キャラクターの オーラ
    "Character's EXP",                          # 6  キャラクターの けいけんち
    "Character's level",                        # 7  キャラクターの レベル
    "A word that can/appear in Arm names",      # 8  アームの なまえに / つくことがある ことば
    "HP/(health)",                              # 9  HP / (たいりょく)
    "AP/(aura)",                                # 10 AP / (オーラ)
    "Attack/Power to cut/the foe's HP",         # 11 こうげき / あいての HPを / へらす ちから
    "Aura attack/Power to cut/the foe's AP",    # 12 A(オーラ)こうげき / あいての APを / へらす ちから
    "AP cost/(AP used)",                        # 13 APしょうひ / (APのしょうひ)
    "Speed/(how fast you move)",                # 14 スピード / (いどうの はやさ)
    "Critical hit/Power to sometimes/deal big damage",   # 15 クリティカルヒット / まれに だいダメージを / あたえる ちから
    "Bounder/Power to/deflect Rolls",           # 16 バウンダー / ロールを / はじく ちから
    "Bounder shot reflect/Power to reflect/projectiles",  # 17 バウンダー たまはんしゃ / とびどうぐを はんしゃする / ちから
    "Shot/Power to fire/projectiles",           # 18 たまはっしゃ / とびどうぐを はっしゃする / ちから
    "Homing shot/Power to chase/the foe",       # 19 ホーミングだん / あいてを おいかける / ちから
    "Shot bounce/Power to make shots/bounce off walls",   # 20 たまはんしゃ / とびどうぐが かべに / はんしゃする ちから
    "Piercing shot/Power to make shots/pierce the foe",   # 21 たまかんつう / とびどうぐが あいてに / かんつうする ちから
    "V Skills you have/ever learned",           # 22 おぼえたことのある / Vスキルリスト
    "Details",                                  # 23 せつめい ("Description" is 7 tiles, the original 6)
] + [f"Can set/{t} type/Arms" for t in TYPES] + [     # 24-32 ○○けいの / アームが / セットかのう
    "Special move of/the equipped Arm",         # 33 そうびしている アームの / ひっさつわざ
    "START: switch/the info shown",             # 34 STARTで / じょうほうの きりかえが / かのう
    "Size you can/fill with Arms",              # 35 = 1
    "Heal Roll recovery/How fast a/Heal Roll heals",      # 36 ヒールロール かいふく / ヒールロールの / ふっきの はやさ
    "AP recovery/How fast/AP comes back",       # 37 APかいふく / APの かいふくの / はやさ
    "Normal state",                             # 38 きほんの じょうたい
    "Attack Roll state",                        # 39 アタックロールの じょうたい
    "Normal attack",                            # 40 つうじょう こうげき
    "Each Arm's/signature attack",              # 41 アームごとの / とくちょうのある こうげき
    "Charge attack",                            # 42 ためこうげき
    "Size left/of total size",                  # 43 のこりサイズ / ぜんたいサイズ (a fraction)
    "Size",                                     # 44 サイズ
    "Name",                                     # 45 なまえ
    "Arm types",                                # 46 アームけいとう
    "Arms you can set",                         # 47 アームが セットかのう
    "Tools you can set",                        # 48 ツールが セットかのう
    "Special move input",                       # 49 ひっさつわざの コマンド
    "Go to/Box",                                # 50 ボックスへ / いどう
    "Go to/Arm Set",                            # 51 アームセットへ / いどう
    "Arm types/you can equip",                  # 52 そうびできる / アームの けいとう
    "Arms you have/ever owned",                 # 53 てにいれたことのある / アームリスト
    "Tools you have/ever owned",                # 54 てにいれたことのある / ツールリスト
    "Characters you/have met",                  # 55 であったことのある / キャラクターリスト
    "V Skills/you know",                        # 56 おぼえている / Vスキルリスト
    "Go to/Character Data",                     # 57 キャラクターデータへ / いどう
    "Go to/Armalet Data",                       # 58 アーマレットデータへ / いどう
] + [f"{t} type" for t in TYPES] + [            # 59-67 ○○けい
    "Reeve type",                               # 68 リーブけい
    "Tool",                                     # 69 ツール
    "Can set/Reeve type/Arms",                  # 70 リーブけいの / アームが / セットかのう
]
BG, FILL, OUTLINE = 9, 1, 5
ADV, SPACE, PAD = 4, 3, 4      # font3 advance, word space, green margin left/right of the text ink (outline incl.)
# (shape, size) of each sprite (w, h) the slicer uses
SHAPE = {(8, 8): (0x1000, 0), (16, 8): (0x5000, 0), (32, 8): (0x5000, 0x4000),
         (8, 16): (0x9000, 0), (16, 16): (0x1000, 0x4000), (32, 16): (0x5000, 0x8000)}


def text_w(line):
    return sum(SPACE if c == " " else ADV for c in line) - 1


def bubble(text, glyphs):
    """Pixel rows of one English bubble: green body with clipped corners, white letters with a black outline."""
    lines = text.split("/")
    w = (max(text_w(ln) for ln in lines) + 2 * PAD + 7) // 8 * 8
    h = 8 * len(lines)
    px = [[BG] * w for _ in range(h)]
    for y in (0, h - 1):
        px[y][0] = px[y][w - 1] = 0
    ink = set()
    for k, ln in enumerate(lines):
        x = (w - text_w(ln)) // 2
        for ch in ln:
            if ch == " ":
                x += SPACE
                continue
            for gy, row in enumerate(glyphs[ch]):
                for gx, c in enumerate(row):
                    if c == "#":
                        ink.add((8 * k + 1 + gy, x + gx))
            x += ADV
    for y, x in ink:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if 0 <= y + dy < h and 0 <= x + dx < w and (y + dy, x + dx) not in ink:
                    px[y + dy][x + dx] = OUTLINE
    for y, x in ink:
        px[y][x] = FILL
    return px


def slices(w, h):
    """Sprites (x, y, sw, sh) covering a w x h bubble: 16 px bands, then an 8 px band; 32/16/8 px pieces."""
    out, y = [], 0
    while y < h:
        sh = 16 if h - y >= 16 else 8
        x = 0
        while x < w:
            sw = 32 if w - x >= 32 else 16 if w - x >= 16 else 8
            out.append((x, y, sw, sh))
            x += sw
        y += sh
    return out


def bbox(recs):
    xs, ys = [], []
    for r in recs:
        w, h = wh(r)
        xs += [s9(r[5]), s9(r[5]) + w]
        ys += [s8(r[4]), s8(r[4]) + h]
    return min(xs), min(ys), max(xs), max(ys)


def build(orig_data, rom):
    """(new #437 bytes = English tiles then every frame's records, [(frame, records offset in the file, count)])."""
    import tagfont
    glyphs = tagfont.load_font3()
    tiles = bytearray()
    blocks = {}
    lists = []
    for k, (_, recs) in enumerate(frames(rom)):
        px = bubble(TEXT[k], glyphs)
        h, w = len(px), len(px[0])
        x0, y0, x1, y1 = bbox(recs)
        cx, cy = (x0 + x1) // 2 - w // 2, (y0 + y1) // 2 - h // 2
        new = []
        for sx, sy, sw, sh in slices(w, h):
            blk = bytes(px[sy + ty * 8 + y][sx + tx * 8 + i] | px[sy + ty * 8 + y][sx + tx * 8 + i + 1] << 4
                        for ty in range(sh // 8) for tx in range(sw // 8) for y in range(8) for i in range(0, 8, 2))
            if blk not in blocks:
                blocks[blk] = len(tiles)
                tiles += blk
            shape, size = SHAPE[(sw, sh)]
            new.append((shape, size, 0xF000, blocks[blk], (cy + sy) & 0xFF, (cx + sx) & 0x1FF))
        lists.append(new)
    assert len(tiles) <= 0x10000, f"{len(tiles):#x} bytes of tiles: offsets are u16"
    out = bytearray(tiles)
    where = []
    for k, new in enumerate(lists):
        where.append((k, len(out), len(new)))
        out += b"".join(struct.pack("<6H", *r) for r in new)
    return bytes(out), where


def budget(rom, data):
    """Per frame: (orig sprites, orig tiles, new sprites, new tiles, orig width, new width)."""
    old = frames(rom)
    rows = []
    for k, (_, recs) in enumerate(old):
        new = [r for r in _new_lists(rom)[k]]
        rows.append((len(recs), sum(wh(r)[0] * wh(r)[1] // 64 for r in recs),
                     len(new), sum(wh(r)[0] * wh(r)[1] // 64 for r in new),
                     bbox(recs)[2] - bbox(recs)[0], bbox(new)[2] - bbox(new)[0]))
    return rows


_cache = {}


def _new_lists(rom):
    if "lists" not in _cache:
        data, where = build(None, rom)
        _cache["lists"] = [[struct.unpack_from("<6H", data, off + 12 * i) for i in range(n)] for _, off, n in where]
    return _cache["lists"]


def files(ar):
    return {FILE: build(ar.file(FILE), ar.rom)[0]}


def patch(out, log, rom):
    """After archive.write_files: point the animation set at the new #437 and each frame at its new records."""
    base = struct.unpack_from("<I", out, archive.TABLE + 8 * FILE)[0]
    _, where = build(None, rom)
    struct.pack_into("<I", out, ANIM, base)
    log.append((ANIM, ANIM + 4, "helpbub: sheet ptr"))
    for k, off, n in where:
        struct.pack_into("<HHII", out, FRAMES + 12 * k, 0, n, 0, base + off)
    log.append((FRAMES, FRAMES + 12 * NFRAMES, "helpbub: frame table"))


def regions():
    return {(ANIM, ANIM + 4), (FRAMES, FRAMES + 12 * NFRAMES)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render")
    ap.add_argument("--english", help="render the English frames as sheets into this directory")
    ap.add_argument("--budget", action="store_true")
    ap.add_argument("--rom", default=str(archive.ROM))
    a = ap.parse_args()
    rom = Path(a.rom).read_bytes()
    data = archive.Archive(rom).file(FILE)
    if a.budget:
        for k, r in enumerate(budget(rom, data)):
            flag = " OVER" if r[3] > r[1] or r[2] > r[0] or r[5] > r[4] else ""
            print(f"{k:2d} sprites {r[0]:2d}->{r[2]:2d} tiles {r[1]:3d}->{r[3]:3d} width {r[4]:3d}->{r[5]:3d}{flag}"
                  f"  {TEXT[k]}")
    if a.english:
        new, where = build(data, rom)
        out = Path(a.english)
        out.mkdir(parents=True, exist_ok=True)
        frs = [(off, [struct.unpack_from("<6H", new, off + 12 * i) for i in range(n)]) for _, off, n in where]
        sheets(new, frs, out)
        print(f"{len(new):#x} bytes -> {out}")
    if a.render:
        out = Path(a.render)
        out.mkdir(parents=True, exist_ok=True)
        rows = []
        for k, (p, recs) in enumerate(frames(rom)):
            px = compose(data, recs)
            render(px).save(out / f"f{k:02d}.png")
            rows.append(f"{k}\t{p:#x}\t{len(recs)}\t" + " ".join(
                f"{wh(r)[0]}x{wh(r)[1]}@{s9(r[5])},{s8(r[4])}:{r[3]:#x}{'h' if r[1] & 0x1000 else ''}" for r in recs))
        (out / "frames.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")
        sheets(data, frames(rom), out)
        print(f"{len(rows)} frames -> {out}")


def sheets(data, frs, out, per=24, zoom=2):
    """Pages of frames, two columns, each frame labelled with its index (frames taller than 40 px are cut)."""
    from PIL import Image, ImageDraw
    for page in range(0, len(frs), per):
        ims = []
        for k in range(page, min(page + per, len(frs))):
            im = render(compose(data, frs[k][1]), zoom)
            ims.append((k, im.crop((0, 0, im.width, min(im.height, 40 * zoom)))))
        rows = (len(ims) + 1) // 2
        cw = 30 + max(im.width for _, im in ims)
        rh = 4 + max(im.height for _, im in ims)
        sh = Image.new("RGB", (2 * cw, rows * rh), (40, 0, 40))
        dr = ImageDraw.Draw(sh)
        for i, (k, im) in enumerate(ims):
            x, y = (i % 2) * cw, (i // 2) * rh
            dr.text((x + 2, y + 2), str(k), fill=(255, 255, 0))
            sh.paste(im, (x + 28, y))
        sh.save(out / f"sheet{page // per}.png")


if __name__ == "__main__":
    main()
