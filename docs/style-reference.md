# Style reference - Vattroller X

Voice table and paired examples taken from the translated, reviewed script (pilot b001 = the Vattroller Jin comic;
rulings in `glossary.md`, D1/D9 in `docs/decisions.md`). Translators and reviewers match this. Each row names the JP
markers and the English devices that carry them.

## Voices

| Character | JP markers | English devices |
|---|---|---|
| Jin (comic hero) | オレ, だぜ, ぞ, ∇ | brash shonen hero: short punchy lines, "!!", "Let's roll!" energy |
| Komachi (club captain) | このコマチさま, あまく見るんじゃないわよ, わよ/のよ | proud, bossy girl: calls herself "Komachi-sama", "Don't underestimate me!", exclamations |
| Totta | このトータさま, です∇ | calls himself "Totta-sama" every time ("is me, Totta-sama!!") |
| Ryo / Shu (rivals) | このリョウ様, オレ, だぜ | cocky: "Ryo-sama", "the great Ryo-sama", taunts; Shu cooler, fewer words |
| Ikazuchi | や/やないか, ねん, へん, ってぇ (Kansai) | casual drawl: "ain't", "ya", dropped g's ("talkin'"), "ain't he!" tags |
| Master West | である | pompous; ends lines with ", I say!" |
| Mr. Globe (old man) | じゃ, の, ムニャ, ヒョヒョヒョ | sleepy elder: "...mnya." at line end, "Hyo hyo hyo" laugh, "my boy/my dear" sparingly |
| Minami (twin) | ホホホ, わね | haughty: "Ohohoho!" laugh, "my dear" |
| Hokuto (twin) | レディ, horoscope talk | smarmy: "little lady", "Miss Komachi", blames his star sign |
| -zamasu lady | ザマス | keeps "zamasu" as a verbal tic at line end |
| Muchapy | ピィ | "Pyii!" |
| Shopkeepers, NPCs | ですます / casual | polite NPCs polite ("Please come again!"), kids casual, old men "eh?", "my boy" |

Honorifics (D1): a name + さん/くん/ちゃん/さま/先生/先輩 keeps "-san/-kun/-chan/-sama/-sensei/-senpai", the player
`∴` included (`∴-chan`). `tools/batches.py check` enforces it for every name in glossary §Characters. Plain titles
without a name (部長 "Captain", おじさん "mister") are translated.

## Paired examples

| id | JP | EN | why |
|---|---|---|---|
| e2494_0044c | いただくのは　このトータさまです∇ | Grandius is me, Totta-sama!! | self-honorific kept as Totta's tic |
| e2520_008d0 | あまく見るんじゃないわよ | Vattrolling captain, Komachi-sama! | Komachi's pride carried by the self-title |
| e2529_016a0 | うでたてふせ　５００回である！ | Five hundred push-ups, I say! | である -> ", I say!" |
| e2530_00630 | いちばんわかいってぇ天才やないか！ | the youngest Mars ever, ain't he! | Kansai -> drawl tag |
| e2533_00150 | マルスはもう引っこんだがの……ムニャ | Mars has already left... mnya. | sleepy tic kept |
| e2608_01194 | わたしと練習するザマスよ∇ | You'll practice with me, zamasu!! | ザマス kept, ∇ -> "!!" |

### Corrected example (reviewer pass)

| id | JP | first EN | corrected EN | lesson |
|---|---|---|---|---|
| e2649_00408 + 0042c | コマチちゃんやライバくんを / みならってほしいものだわい | I wish they'd learn from / Komachi and Raiba. | I wish they'd learn from / Komachi-chan and Raiba-kun. | honorifics are never dropped to save space; reword instead |
| e2607_012c4 | ∴ちゃんが今のところ　１位ね | ∴ is in 1st place now. | ∴-chan leads for now. | `∴` counts 72 px (12 chars): budget for the name, keep the suffix |
