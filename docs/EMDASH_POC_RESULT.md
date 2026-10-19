# EMDASH_POC_RESULT.md - DonzLab ポータル PoC 結果

- **実施日:** 2026年10月19日
- **対象:** `donzlab-portal/`（EmDash 1.3.1 / Astro 7.4 / Cloudflare 版テンプレート、ローカル実行）
- **公開範囲:** 非公開（この開発環境の中だけで起動）
- **関連:** [EMDASH_RESEARCH.md](./EMDASH_RESEARCH.md) / [EMDASH_COUNTER_REVIEW.md](./EMDASH_COUNTER_REVIEW.md)

---

## 1. 結論

**EmDash で DonzLab ポータルは作れて、AI から MCP 経由で安全に更新できることを確認しました。**
反証レビューで予想した「日本語検索の弱さ」も、実際に再現しました。

| 検証項目 | 結果 |
| --- | --- |
| ポータルの構築（ラボ / エージェント図鑑 / 開発日記 / 活動リンク） | ✅ 全ページ表示。スマホ幅（390px）でも横にはみ出さない |
| 型チェック・本番ビルド（Cloudflare Workers 向け） | ✅ `pnpm typecheck` エラー0、`pnpm build` 成功 |
| MCP 接続（最小スコープのトークン） | ✅ 接続でき、72 個のツールが見える |
| AI が下書きを作る → 公開サイトには出ない | ✅ |
| 公開済み記事を AI が更新 → 本番は旧文言のまま、差分を確認できる | ✅ `content_compare` で差分を取得 |
| 古い版を元にした上書き | ✅ `[CONFLICT]` で拒否 |
| 権限外の操作（スキーマ変更・サイト設定の変更） | ✅ `[INSUFFICIENT_SCOPE]` で拒否 |
| 公開操作 → 本番に反映 | ✅ |
| 日本語検索 | ⚠️ 既定の設定では語の途中に一致しない。trigram で改善するが、2文字の語は不可 |

---

## 2. 作ったもの

- **ページ:** トップ、ラボ一覧と詳細、エージェント図鑑の一覧と詳細、開発日記の一覧と詳細、カテゴリ、DonzLab について、404
- **コレクション:** `labs`、`agents`、`posts`、`links`、`pages`（スキーマは `seed/seed.json`。`scripts/build-seed.py` で生成）
- **初期データ:**
  - ラボ 8件（DonzCorelab、ChordSheetMaker、DonzMusicLab、父ちゃんのパスタAI研究所、DonzMarketingLab、LLM比較Lab、Graphify 知識基盤、FlutterProject）
  - エージェント 5体（クロちゃん、コデちゃん、グラちゃん、スン爺、パルスくん）
  - X「AIまげ丼」へのリンク
- **意図的に載せなかったもの:** 法務関連のプロジェクトと、実在の人物が関わるファン活動系のプロジェクト。公開ポータルには向かないと判断した

---

## 3. MCP 検証の詳細

AI 用トークンのスコープは `content:read`、`content:write`、`media:write` の3つだけにしました。

1. **下書きの作成:** `content_create` で開発日記を作成 → `status: draft`。`/posts` には表示されない
2. **公開済みラボの更新:** `content_update` でひとことを変更 → 公開ページは旧文言のまま。`content_compare` で新旧を比べられる
3. **競合の防止:** 同じ `_rev` でもう一度更新 → `[CONFLICT] Content has been modified since last read`
4. **権限外の操作:**
   - `schema_create_collection` → `[INSUFFICIENT_SCOPE] requires schema:write`
   - `settings_update` → `[INSUFFICIENT_SCOPE] requires settings:manage`
5. **公開:** `content_publish` → 公開ページが新文言に変わる

### 気づいたこと

- **スコープがないツールも `tools/list` には出てきます**（72個中、スキーマ系13個・設定系2個）。呼び出すと拒否されますが、AI のコンテキストを消費し、ツールの選び間違いも誘いやすくなります
- **今回のトークンは開発用の管理者に紐づいているので、公開もできてしまいます。** スコープの `content:write` には公開も含まれます。「AI は公開できない」をシステムで保証するには、**AI 用ユーザーを Contributor ロールで作る**必要があります。ローカルではユーザーの招待（メール）ができないため、本番環境で検証します

---

## 4. 日本語検索

| 検索語 | 既定（porter unicode61） | trigram |
| --- | --- | --- |
| 耳コピ（3文字・語の先頭） | 1件 ✅ | 1件 ✅ |
| 自動生成（4文字・語の途中） | 0件 ❌ | 1件 ✅ |
| 知識の神経網（6文字・語の途中） | 0件 ❌ | 1件 ✅ |
| コード譜（4文字・AI が追加した文言） | 0件 ❌ | 1件 ✅ |
| 番人（2文字） | 0件 ❌ | 0件 ❌ |
| 研究（2文字） | 0件 ❌ | 0件 ❌ |

- trigram への切り替えは DB の設定で、シードには含められません。環境を作るたびに `scripts/enable-ja-search.sh` を実行します
- 2文字の語は trigram でもヒットしません。本番で検索が重要になったら、外部の検索サービスと併用します

---

## 5. 環境面のメモ

- `npm create emdash@latest` は、テンプレートを GitHub API から取得しようとして失敗しました（この開発環境のプロキシが 403 を返すため）。`git clone` でテンプレートを取得して代わりにしました
- 検索ボックスの「Searching… / No results found」など、一部の UI 文言は英語のままです

---

## 6. 次のステップ（本番化の前に）

1. [ ] 丼ちゃんがローカルの画面を確認し、デザインと中身を調整する（立ち絵の画像、各ラボの紹介文とリンク先）
2. [ ] Cloudflare コネクタを認可 → D1 と R2 を作成 → **Cloudflare Access で非公開のまま**デプロイ
3. [ ] 本番で AI 用ユーザーを **Contributor ロール**で作成し、「AI は公開できない」ことを確認する
4. [ ] Claude のカスタムコネクタに `/_emdash/api/mcp` を登録し、実際の会話から下書きを作る
5. [ ] 日本語検索の設定（trigram）を本番にも適用する
6. [ ] 一般公開の判断
