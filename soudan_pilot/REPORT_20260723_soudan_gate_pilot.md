# REPORT — 意思決定支援室 ゲート最小パイロット（DIRECTION案 §6）

- record_type: REPORT
- author: codex（COO・単一Writer）代行セッション
- created_at: 2026-07-23
- scope: DIRECTION案 v3 §6 の最小パイロット（`detect_soudan_gate.py` の実装＋4ゲート発火の物理観測）。判子前の実装リスク潰し。
- boundary: scratch相当（作業ブランチ）で実施。Drive・正典への書込ゼロ。外部送信なし。

## 0. 一行

意思決定支援室の **4ゲート（宛先／完全性／権限フィールド文脈／利益相反subject除外）を機械実装し、正常系PASS＋各違反系で検出が実際に発火することを物理観測した**（自己申告フィールドは読まない）。

## 1. 成果物

| ファイル | 役割 |
|----------|------|
| `detect_soudan_gate.py` | SOUDANゲート検出器（stdlibのみ）。frontmatter＋本文8節を機械再構成し4ゲートを判定。違反時 exit 非ゼロ。 |
| `soudan_fixtures/S1_complete_ok.md` | 完全・compliant（実在の論点＝L-038 model明示チェック要否の決定支援パッケージ）。 |
| `soudan_fixtures/S2_incomplete.md` | §6 指示案を意図的に欠落。 |
| `soudan_fixtures/S3_coi_kuro.md` | subject=kuro を kuro が準備／書込／決定（利益相反）。 |
| `soudan_fixtures/citing_related_ok.md` | soudan_id を `related:` にのみ参照（正当）。 |
| `soudan_fixtures/citing_authority_bad.md` | soudan_id を `authority:` と 根拠節に参照（違反）。 |
| `run_soudan_pilot.py` | 全fixtureを回し発火セルフチェック。 |
| `test_soudan_gate.py` | 単体テスト12件。 |
| `soudan_pilot_run.log` | 実行証跡。 |

## 2. 実測結果（証跡: `soudan_pilot_run.log`）

単体テスト **12件 PASS**（`py_compile` exit0）。

| fixture | 期待 | 観測 | 判定 |
|---------|------|------|------|
| S1_complete_ok | クリーン | 0違反 | OK |
| S2_incomplete | 完全性発火 | 1違反（§6欠落） | OK（fired） |
| S3_coi_kuro | 利益相反発火 | 3違反（prepared/committed/for_decider=kuro） | OK（fired） |
| citing_related_ok | クリーン | 0違反 | OK |
| citing_authority_bad | 権限発火 | 2違反（authority欄＋根拠節） | OK（fired） |

- 単独実行 `detect_soudan_gate.py S3 --citing citing_authority_bad` は **exit=1**（違反ゲートが物理的に非ゼロ終了）。
- 発火セルフチェック: **PASS**。**正常系だけで完了扱いにしていない**（各違反系で発火を確認）。

## 3. 特記（フィールド文脈判定の実証）

権限ゲートは「soudan_id が出現したら違反」ではなく **出現フィールドで判定**する: `related:` は通し（来歴＝正当）、`authority:` 欄・`根拠` 節は発火。`citing_related_ok`（related参照）がクリーンで `citing_authority_bad`（authority/根拠参照）が発火することで、v3査読で要求した「provenance参照 vs 根拠引用の機械分離」が実際に効くことを確認した。

## 4. 境界・限定

- fixtureは検出器検証用の合成物。ライブ運用の測定ではない。
- 本パイロットは機構の発火実証であり、対象の実在論点（S1=Themis model-check）は**判子前ゆえ成果物として使い回さない**（機構承認後に正式相談として作り直す）。
- 本設置（`_soudan/` への常駐配置・正典接続）は丼ちゃん判子後にコデが実行。本セッションはscratch相当の実装・実証まで。

以上。
