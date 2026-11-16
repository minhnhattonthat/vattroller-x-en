"""text.py: extract the game's text to script/*.json and apply translations at build time (docs/re/text.md).

    python -X utf8 tools/text.py dump [--force]   # write script/*.json from the ORIGINAL ROM (never clobbers en)
    python -X utf8 tools/text.py stats            # entries and translation progress per file
    python -X utf8 tools/text.py check            # roundtrip + coverage against the original ROM (exit 1 on a gap)

Sources (ids are address-based and stable):
  e<file>_<off>[.k]  event text inside archive file <file> (2475-2711) at command offset <off> (hex, 5 digits).
                     kind line (op 0x00, one box line), choice (op 0x01 field k), title (op 0x13 field k).
  r<addr>            NUL-terminated string outside the archive reached by 4-aligned 0x08xxxxxx pointers (ptrs).
                     A string that starts inside another one (shared tail) has `inside` = the containing id.
  c<addr>            ending-credits record (fixed 0x2C-byte records at 0x74570, no pointers; text slot 0x28 bytes).
  n<addr>            string with no pointer found (in place only; max = original byte length).

Text codec: Shift-JIS (cp932) per character; a byte that does not decode (or a literal '[') is written [XX].
`dump` on an existing file keeps en/status/notes per id and refreshes jp; it reports ids whose jp changed while
they already had an English line."""
import json
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import archive  # noqa: E402
import events  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "script"
LANG = "en"

CREDITS, CREDITS_END, CREDIT_REC, CREDIT_SLOT = 0x74570, 0x75E30, 0x2C, 0x28
# Strings found with no pointer (sweep in check_coverage); reached by code base+offset or unused. In place only.
NOPTR = [0x0F0A0C, 0x0F0F2C, 0x0F0F44, 0x0F0F54, 0x0F0FE0, 0x0F0FEC, 0x0F1000, 0x0F1014, 0x0F1018,
         0x0F1684, 0x0F16E8]

TOKEN = re.compile(r"\[([0-9A-Fa-f]{2})\]")


# ---------------------------------------------------------------- codec
def decode(raw: bytes) -> str:
    out, i = [], 0
    while i < len(raw):
        c = raw[i]
        n = 2 if (0x81 <= c <= 0x9F or 0xE0 <= c <= 0xFC) and i + 1 < len(raw) else 1
        ch = None
        try:
            ch = raw[i:i + n].decode("cp932")
            if n == 2 and ch.encode("cp932") != raw[i:i + 2]:
                # a duplicate code (IBM ext. 桒 = FA E3 re-encodes as ED 93): keep both bytes
                out.append(f"[{raw[i]:02X}][{raw[i + 1]:02X}]")
                i += 2
                continue
            if ch.encode("cp932") != raw[i:i + n] or ch == "[" or (n == 1 and c < 0x20 and c != 0x0A) \
                    or "" <= ch <= "":  # cp932 maps 0x80/0xA0/0xFD-0xFF and user codes to the PUA
                ch = None
        except UnicodeDecodeError:
            pass
        if ch is None:
            out.append(f"[{c:02X}]")
            i += 1
        else:
            out.append(ch)
            i += n
    return "".join(out)


def encode(s: str) -> bytes:
    out, pos = bytearray(), 0
    for m in TOKEN.finditer(s):
        out += s[pos:m.start()].encode("cp932")
        out.append(int(m.group(1), 16))
        pos = m.end()
    out += s[pos:].encode("cp932")
    return bytes(out)


def is_sjis_pair(d, i):
    return (0x81 <= d[i] <= 0x9F or 0xE0 <= d[i] <= 0xEF) and i + 1 < len(d) and 0x40 <= d[i + 1] <= 0xFC \
        and d[i + 1] != 0x7F


def cstr(d, o, end=None):
    e = d.index(0, o)
    return bytes(d[o:e])


# ---------------------------------------------------------------- event text
def event_entries(i, ev):
    """(id, kind, raw, extra) for every text field of a parsed event file."""
    out = []
    for si, sc in enumerate(ev.scripts()):
        for n in sc.nodes:
            if len(n.data) < 8:
                continue
            p = sc.node_pos(n)
            base = f"e{i}_{p:05x}"
            if n.op == events.OP_TEXT:
                out.append((base, "line", n.text, {"flags": f"{events.u16(n.data, 4):#06x}", "script": si}))
            elif n.op in events.FIELD_OPS:
                kind = "choice" if n.op == events.OP_CHOICE else "title"
                for k, raw in enumerate(n.fields):
                    if raw:
                        out.append((f"{base}.{k}", kind, raw, {"script": si}))
    return out


# ---------------------------------------------------------------- ROM strings
def in_archive(o):
    return archive.TABLE <= o < archive.DATA_END


def string_end(d, t):
    """End (NUL offset) of a text-like string at t, or None: SJIS pairs, printable ASCII and newlines, >= 1 SJIS."""
    i, sj = t, 0
    while i < len(d):
        c = d[i]
        if c == 0:
            return i if sj else None
        if is_sjis_pair(d, i):
            try:
                d[i:i + 2].decode("cp932")
            except UnicodeDecodeError:
                return None
            i, sj = i + 2, sj + 1
        elif 0x20 <= c < 0x7F or c == 0x0A:
            i += 1
        else:
            return None
    return None


def pointered_strings(d):
    """{target: (end, [pointer offsets], inside)} for strings outside the archive with 4-aligned pointers."""
    ptrs = {}
    for o in range(0, len(d) - 3, 4):
        if in_archive(o) and not (archive.TABLE <= o < archive.DATA_START):
            continue  # inside archive files: event files hold no absolute pointers (script.md); others are data
        v = struct.unpack_from("<I", d, o)[0]
        t = v - 0x08000000
        if 0 <= t < len(d) and not in_archive(t):
            ptrs.setdefault(t, []).append(o)
    cand = {}
    for t, ps in ptrs.items():
        e = string_end(d, t)
        if e is not None:
            cand[t] = (e, ps)
    # a string starts where no SJIS character ends (after a NUL or other data), or inside another accepted string
    # (shared tail). Pointer-like values into the middle of a kanji list (0x3C0) are not strings.
    # Without a NUL before it, the target must also be even, start with a SJIS character and hold >= 2 of them:
    # odd values are Thumb code pointers, and short hits are constants.
    def head(t, e):
        if d[t - 1] == 0:
            return True
        return not is_sjis_pair(d, t - 2) and t % 2 == 0 and is_sjis_pair(d, t) and \
            sum(1 for _ in re.finditer(rb"[\x81-\x9f\xe0-\xef][\x40-\xfc]", bytes(d[t:e]))) >= 2
    heads = {t: v for t, v in cand.items() if t > 1 and head(t, v[0])}
    starts = sorted(heads)
    out = {t: (e, ps, None) for t, (e, ps) in heads.items()}
    import bisect
    for t, (e, ps) in cand.items():
        if t in heads:
            continue
        k = bisect.bisect_right(starts, t) - 1
        if k >= 0 and starts[k] < t and heads[starts[k]][0] == e:
            out[t] = (e, ps, starts[k])
    return out


# Pointered "strings" that are not text: kind "data", never translated or written.
DATA = [
    (0x0003C0, 0x000880, "JIS-ordered kanji list searched by code (font / name-entry index), not a string"),
    (0x000CC0, 0x000CD8, "digit table ０-９: code indexes it by number*2; fixed width, phase 5 decides"),
    (0x007890, 0x007894, "bytes of the pointer 0x08008C90, not text"),
    (0x02FDF9, 0x02FDFC, "code bytes"),
    (0x048979, 0x04897D, "code bytes"),
    (0x0E21D8, 0x0E21DA, "name marker ∴: the typer (0x080735C0) compares each text code with it, keep as is"),
    (0x0F1828, 0x0F182A, "name marker ∴ (second copy), keep as is"),
]


def data_reason(t):
    return next((why for a, b, why in DATA if a <= t < b), None)


def rom_entries(d):
    out = []
    for t, (e, ps, inside) in sorted(pointered_strings(d).items()):
        extra = {"ptrs": [f"{p:#x}" for p in ps]}
        if inside is not None:
            extra["inside"] = f"r{inside:06x}"
        why = data_reason(t)
        if why:
            extra["notes"] = why
        out.append((f"r{t:06x}", "data" if why else "string", bytes(d[t:e]), extra))
    return out


def credit_entries(d):
    out = []
    for o in range(CREDITS, CREDITS_END, CREDIT_REC):
        raw = cstr(d, o)
        if raw:
            out.append((f"c{o:06x}", "credit", raw, {"max": CREDIT_SLOT - 1,
                                                       "attr": d[o + CREDIT_SLOT:o + CREDIT_REC].hex()}))
    return out


def noptr_entries(d):
    return [(f"n{o:06x}", "noptr", cstr(d, o), {"max": len(cstr(d, o))}) for o in NOPTR]


# ---------------------------------------------------------------- files
def all_sources(rom=None):
    """{json path relative to script/: [(id, kind, raw, extra)]} from the original ROM."""
    d = rom if rom is not None else archive.ROM.read_bytes()
    ar = archive.Archive(d)
    files = {}
    for i in range(events.FIRST, events.LAST + 1):
        files[f"events/e{i}.json"] = event_entries(i, events.parse(ar.file(i)))
    for ent in rom_entries(d):
        addr = int(ent[0][1:], 16)
        files.setdefault(f"rom/r{addr >> 16:02x}.json", []).append(ent)
    files["rom/credits.json"] = credit_entries(d)
    files["rom/noptr.json"] = noptr_entries(d)
    return files


def to_rows(ents):
    rows = []
    for id_, kind, raw, extra in ents:
        r = {"id": id_, "kind": kind, "jp": decode(raw), LANG: "", "status": "data" if kind == "data" else "new"}
        r.update(extra)
        r.setdefault("notes", "")
        rows.append(r)
    return rows


def load(rel):
    return json.loads((SCRIPT / rel).read_text(encoding="utf-8"))


def save(rel, rows):
    p = SCRIPT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def dump(force=False):
    changed_jp, wrote = [], 0
    for rel, ents in all_sources().items():
        rows = to_rows(ents)
        p = SCRIPT / rel
        if p.exists():
            old = {r["id"]: r for r in load(rel)}
            for r in rows:
                o = old.get(r["id"])
                if not o:
                    continue
                r[LANG] = o.get(LANG, "")
                if o.get("status") not in (None, "new", "data"):
                    r["status"] = o["status"]
                if o.get("notes"):
                    r["notes"] = o["notes"]
                if o.get(LANG) and o["jp"] != r["jp"]:
                    changed_jp.append(r["id"])
                    r["status"] = "jp-changed"
            lost = [k for k, o in old.items() if o.get(LANG) and k not in {r["id"] for r in rows}]
            if lost and not force:
                sys.exit(f"{rel}: ids with English would disappear: {lost[:10]} (use --force)")
        save(rel, rows)
        wrote += 1
    print(f"wrote {wrote} files under script/")
    if changed_jp:
        print(f"jp changed under an existing translation ({len(changed_jp)}), status set to jp-changed:",
              changed_jp[:20])


def iter_rows():
    for p in sorted(SCRIPT.rglob("*.json")):
        rel = p.relative_to(SCRIPT).as_posix()
        for r in load(rel):
            yield rel, r


# ---------------------------------------------------------------- build hook
def apply_events(evs, enc=encode, by_id=None):
    """Put text into the parsed event files: by_id {id: text}, default every non-empty `en` of script/events.
    Returns the count applied."""
    if by_id is None:
        by_id = {r["id"]: r[LANG] for rel, r in iter_rows() if rel.startswith("events/") and r.get(LANG)}
    n = 0
    for i, ev in evs.items():
        for sc in ev.scripts():
            for node in sc.nodes:
                if len(node.data) < 8:
                    continue
                base = f"e{i}_{sc.node_pos(node):05x}"
                if node.op == events.OP_TEXT and base in by_id:
                    node.set_text(enc(by_id[base]))
                    n += 1
                elif node.op in events.FIELD_OPS:
                    fs = node.fields
                    new = [enc(by_id[f"{base}.{k}"]) if f"{base}.{k}" in by_id else raw for k, raw in enumerate(fs)]
                    if new != fs:
                        node.set_fields(new)
                        n += 1
    return n


# ---------------------------------------------------------------- checks
def text_runs(d, lo, hi):
    """SJIS runs in d[lo:hi] that look like text: >= 2 SJIS chars and either a kana in them or NUL on both sides."""
    i = lo
    while i < hi - 1:
        if not is_sjis_pair(d, i):
            i += 1
            continue
        j, n, kana, last = i, 0, 0, i
        while j < hi:
            if j < hi - 1 and is_sjis_pair(d, j):
                if d[j] == 0x82 and 0x9F <= d[j + 1] <= 0xF1 or d[j] == 0x83 and 0x40 <= d[j + 1] <= 0x96:
                    kana += 1
                j, n = j + 2, n + 1
                last = j
            elif 0x20 <= d[j] < 0x7F:
                j += 1
            else:
                break
        j = last  # trailing ASCII is not part of the run
        if n >= 2 and (kana or (d[i - 1] == 0 and j < hi and d[j] == 0)):
            yield i, j
        i = j


def load_waive():
    """script/waive.tsv: `start<TAB>end<TAB>reason` ranges (hex) where SJIS-looking runs are known non-text."""
    out = []
    p = SCRIPT / "waive.tsv"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#"):
                a, b, why = line.split("\t", 2)
                out.append((int(a, 16), int(b, 16), why))
    return out


def check(rom=None):
    """Roundtrip and coverage against the original ROM. Returns a list of problems."""
    d = rom if rom is not None else archive.ROM.read_bytes()
    ar = archive.Archive(d)
    probs = []
    srcs = all_sources(d)
    # roundtrip: every extracted raw string re-encodes from its decoded form
    for rel, ents in srcs.items():
        for id_, _, raw, _ in ents:
            if encode(decode(raw)) != raw:
                probs.append(f"roundtrip {id_}")
    # field layout: op 0x01 / 0x13 rebuild from their own fields
    evs = {i: events.parse(ar.file(i)) for i in range(events.FIRST, events.LAST + 1)}
    for i, ev in evs.items():
        for sc in ev.scripts():
            for n in sc.nodes:
                if n.op in events.FIELD_OPS and len(n.data) >= 8 and n.layout_fields(n.fields) != n.data:
                    probs.append(f"field layout e{i}_{sc.node_pos(n):05x}")
    # json on disk matches the ROM (jp fields current)
    on_disk = {}
    for rel, r in iter_rows():
        on_disk[r["id"]] = r
    for rel, ents in srcs.items():
        for id_, _, raw, _ in ents:
            r = on_disk.get(id_)
            if r is None:
                probs.append(f"missing in script/{rel}: {id_}")
            elif encode(r["jp"]) != raw:
                probs.append(f"jp differs from ROM: {id_}")
    # coverage, event files: every SJIS-looking run lies inside an extracted field
    for i, ev in evs.items():
        b = ar.file(i)
        spans = []
        for sc in ev.scripts():
            for n in sc.nodes:
                p = sc.node_pos(n)
                if n.op == events.OP_TEXT and len(n.data) >= 8:
                    spans.append((p + 8, p + 8 + len(n.text)))
                elif n.op in events.FIELD_OPS and len(n.data) >= 8:
                    for o, raw in zip(n.field_offsets(), n.fields):
                        spans.append((p + o, p + o + len(raw)))
        for s, e in text_runs(b, 1, len(b)):
            if not any(a <= s and e <= z for a, z in spans):
                probs.append(f"uncovered event text e{i} +{s:#x}: {decode(b[s:e])[:30]}")
    # coverage, ROM outside the archive
    spans = []
    for rel, ents in srcs.items():
        if rel.startswith("rom/"):
            for id_, _, raw, _ in ents:
                a = int(id_[1:], 16)
                spans.append((a, a + len(raw)))
    spans.sort()
    import bisect
    starts = [a for a, _ in spans]
    waive = load_waive()
    for lo, hi in ((0, archive.TABLE), (archive.DATA_END, len(d))):
        for s, e in text_runs(d, lo, hi):
            k = bisect.bisect_right(starts, s) - 1
            if k >= 0 and spans[k][0] <= s and e <= spans[k][1]:
                continue
            if any(a <= s < b for a, b, _ in waive):
                continue
            probs.append(f"uncovered ROM text {s:#08x}: {decode(d[s:e])[:30]}")
    return probs


def stats():
    tot = {}
    for rel, r in iter_rows():
        top = rel.split("/")[0] + "/" + (rel.split("/")[1] if rel.startswith("rom/") else "*")
        t = tot.setdefault(top, [0, 0])
        t[0] += 1
        t[1] += bool(r.get(LANG))
    for k, (n, done) in sorted(tot.items()):
        print(f"{k:24s} {n:6d} entries, {done:6d} translated")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"
    if cmd == "dump":
        dump("--force" in sys.argv)
    elif cmd == "check":
        probs = check()
        for p in probs[:200]:
            print(p)
        print(f"{len(probs)} problems")
        sys.exit(1 if probs else 0)
    else:
        stats()


if __name__ == "__main__":
    main()
