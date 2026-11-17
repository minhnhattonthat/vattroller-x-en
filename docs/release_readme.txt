Vattroller X - English translation patch v{version} ({date})
================================================================

Unofficial English fan translation of Vattroller X (Game Boy Advance, Bandai, 2004;
developed by Ganbarion).

This zip holds only the patch ({patch}) and this README. It contains no game data.
You need your own dump of the Japanese cartridge. Do not ask for, or share, patched ROMs.


Base ROM (apply the patch to exactly this file)
-----------------------------------------------
  No-Intro name: Vattroller X (Japan).gba
  Size:   {base_size} bytes
  CRC32:  {base_crc32}
  MD5:    {base_md5}
  SHA-1:  {base_sha1}

Patched result
--------------
  Size:   {out_size} bytes (the ROM grows past 16 MiB: that is expected)
  CRC32:  {out_crc32}
  SHA-1:  {out_sha1}


How to patch
------------
The patch is BPS. Use Floating IPS (Flips), beat, or the web patcher at
https://www.marcrobledo.com/RomPatcher.js/ : pick the Japanese ROM and {patch},
then save the result as a .gba file. A wrong base ROM is refused by the patcher
(BPS checks the CRC32).


Playing
-------
Tested in Mesen 2 (MesenCE 2.2.1). Any accurate GBA emulator or flash cart that
handles a 32 MiB-class ROM should work.
Start from a cold boot: savestates made with another version of the game or patch
carry old text and graphics.


Translation status
------------------
  Story and dialogue (comic mode, RPG mode, side events, town NPCs)   Translated
  Menus, items, Arms, Armalets, V Skills, shops, system messages       Translated
  Graphics with text (menu labels, help bubbles, map labels, signs,
  book spines, rule cards)                                             Translated
  Name entry                                                           Latin keyboard (kana pages redrawn)
  Credits roll                                                         Translated
  Title logo and Ganbarion boot logo                                   Left in Japanese (logos)


Known issues
------------
  - Link-cable features (multiplayer battles, V Skill trading) could not be tested.
  - Some short labels are abbreviated to fit their fixed-width boxes.
  Report bugs (a savestate helps most): https://github.com/minhnhattonthat/vattroller-x-en/issues


Credits
-------
  Translation, hacking and tools: minhnhattonthat
  The translation was made with extensive AI assistance (Claude by Anthropic).
  Corrections are very welcome.

Vattroller X is (c) Bandai / Ganbarion / Tenya Yabuno. This is an unofficial fan
project, not affiliated with them.
