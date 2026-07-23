---
record_type: SOUDAN
authority: none
read_policy: never_first
soudan_id: S-20260723-01
title: Themis(L-038)へ〈model明示チェック〉を追加するか
subject: L-038 Themis model-check   # 案件名（人/AIでない）→利益相反ゲートN/A
requested_by: 丼ちゃん
prepared_by: codex
committed_by: codex
for_decider: kuro
effective_from: null
status: open
review_by: 2026-07-30
expires_when: L-038段階1完了時
promotes_to: null
related: L-038, L-034, DIRECTION 20260723a
created_at: 2026-07-23
updated_at: 2026-07-23
---

## 1. 論点

Themis段階1（Issuer・発注のfile-first強制, L-038）へ、サブagent spawnの「model明示」チェック（D2検出器 `detect_tier_violations.py` 相当）を今組み込むか、繰延べるか。

## 2. 丼ちゃんの意図（一次記録）

> （DIRECTION 20260723a 境界節・逐語）「L-034本文改訂・Themis(L-038)へのmodel明示チェック追加はD2結果を見て別途起案・別途判子（本DIRECTIONに含まない）。」
> 丼ちゃんは「D2の結果を見てから」を明示的な前提に置いている。

## 3. 材料（事実）

- D2検出器は実装・検証済み（単体9件PASS、違反ケースで発火＝C2:1/C3:5、単独exit=1）。出典: `REPORT_20260723_soudan_pilot.md`。
- ただしD2はfixture検証であり、実セッションログでの稼働実績はゼロ（同REPORT §4）。
- L-038段階1はIssuer限定・execution_authority=granted・判子済み（DISPATCH_LEDGER L-038行）。

## 4. 選択肢

- **案A（今すぐ組込）**: Themis Issuerにmodel明示チェックを即追加。コスト小・可逆（フラグ化）。リスク=実ログ未検証の検出器を本番ゲートに載せ、誤検知でIssuerが止まる恐れ。触れる正典=L-038本文。
- **案B（繰延・パイロット後）**: まずD2検出器を実ログ数本に通し発火/誤検知を実測 → 問題なければ段階1完了時に組込。コスト=1パイロット。リスク小。DIRECTION 20260723a境界と整合。触れる正典=なし（別判子で後日）。
- **案C（恒久見送り）**: model明示はREPORT自己申告に委ね機械ゲート化しない。コスト0・リスク=規律が緩む（自己申告不可の原則に反する）。

## 5. 推奨案

**案B（繰延・パイロット後）を推奨**（助言であり決定ではない）。理由: 丼ちゃんの一次意図が「D2結果を見て」であり、検出器は在るが実ログ未検証。誤検知でIssuerを止める前に、安価なパイロットで発火/誤検知を実測する方が「正常系だけで完了にしない」規律（L-038/L-040）に忠実。

## 6. 指示案（案・未発効）

> MISSION草案（判子後にコデが発行）: 「実Claude Codeトランスクリプト3本を `transcript_adapter.py` に通し `detect_tier_violations.py` で検査。誤検知0・真陽性の発火を確認したら、Themis Issuerへ同チェックをフラグ付きで組込む案を別途起票。異常系での実停止を物理観測しREPORT添付。」

## 7. 一回判断チェックリスト

- 完全性: 本節1〜7充填済み ✓
- 権限: 本SOUDANは非権威・authority:none、指示案は未発効 ✓
- 利益相反: subjectは案件（人/AIでない）→N/A ✓
- 可逆性: 案Bは組込前段階ゆえ完全可逆 ✓
- 境界: L-034本文・Themis本文は触れない（別判子）／外部送信なし ✓

## 8. 危険・未確定

- 実ログの入手経路（どのセッションのトランスクリプトを使うか）は未確定。断定せず、パイロット設計時に切り分ける。
- 誤検知率は未測定（fixtureでは0だが実ログ分布は不明）。
