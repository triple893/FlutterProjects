# REPORT — 相談レーン最小パイロット (DIRECTION 20260723a D2)

- record_type: REPORT
- author: codex (COO・単一Writer) 代行セッション
- created_at: 2026-07-23
- direction: DIRECTION 20260723a（丼ちゃん判子済み・即発効）
- scope: D2（最小パイロット・違反機械検出）のみ。D1はDrive側で別途処理、D3は下記§5参照。
- sensitivity: internal / 外部送信: なし

---

## 0. 一行

サブagent格下原則（L-034 補則2）の**違反機械検出スクリプトを実装し、正常系PASS＋違反系で検出が実際に発火することを物理観測した**。ただし本パイロットは**検出機構の実証**であり、**ライブ・セッションの行動測定ではない**（§4 の境界を厳守）。

## 1. 成果物（gitブランチ `claude/soudan-pilot-implementation-mvy2b0`）

| ファイル | 役割 |
|----------|------|
| `soudan_pilot/detect_tier_violations.py` | 違反機械検出器（stdlibのみ・非依存）。セッションログのAgent spawnをパースし (a)模型表 (b)model有無＋階層 (c)証拠引用レビュー を機械再構成。**自己申告PASSフィールドは一切読まない。** |
| `soudan_pilot/transcript_adapter.py` | 実Claude Codeトランスクリプト（JSONL）→ 正準イベント схемаへの変換器。実ログでも使える。 |
| `soudan_pilot/fixtures/C1_direct_injection.jsonl` | C1: 新規＋L-034本文直接注入。 |
| `soudan_pilot/fixtures/C2_link_only.jsonl` | C2: 新規＋リンクのみ。 |
| `soudan_pilot/fixtures/C3_link_only_elapsed.jsonl` | C3: 長時間経過＋リンクのみ。 |
| `soudan_pilot/run_pilot.py` | 全ケースを回し切り分け表＋発火セルフチェックを出力。 |
| `soudan_pilot/test_detector.py` | 単体テスト9件（正常系＋全違反コード）。 |
| `soudan_pilot/pilot_run.log` | 実行証跡（本REPORTの添付・§3）。 |

## 2. 検出器の設計（自己申告PASS不可の担保）

検出器は「合格」「compliant」等の判定フィールドを**読まない**。ログ中の構造イベントのみから (a)(b)(c) を再構成する：

- **(a) 模型表宣言** … 最初のspawnより前に `model_table` イベントが存在し、全spawnのsubagent_typeを網羅しているか。無い/遅い/不完全 → `V_A_*`。
- **(b) model明示＋階層（格下原則）** … 各spawnに `model` があるか（無 → `V_B_MODEL_MISSING`）。tier(sub) ≤ tier(parent) か。tier(sub) > tier(parent) かつ escalation未宣言 → `V_B_TIER_INVERSION`（指揮構造の逆転）。同格かつ例外(a)なし → `W_B_SAME_TIER`（既定は1段下ゆえ警告）。1段下以下 → 合格。
- **(c) 証拠引用レビュー** … 各spawn_idを参照し **citations が非空** の `review` イベントがあるか。無/空 → `V_C_NO_EVIDENCE_REVIEW`。

tier表（org固有・`--tier`で上書き可）: `haiku=1 < sonnet=2 < opus=3 < fable=4`。根拠: L-031（Fable5=最上位裁定・Opus=CEO代行/COO級）。**この順位はdonzlab運用の約束事であり、検出器のコアではなく設定である**（モデル名がマーケティング上どちらが上かとは独立に、格下原則の判定にのみ使う）。

## 3. 実測結果（証跡: `pilot_run.log`）

単体テスト: **9件 PASS**（`py_compile` exit0）。

切り分け表（機械再構成・自己申告なし）:

| case | delivery | ctx | (a) | (b) | (c) | 違反数 |
|------|----------|-----|-----|-----|-----|--------|
| C1 | direct_injection | fresh | PASS | PASS | PASS | 0 |
| C2 | link_only | fresh | PASS | WARN | FAIL | 1 |
| C3 | link_only | long | FAIL | FAIL | FAIL | 5 |

発火セルフチェック（**正常系だけで完了扱いにしない**要件）:

- C1: 期待0違反 → 観測0 → **OK**
- C2: 検出発火を期待 → 観測1違反 → **OK (fired)**
- C3: 検出発火を期待 → 観測5違反 → **OK (fired)**
- 単独実行 `detect_tier_violations.py fixtures/C3...` は **exit=1**（違反ゲートが物理的に非ゼロ終了することを確認）。

→ **違反ケースで検出が実際に発火することを物理観測した。** 検出コード実例: `V_A_NO_MODEL_TABLE` / `V_B_MODEL_MISSING` / `V_B_TIER_INVERSION` / `V_C_NO_EVIDENCE_REVIEW`。

## 4. 境界・正直な限定（事実ベース／原因は断定しない）

- **本パイロットのfixture（C1/C2/C3）は、検出器を検証するために手で書いた合成シナリオである。** 隔離コンテナからはユーザ環境の実セッションログにアクセスできないため、**ライブのOpus親セッションの指示追従を測定したものではない**。
- したがって「C3（リンクのみ＋長経過）は追従が落ちる」等の**行動的結論は本REPORTからは主張しない**。fixtureはあくまで各チェックを発火させるための入力であり、因果の証拠ではない。
- **確定した事実は2点のみ**: ①検出機構が正常系を素通しし違反系で必ず発火する（機械的に実証）。②実ログ投入用アダプタが用意された。
- 実測（3条件の行動測定）に進むには、実C1/C2/C3セッションを実際に走らせ、そのトランスクリプトを `transcript_adapter.py` に通す必要がある。これは別ステップ。

## 5. D3（回付規律）の判断

- 候補5（Opus固有の指示追従不良）は、**本パイロットでは支持も反証もされない**（§4のとおり行動データを取得していないため）。
- よって **L-031行へ回付する証拠は無し**。何も回付しない。続投可否はコデ判定事項でなく丼ちゃん判子事項（DIRECTION D3）ゆえ、当方は判定しない。
- 実ログでの3条件測定後に候補5が示唆された場合に限り、その時点で証拠のみをL-031へ回付する（本REPORTでは非該当）。

## 6. 次アクション（本DIRECTION外・参考）

- L-038 Themis へ「model明示チェック」を組み込むか否かは、本D2結果を見て**別途起案・別途判子**（境界条項どおり本DIRECTIONに含まない）。本検出器はその判子が下りた場合の実装部品として流用可能。
- D1 の DISPATCH_LEDGER L-025 一行追記は、当セッションのDrive конnекторがcreate/copyのみ（in-place編集不可）のため未適用。正典台帳の複製は L-029（「正典2本」認識の廃止）に反するので**複製しない**。単一Writerが実機G:上で下記1行を L-025 備考へ追記されたい：

  > HQ配下・非権威の相談サブレーン `_soudan\` を設置（DIRECTION 20260723a）。

以上。
