import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import cover  # noqa: E402


def test_halfword_runs_end_on_the_nul_only_in_the_right_rom():
    base = cover.RELOC
    # "Rule Select \0" + 0xFF fill, then "Small \0": the text loop reads halfwords up to the one holding the NUL
    right = bytearray(b"\xff" * base) + b"Rule Select \x00\xff\xff\xffSmall \x00\xff"
    wrong = bytearray(b"\xff" * base) + b"\xff\xffRule Select \x00\xffSmall \x00\xff\xff\xff"
    reads = {base + k for k in range(0, 13, 2)} | {base + 16 + k for k in range(0, 7, 2)}
    ends = cover.runs_past(reads)
    assert ends == [base + 12, base + 22]
    span = (base, base + 64)
    assert cover.score(ends, right, span) == 1.0
    assert cover.score(ends, wrong, span) < 0.7


def test_reads_outside_the_string_block_do_not_score():
    assert cover.score([cover.RELOC + 0x100000], b"", (cover.RELOC, cover.RELOC + 64)) is None
