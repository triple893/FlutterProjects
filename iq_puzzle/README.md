# 無料IQパズル（iq_puzzle）

結果まで無料で遊べる、行列推理（レーヴン漸進的マトリックス風）のIQパズルアプリです。
問題はシード付き乱数でその場で自動生成するので、画像素材は使っていません。

## 遊び方

- 3×3 のマスに並んだ図形の規則（縦・横の並び）を見つけて、右下の「？」に入る図形を選びます。
- 30問・制限時間20分。難易度は5段階で、6問ごとに上がります。
- 分からない問題は飛ばして、「前へ」で戻れます。
- 終了すると推定IQ・上位何%か・難易度別の正答数が出て、各問題の正解と規則の解説を確認できます。

> 推定IQは、正答数を仮の分布（平均50%・標準偏差約17%）に当てはめた娯楽用の目安です。
> 標準化された知能検査の結果ではありません。

## 問題の作り方

| 属性 | 使う規則 |
| --- | --- |
| 形（6種） | 一定 / 3種類が各行・各列に1回ずつ（ラテン方陣） |
| 個数（1〜6） | 一定 / 等差（行ごとにずらすこともある） / ラテン方陣 / 左 ± 中央 = 右 |
| 塗り（白・黒・斜線） | 一定 / ラテン方陣 |
| 大きさ（小・中・大） | 一定 / 左から右へ変化 / ラテン方陣 |

| レベル | 変化する属性 | 選択肢 | 追加される規則 |
| --- | --- | --- | --- |
| 1 | 1 | 6 | |
| 2 | 2 | 6 | 行ごとのずらし・ラテン方陣（個数・大きさ） |
| 3 | 2 | 8 | 足し算・引き算 |
| 4 | 3 | 8 | |
| 5 | 4 | 8 | |

誤答の選択肢は「隣のマスの写し」「1属性だけずらしたもの」「2属性ずらしたもの」を混ぜて作るので、
「他の選択肢と一番共通点が多いもの」を選ぶだけでは正解できません。

コード: `lib/src/puzzle/generator.dart`（生成）、`lib/src/test/scoring.dart`（採点）

## 開発

```sh
flutter pub get
flutter analyze
flutter test
flutter run -d chrome            # ブラウザでプレビュー
flutter build web --no-web-resources-cdn   # 外部CDNに依存しないWeb版
```

### 日本語フォント

Web版が日本語フォントを外部（fonts.gstatic.com）から読み込まずに済むよう、
UIで使う文字だけに絞った Noto Sans JP（SIL OFL 1.1、`assets/fonts/OFL.txt`）を同梱しています。
`lib/` の文言を変えたら作り直してください（`test/font_coverage_test.dart` が不足を検出します）。

```sh
pip install fonttools
curl -LO 'https://raw.githubusercontent.com/google/fonts/main/ofl/notosansjp/NotoSansJP%5Bwght%5D.ttf'
python3 tool/subset_fonts.py 'NotoSansJP[wght].ttf'
```
