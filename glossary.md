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
| ライバ | Raiba | | an opponent (not ライバル rival) | |
| レイナ | Reina | | ex-member of the Tsuchioni Gang (Ryo side story) | |
| カタマリ | Katamari | | Tsuchioni Gang leader | |
| アオイ | Aoi | | Kanata's little brother (Totta side story) | |
| カナタ | Kanata | | manager of the Mugendo VR shop; owns Dogrelic | |
| レイオン | Reion | | Master Reion of Reion Gym; Shu and Ryo's master | |
| イノガシラ | Inogashira | | dojo master (Shu side story) | |
| トホ | Toho | | name a Death Roller gives Totta's master (guess; e2517) | |
| ウェスト / マスターウェスト | West / Master West | | Premium Gym master; pompous, ends lines with "I say" (である) | |
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
| 界天島 | Kaiten Island | | where "Mars" waits (reading guessed) | |
| 界天コロシアム | Kaiten Colosseum | | | |
| グローブスタジアム | Globe Stadium | | Vattleague venue | |

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
| ツチオニ団 | Tsuchioni Gang | | thugs who take Arms from beaten opponents | |
| ロンダリンダ | Rondarinda | | gang of Rare Arm thieves | |
| ムゲンどう | Mugendo | | Kanata's VR shop | |
| ハンニバル社 | Hannibal Corp. | | Globe Corp. subsidiary | |
| しきょうせい | Four Fiends | | Hannibal's four Death Rollers | |
| インテンション | Intention | | an Arm | |
| ライオネル | Lionel | | Armalet | |
| ドラグーン | Dragoon | | Armalet (cf. Dragoon Rise) | |
| クラッケン | Kraken | | Armalet | |
| アシュラム | Ashram | | Armalet | |
| デスロード | Death Lord | | Armalet | |
| ベルゼーブ | Beelzeb | | Armalet | |
| Ｖポイント | V Points | | short for Vattrolling Points | |
| Ｖスキル | V Skills / V Skill | | singular when one skill is meant | |
| だいじなもの | Key Items | | menu entry | |
| せってい | Settings | | menu entry | |
| きろく | Save | | menu entry (quoted as "Save") | |
| リーブ | Reeve | | beginner Arm type (リーブけい Reeve type); リーブラスター Reeveblaster, リーブレード Reeveblade | |
| シャムシール | Shamshir | | Blade-type Arm | |
| Ｖマシン | V Machine | | Arm Set machine | |
| Ｖメダル | V Medal | | | |
| ツール | Tool | | support gear (HP restore etc.) | |
| キュアメイト | Cure Mate | | Tool | |
| チェーンアタック | Chain Attack | | technique | |
| ファルコーン | Falcorn | | Armalet | |
| ヘクサ社 | Hexa Corp. | | runs Premium Gym; president Todo | |
| バトリーグさんかパス | Vattleague Pass | | key item | |
| エンジェラン | Angelan | | Armalet (Corona side event, e2591) | |
| マルスパス | Mars Pass | | key item, Vattleague 1st prize (e2613) | |
| リーグパス | League Pass | | pro entry pass | |
| エクスバウンダー | Ex-Bounder | | arm type (エクスバウンダーけい) | |
| バトレンジャー | Vattranger | | TV hero show; バトレンピンク Vattranger Pink | |
| Ｖセンター | V Center | | link-battle / V Skill building | |
| ＶＲＸ | VRX | | in-world fighting video game | |
| ジャマーボール | Jammer Ball | | link-battle obstacle | |
| ジョイスポット | Joy Spot | | data receive service | |
| Ｖポン | V-Pon | | Arm capsule machine (VP in, random Arm out) | |
| エクスストライク | Ex-Strike | | arm type | |
| エクスハント | Ex-Hunt | | arm type | |
| エクスブレード | Ex-Blade | | arm type | |
| アシストけい | Assist type | | arm type | |
| サラマンド | Salamand | | Armalet | |
| フェンリー | Fenrie | | Armalet | |
| ユニホース | Unihorse | | Armalet | |
| ニャティー | Nyatty | | Armalet | |
| ゲンブール | Genbull | | Armalet | |
| ゴラムス | Golamus | | Armalet | |
| エンペリオル | Emperiol | | Armalet | |
| ブレイクロール | Break Roll | | Attack Roll a Bounder cannot deflect | |
| ウナギケーキ | Eel Cake | | key item | |
| カッパのて / カッパの手 | Kappa Hand | | key item (trade chain) | |
| ワカメ | Seaweed | | key item | |
| マスターのあかし | Master's Proof | | key item | |
| ぶいんバッチ | Club Badge | | key item (Club Force) | |
| ドロップドール | Drop Doll | | Tool | |
| アームスケープ | Arm Escape | | Tool | |
| ハイドマーカー | Hide Marker | | Tool | |
| サバイバルルール / オフィシャルルール | Survival Rules / Official Rules | | VRX rules | |
| サインアーム | Sign Arm | | Arm engraved with the player's favourite word | |
| バトローリングじてん | Vattrolling Encyclopedia | | library book | |

## Decisions from earlier batches
- RPG mode (b016-b030): Minami and her brother Hokuto are the Premium Gym twins (Takumi's ex-gym mates); Hokuto blames
  his horoscope (Scorpio, Cancer) and calls Komachi "Miss Komachi" / "little lady"; Minami laughs "Ohohoho".
  Kodama = Komachi's cat. Suzuka writes bottle letters to Mars; Komachi's crush is "Shu-sama".
  急がば転がれ (pun on 急がば回れ) = "Practice makes Roll-fect!". Ikazuchi's センチメートル malaprop = "centimental". Raiba is Komachi's big brother (she calls him "big brother"). Ikazuchi speaks Kansai
  dialect: casual drawl ("ain't", "ya", dropped g's). グローブ (the man) = Mr. Globe / President Globe, Globe Corp.
  president and the sleepy "...mnya" old man; laughs "Hyo hyo hyo".
- Club Force naming joke (e2528): "Four, so Force?" / "what's with the 'ce'" / "English puts 's' on the end".
- Side events b031-b036: Komachi's family runs a Japanese-sweets shop (和がし = "Japanese sweets"); Komachi calls
  the twins "the Dopey Twins" (おまぬけツインズ), Hokuto calls her "the shrimpy girl" (チンチクリン女); Corona is
  called a "cutesy faker" (ブリっ子). Puns: つきあって = "be my partner" (date / sparring), ヘナチョコ scrambled =
  "pipsqueak" -> "squeakpip", "peaksquip", "squippeak"; ロマン/マロン = "romance" / "MARRONS, chestnuts".
  アームセットしゅうりょう / をつづける = "Finish Arm Set" / "Continue Arm Set".
- A glossary JP run that is an ordinary word on one line (カタマリ "lump") is waived per id in
  `script/glossary_waive.tsv` (id, JP term, reason), read by `tools/batches.py`.
- ケイコ in the script is always 稽古 "training/practice" (Raiba, e2582-e2583), never a name: the old "Keiko" row
  was dropped (b032).
- The glossary check needs the literal "Vattrolling": write "Vattrolling" rather than the verb "Vattroll".
- Default player names (r077ac4-r077ae8): Gen, Jun, Tubasa (ツバサ; 6-cell name limit, Kunrei spelling, D10), Yoichi, Kai.
  ツバサ elsewhere is the word "wing(s)", so it has no table row.
