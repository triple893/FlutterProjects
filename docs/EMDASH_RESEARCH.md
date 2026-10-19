# EMDASH_RESEARCH.md - EmDash CMS 導入リサーチ

- **調査日:** 2026年10月19日
- **調査対象:** EmDash（Cloudflare 発の OSS CMS）
- **一次情報:** [emdash-cms/emdash](https://github.com/emdash-cms/emdash) リポジトリ（`main` 88c2fa3、`emdash` コアパッケージ v1.3.1）の README と公式ドキュメントのソース（`docs/src/content/docs/`）
- **ステータス:** 調査段階（導入判断はまだ。下記「次のアクション」を参照）

---

## 1. 結論（要約）

EmDash は **「AIエージェントに CMS を直接操作させる」ことを前提に作られた CMS** です。今回の目的（AI前提で、MCP経由でコンテンツを作成・更新する）と合っています。

- MCP サーバーが**最初から組み込まれていて、デフォルトで有効**です（`/_emdash/api/mcp`）。
- Claude にはカスタムコネクタとして URL を登録すれば OAuth で接続できます。記事の作成・更新・公開・予約投稿、メディア、タクソノミー、メニュー、スキーマ、サイト設定まで扱えます。
- 権限は「OAuth スコープ × ユーザーロール」の積集合で決まるので、AIに渡す権限を最小にできます。
- Cloudflare Workers の**無料プランでも動きます**。サンドボックス化したプラグインを使う場合だけ Workers Paid が必要です。
- 注意点：安定版 1.0 は2026年9月末に出たばかりで、プラグインのエコシステムはまだ小さいです。ファーストパーティのプラグインも 0.x です。
- 反対の立場からの検証は [EMDASH_COUNTER_REVIEW.md](./EMDASH_COUNTER_REVIEW.md) を参照してください。

**推奨:** まず PoC（検証環境）として `blog-cloudflare` テンプレートを Workers 無料プランにデプロイします。次に Claude を MCP 接続して、「下書き作成 → 人間がレビュー → 公開」の運用フローを検証します。

---

## 2. EmDash とは

| 項目 | 内容 |
| --- | --- |
| 位置づけ | 「WordPress の精神的後継」をうたう、フルスタックの TypeScript CMS |
| 開発元 | Cloudflare（OSS として公開、ガバナンス文書あり） |
| ライセンス | MIT |
| バージョン | コア v1.3.1。2026-04-01 に v0.1.0（プレビュー）として公開、**安定版 1.0 は 2026-09-28**（v1.0.1） |
| 基盤 | Astro インテグレーション（`emdash/astro`）、Live Collections でコンテンツを取得 |
| コンテンツ形式 | Portable Text（HTML ではなく構造化データ。AI が扱いやすい） |
| エディタ | TipTap ベースのリッチテキスト管理画面（`/_emdash/admin`） |
| DB / ストレージ | Cloudflare: D1 / R2 / KV。Node.js: SQLite・Turso/libSQL・PostgreSQL・ローカルファイル |
| プラグイン | `definePlugin()` で作り、マニフェストで権限を宣言（例 `content:read`）。分離した Worker isolate 上で実行 |
| 移行 | WordPress（WXR / REST API / WordPress.com）のインポートウィザード、Contentful 変換パッケージ |
| テンプレート | `blank` / `starter` / `blog` / `marketing` / `portfolio`（それぞれ `-cloudflare` 版あり） |

---

## 3. AI / MCP 連携（本調査の中心）

### 3.1 MCP サーバーの仕様

- **エンドポイント:** `https://<ドメイン>/_emdash/api/mcp`（ローカルでは `http://localhost:4321/_emdash/api/mcp`）
- **トランスポート:** ステートレスな Streamable HTTP（`POST` のみ、JSON-RPC 2.0）
- **デフォルトで有効**です。無効にするときは `astro.config.mjs` で `emdash({ mcp: false })` を指定します。
- **認証:** Bearer トークンが必要です。管理画面のセッション Cookie では認証できません。
  - OAuth 2.1 + PKCE：Claude や ChatGPT などの対話型クライアント向け。ブラウザでスコープを承認します。
  - パーソナルアクセストークン（`ec_pat_` から始まる）：自動化やバッチ処理向け
  - OAuth Device Authorization Grant：CLI（`emdash login`）向け
- **OAuth ディスカバリ:** `/.well-known/oauth-protected-resource` から自動で検出されます。

### 3.2 使えるツール（静的なツールは約90個）

| カテゴリ | 主なツール |
| --- | --- |
| コンテンツ | `content_list` / `get` / `create` / `update` / `publish` / `unpublish` / `schedule` / `compare` / `duplicate` / `discard_draft` / `translations` ほか |
| 署名（著者） | `byline_*` |
| スキーマ | `schema_list_collections` / `schema_create_collection` / `schema_create_field` ほか |
| メディア | `media_upload`（base64）/ `media_update`（alt テキストなど）/ `media_delete` ほか |
| 検索 | `search`（全コレクション横断） |
| タクソノミー | `taxonomy_*`（カテゴリ・タグ、階層構造にも対応） |
| メニュー | `menu_*`（`menu_set_items` で一括置き換え） |
| リビジョン | `revision_list` / `revision_restore` |
| サイト設定 | `settings_get` / `settings_update`（タイトル、ロゴ、OG画像、SNSリンク） |
| サイト移行 | `site_export_*` / `site_import_*`（管理者の承認フローあり） |
| プラグイン | 有効にしたプラグインのツール（`<plugin>__<tool>` という名前で公開） |

### 3.3 AI 運用で安全性に効く仕組み

- **公開済み記事の更新は下書きとして保存されます。** `content_update` で本番は変わらず、`content_compare` で差分を確認し、`content_publish` を呼んで初めて反映されます。「AIが書く → 人間が承認」のフローを作りやすいです。
- **楽観ロック（`_rev`）:** 古いリビジョンを元に更新すると競合エラーになり、上書き事故を防げます。
- **編集ロック:** 人間が管理画面で編集している間は、AI 側の更新が `ENTRY_LOCKED` で拒否されます。
- **スコープ × ロール:** たとえば Contributor ロールのユーザーと `content:write` スコープの組み合わせなら、AI は下書きの作成しかできず公開はできません。
- **破壊的な操作:** `destructiveHint: true` の注釈が付いているので、クライアント側で確認を挟めます。

### 3.4 Claude との接続手順

1. EmDash サイトをデプロイします。
2. Claude の設定 → コネクタ → カスタムコネクタで `https://<ドメイン>/_emdash/api/mcp` を追加します。
3. OAuth の同意画面でスコープを必要なものに絞って承認します。
4. 自然言語で指示します。例：「夏のセールのブログ記事を下書きで作って」「FAQ の誤字を直して」「6月1日9時に予約公開して」

その他の連携先：
- Claude Code、Cursor などの開発ツール：同じ URL をリモート MCP として登録します。
- ドキュメント用 MCP：EmDash のドキュメント自体を AI に参照させるもので、開発時に使います。
- **Agent Skills:** [emdash-cms/skills](https://github.com/emdash-cms/skills) にサイト構築・プラグイン作成・CLI・WordPress 移行などのスキルがあり、Claude Code に読み込ませられます。
- **CLI:** `npx emdash content list|get|create ...`、`emdash types`（スキーマから型を生成）などがあり、CI や自動化からも操作できます。

---

## 4. ホスティングとコスト

| 構成 | 要件 | 備考 |
| --- | --- | --- |
| Cloudflare（推奨） | Workers + D1 + R2 + KV | **無料プランでデプロイできます。** `*-cloudflare` テンプレートは最初から無料プランで動く設定です |
| サンドボックス化したプラグイン | Workers Paid プラン + `worker_loaders`（`LOADER`）バインディング | 有料（Dynamic Workers）。使わなければ不要です |
| 画像変換 | Cloudflare Images の変換課金 | 同じ変換は月1回だけ課金 |
| Node.js でのセルフホスト | SQLite / PostgreSQL など | プラグインは `workerd` の子プロセスで実行します。Dockerfile と compose.yaml が同梱されています |

---

## 5. 評価

| 観点 | 評価 | コメント |
| --- | --- | --- |
| AI / MCP 対応 | ◎ | MCP が組み込みで、OAuth・スコープ・下書きフローまで揃っています。今回の目的に最も合います |
| セキュリティ | ○ | プラグインのサンドボックスと権限宣言があります（WordPress の脆弱性の大半はプラグイン由来、というのが設計の理由） |
| 開発体験 | ○ | TypeScript / Astro。型生成、CLI、Agent Skills があります |
| 運用コスト | ◎ | Workers 無料プランから始められ、サーバー管理は不要です |
| 成熟度・エコシステム | △ | 1.0 が出たばかりです。WordPress（6万以上のプラグイン）と比べるとプラグインはまだ少ないです |
| 既存の Flutter アプリとの連携 | ○ | REST API があるので、Flutter アプリのお知らせやコンテンツ配信のヘッドレス CMS として使えます |

---

## 6. 想定ユースケース（このプロジェクト向け）

1. **アプリのマーケティングサイトやLPの自動運用:** `marketing-cloudflare` テンプレートを使い、AIが更新情報やキャンペーンページを下書きし、人間が承認して公開します。
2. **ブログや SEO コンテンツの量産:** AIが記事を下書きし、タクソノミー、OG画像、予約公開まで MCP で一気通貫に行います。
3. **Flutter アプリのヘッドレス CMS:** アプリ内のお知らせ、FAQ、ヘルプを EmDash で管理し、REST API で取得します。

---

## 7. 次のアクション（PoC 計画案）

1. [ ] **「うちの環境」の確認:** 既存の EmDash インスタンスがあるか（Cloudflare アカウント上の Worker、D1 など）。※ 今回のセッションでは Cloudflare コネクタが未認可だったので確認できていません
2. [ ] PoC 用に `npm create emdash@latest` で `blog-cloudflare` を作成し、Workers 無料プランにデプロイ
3. [ ] AI 専用のユーザーを **Contributor（または Author）ロール**で作成し、最小スコープ（`content:read`、`content:write`、`media:write`）で Claude に接続
4. [ ] 検証シナリオ：記事の下書き作成 → `content_compare` で確認 → 人間が公開 → 予約公開 → リビジョンの復元
5. [ ] 評価結果を `DECISION_LOG.md` に記録して、本番導入を判断

---

## 参考

- リポジトリ: https://github.com/emdash-cms/emdash
- MCP サーバーリファレンス: リポジトリ内 `docs/src/content/docs/reference/mcp-server.mdx`
- AI ツール接続ガイド: リポジトリ内 `docs/src/content/docs/guides/ai-tools.mdx`
- Agent Skills: https://github.com/emdash-cms/skills
- 報道: [Phoronix](https://www.phoronix.com/news/Cloudflare-EmDash) / [TechRadar](https://techradar.com/pro/cloudflare-launches-emdash-the-spiritual-successor-that-wants-to-take-on-wordpress) / [DEV Community 比較記事](https://dev.to/alanwest/wordpress-vs-emdash-is-this-astro-based-cms-worth-the-switch-52hh)
