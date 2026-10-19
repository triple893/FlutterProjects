# DonzLab ポータル

DonzLab の各ラボ・エージェント図鑑・開発日記・活動リンクをまとめる入口サイト。
[EmDash](https://github.com/emdash-cms/emdash)（Astro ベースの CMS）で作っていて、AI が MCP 経由で記事を下書きできる。

> 現在は **PoC（お試し版）・非公開**。検証結果は [`../docs/EMDASH_POC_RESULT.md`](../docs/EMDASH_POC_RESULT.md)。

## 構成

| 区分 | コレクション | URL |
| --- | --- | --- |
| ラボ | `labs`（名前・絵文字・ひとこと・ステータス・リンク・並び順・紹介文） | `/labs`、`/labs/{slug}` |
| エージェント図鑑 | `agents`（名前・役割・中の人・立ち絵・キャッチコピー・プロフィール） | `/agents`、`/agents/{slug}` |
| 開発日記 | `posts`（カテゴリ: 開発日記 / リリース） | `/posts`、`/posts/{slug}` |
| 活動リンク | `links`（X・YouTube・TikTok など） | トップページに表示 |
| 固定ページ | `pages` | `/{slug}`（例: `/about`） |

スキーマと初期データは `seed/seed.json`。直接編集せず `python3 scripts/build-seed.py` で作り直す。

## ローカルで動かす

```bash
pnpm install
pnpm dev                     # http://127.0.0.1:4321
```

1. `http://127.0.0.1:4321/_emdash/api/setup/dev-bypass?redirect=/_emdash/admin` を開くと、開発用の管理者でログインし、シードが入る
2. 日本語検索を有効にする（初回のみ。DB の設定なのでシードでは入らない）

   ```bash
   curl -c cookies.txt http://127.0.0.1:4321/_emdash/api/setup/dev-bypass
   EMDASH_COOKIE_JAR=cookies.txt scripts/enable-ja-search.sh
   ```

3. 作り直したいときは dev サーバーを止めて `.wrangler/` を消す

## AI（MCP）からの更新

- エンドポイント: `/_emdash/api/mcp`
- AI 用トークンは **最小スコープ**で発行する：`content:read`、`content:write`、`media:write`
  - 管理画面 → 設定 → API トークン、または `POST /_emdash/api/admin/api-tokens`
- 運用ルール：**AI は下書きまで。公開は丼ちゃん（または CI のゲート）**
  - 公開済みの記事を AI が更新しても、本番は変わらず下書きとして保存される。差分を確認してから公開する
  - 本番では AI 用ユーザーを Contributor ロールにして、公開の権限そのものを持たせない

## 本番（Cloudflare）へ出すとき

`wrangler.jsonc` の D1・R2 を作成してから `pnpm deploy`。Workers の無料プランで動く。
公開範囲は Cloudflare Access などで先に絞っておく。

## チェック

```bash
pnpm typecheck
pnpm build
```
