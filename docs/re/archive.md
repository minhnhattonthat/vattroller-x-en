# Resource archive

**verified** (contiguity check over all entries; Huffman/LZ10 decoders produce coherent images): `tools/archive.py`.

- Table at ROM `0x100000`: 2714 entries of `(u32 GBA pointer, u32 size)`. Code holds the table address as a literal at
  `0xEC740`, `0xFC4D8` and `0x312D10` (the last one is inside archive data; check before relying on it).
- Files are stored back to back in table order from `0x1054D0` to `0x7FF268` (no gaps: entry i end == entry i+1 start).
  Files are reached by index through the table, so a rebuilt archive may move, grow or be placed past 8 MiB.
  **guess:** nothing else points into the data area with absolute pointers. Some 0x0874xxxx-looking words occur inside
  other files (24 at 0x19xxxx, 56 at 0x1Cxxxx, ...); confirm they are not file pointers before moving files (phase 3).
- Compression: 23 files are BIOS Huffman 8-bit (type 0x28; #1317-1358, images); a few start with 0x10 (LZ10), most
  raw. Both decoders are in `archive.py` (`unpack`). Encoders are not written yet; only text files must change, and
  those are raw.
- File groups seen in the sweep (`tools/gfx_sweep.py`):
  - #0-430: small tables and palettes (0x20 / 0x80 / 0x200 bytes);
  - #431-452: UI tile sheets (menus, name entry, title);
  - #453-643: battle/effect sprites; #644-702: map tilesets; #703-1131: tilemaps and sprite/animation data;
  - #1132-1135: fonts (see `font.md`); #1136-1530: character sprites; #1531-1654: portraits;
  - #1655-1835: comic-mode art pieces; #2176-2474: map/collision data;
  - #2475-2711: event files holding script command streams (`script.md`).

## Free space

- After the archive: `0x7FF268-0x7FFFFF` holds non-uniform bytes, not proven free.
- Save type SRAM (`SRAM_F_V103` at 0xE495C and 0xF3FAC), so expanding the ROM to 16 MiB (or 32 MiB, xdelta) does not
  disturb saves. **Plan:** put relocated text, the rebuilt archive tail and new code past `0x800000`.
- Zero runs of 0x7838 bytes at `0xE49EC` and `0xF4784` sit inside the two embedded link/multiboot images
  (`NINTENDOSio32ID_030820` headers at 0xE4944 and 0xF3F94); not free.
