# Glossary - Vattroller X

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.
`tools/batches.py check` enforces the tables below (JP run in the line -> one EN form must appear; Avoid forms fail).

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept, hyphenated (Komachi-san, Takumi-chan, Toda-sensei). Name order: Western (given name first).
- Romanisation source: official English names where they exist (none found: no English release), else Hepburn without macrons (Shu, Ryo, Todo).
- Credits: English.
- Register / flavour (D9): natural, lively kids'-anime English; contractions; each character's quirk kept in English
  (Totta's "Totta-sama", the old man's sleepy "...mnya", the -zamasu lady's "zamasu" kept as a verbal tic).
- ジン = Jin (Jin Tsukahara, つかはら ジン), hero of the "Vattroller Jin" comic books; not a table row, so
  lines that address him may drop the name. ファイバード = Firebird (Jin's Armalet bird; ふしちょう = phoenix),
  ドラグーン・ライズ = Dragoon Rise (Shu's special move).
- Comic-book chapter titles: バトローラージン "Vattroller Jin", 登場編 "Debut Arc", げきとう編 "Showdown Arc",
  修行編 "Training Arc", アレーナ編 "Arena Arc", 番外編 "Side Story", デスロール編 "Death Roll Arc",
  第１話 "Episode 1", おわり "The End".
  Sound effects: English onomatopoeia (ゴロゴロ -> rumble, グーグー -> zzz).
- Abbreviations: full names and terms, prefer engine changes over shortening. Stat abbreviations the game prints in
  Latin letters (HP, AP, VP, BL, ST...) stay as they are.

## Style rules
- One row = one on-screen line, at most 36 characters (dialogue). Rows flagged `+` continue the box of the row before;
  a sentence may run across rows, split it where the English reads naturally.
- Punctuation map: 「」 -> "...", 『』 -> "..." (term quotes, used sparingly), …… / ・・・ -> ..., ！？ -> !?,
  ∇ -> !!, ≡ -> !? (these are glyph codes in the JP font), 　 (fullwidth space) -> normal space or nothing.
- Plain ASCII only. No curly quotes, no em dashes (use "--" sparingly).
- The player character is addressed as "you" (キミ/あんた/おまえ: tone carried by the speaker's voice, not the pronoun).

## Characters
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| コマチ | Komachi | | 1st-year VR Club captain, proud ("Komachi-sama") | |
| シュウ | Shu | | rival | Shuu |
| タクミ | Takumi | | | |
| リョウ | Ryo | | rival | Ryou |
| イカヅチ | Ikazuchi | | | |
| トータ | Totta | | calls himself "Totta-sama" | Tota |
| ヘクサ | Hexa | | | |
| コロナ | Corona | | | |
| グレン | Glen | | | Guren |
| スズカ | Suzuka | | | |
| タイラー / マスタータイラー | Tyler / Master Tyler | | | |
| ミナミ | Minami | | | |
| ハヤテ | Hayate | | | |
| ホクト | Hokuto | | | |
| コダマ | Kodama | | | |
| クニガミ | Kunigami | | | |
| ハンニバル | Hannibal | | | |
| ワシュー | Washu | | | |
| トウドウ | Todo | | | Toudou |
| ムチャピー | Muchapy | | Jin's pet; cries "Pyii!" | |
| ムニャ | mnya | | sleepy mumble of an old man (e2533) | |
| アサマ | Asama | | | |
| ケイコ | Keiko | | | |
| ライバ | Raiba | | an opponent (not ライバル rival) | |

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 勝飛中 / 勝飛中学 | Katsutobi Middle / Katsutobi Middle School | | the hero's school | |
| 勝飛町 | Katsutobi Town | | | |
| 勝飛体育舘 | Katsutobi Gym | | | |
| 真丸中 | Mamaru Middle | | | |
| 真丸町 | Mamaru Town | | | |
| 田万里村 | Tamari Village | | | |
| 光円寺 / こうえんじ | Koenji | | | |
| 弾打浜 | Dandahama | | | |
| グローブタウン | Globe Town | | | Glove Town |
| グローブ社 | Globe Corp. | | runs the official tournaments | Glove |
| マーブルアレーナ | Marble Arena | | | |
| マーブルスタジアム | Marble Stadium | | | |
| スパイルアレーナ | Spile Arena | | | Spiral Arena |
| スパイルスタジアム | Spile Stadium | | | |
| デスロールコロシアム | Death Roll Colosseum | | | |
| プレミアムジム | Premium Gym | | | |
| レイオンジム | Reion Gym | | | |
| クラブフォース | Club Force | | | |

## Items / skills / terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| バトローラー | Vattroller | | title word; a player of the sport | Battroller, Battler |
| バトローリング | Vattrolling | | the sport | Battrolling |
| バトリーグ | Vattleague | | | Battleague |
| ＶＲ部 / ＶＲ | VR Club / VR | | short for Vattrolling club | |
| アーム | Arm | | the battle parts (arm units) | |
| アームセット | Arm Set | | | |
| アーマレット | Armalet | | aura-amplifying bracelet | Armlet |
| オーラ | aura | | | |
| オーラメイト | Aura Mate | | | |
| マルス | Mars | | a state a Vattroller reaches; keep the quotes the JP has | |
| ロール | Roll | | moves: アタックロール Attack Roll, ヒールロール Heal Roll | |
| デスロール | Death Roll | | | |
| デスローラー | Death Roller | | | |
| レアアーム | Rare Arm | | | |
| ブレード | Blade | | arm type (BL) | |
| ストライク | Strike | | arm type (ST) | |
| ハント | Hunt | | arm type (HU) | |
| バウンダー | Bounder | | arm type (BO) | |
| ドグレリック | Dogrelic | | a famous arm | |
| シャークボール | Shark Ball | | | |
| アームリライター | Arm Rewriter | | | |
| 必殺技 | special move / special | | | |
| グランディウス | Grandius | | Marble Arena prize Arm (sword + Bounder) | |
| ホウオウマル | Hououmaru | | Jin's sword | |
| マール | Marl | | Dr. Marl (マールはかせ), head of the Marl Vattrolling Lab, M-VL "Marble" | |
| シャークボール | Shark Ball | | training machine | |
| ヒールロール | Heal Roll | | | |
| アタックロール | Attack Roll | | | |
| スマッシュ | Smash | | | |
| ドロップ | Drop | | | |

## Decisions from earlier batches
- (none yet)
