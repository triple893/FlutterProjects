# Don'z Lab ポータル（Donz-Lab.com）

Don'z Lab の「城」。ラボの門（カード）をくぐると、各ラボの世界に入っていく入口サイト。
[EmDash](https://github.com/emdash-cms/emdash)（Astro ベースの CMS）で作っていて、AI が MCP 経由で記事を下書きできる。

> 現在は **PoC（お試し版）・非公開**。検証結果は [`../docs/EMDASH_POC_RESULT.md`](../docs/EMDASH_POC_RESULT.md)。

## デザインの考え方

**漆と金箔の電脳城** — 漆黒の地に金箔の細い回路紋、差し色は朱を一点。明朝（Shippori Mincho B1）が手仕事、等幅（IBM Plex Mono）が技術を担い、見出しは日本語と英語を併記する。
デザインの正本は Claude Design のキャンバス（城・ラボの世界・ビジネス・神殿と街・動きの法則の 5 ボード）。動きのルールは [`docs/MOTION.md`](docs/MOTION.md)。

| モード | 使う場所 | 見た目 |
| --- | --- | --- |
| `castle`（城） | トップ、門の一覧、神殿と街、開発日記 | 黒地に金の回路紋・光輪・額縁の門 |
| `world`（世界） | 各ラボの中、エージェントの詳細 | ラボごとの世界グラフィックとテーマカラーで、全画面を使って没入させる |
| `business`（ビジネス） | `world: business` のラボ、`layout: business` の固定ページ | 生成りと紺のクリーンな構造。動かさない |

- 門のカードの紋は `src/components/GateMotif.astro`、ラボの世界の背景は `src/components/WorldArt.astro`
- ラボに `thumbnail`（サムネイル）や `hero_image`（メインビジュアル）の画像を入れると、紋や背景の代わりにその画像が出る
- 門の番号（壱・弐・参…）は並び順から自動で振る

## 構成

| 区分 | コレクション | URL |
| --- | --- | --- |
| ラボ | `labs`（英語のひとこと・ひとこと・ステータス・世界観・テーマカラー・サムネイル・メインビジュアル・紹介文・この世界でやっていること） | `/labs`、`/labs/{slug}` |
| 神殿と街 | `agents`（英語名・二つ名・所属〈本陣/天/街/復活待ち〉・担当・中の人・肖像画・ひとこと・プロフィール） | `/agents`、`/agents/{slug}` |
| 開発日記 | `posts`（カテゴリ: 開発日記 / リリース） | `/posts`、`/posts/{slug}` |
| 活動リンク | `links`（X・YouTube・TikTok など） | トップページに表示 |
| 固定ページ | `pages`（レイアウト〈business/world〉・リード文） | `/{slug}`（例: `/about`） |

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

Workers の無料プランで動く。ドメインは **`donz-lab.com`（ハイフンあり）**。

### 事前に必要なもの

- `donz-lab.com` が Cloudflare のアカウントでゾーンとして管理されていること（ネームサーバーが Cloudflare を向いていること）
- クラウド作業環境の設定
  - Network access の Allowed domains に `api.cloudflare.com`
  - Network secrets（または環境変数）に `CLOUDFLARE_API_TOKEN` と `CLOUDFLARE_ACCOUNT_ID`
- API トークンの権限
  - Account：Workers Scripts・D1・Workers R2 Storage・Access: Apps and Policies を Edit
  - Zone（donz-lab.com）：DNS・Workers Routes を Edit

### 手順

1. `npx wrangler d1 create donzlab-portal` と `npx wrangler r2 bucket create donzlab-portal-media` を実行し、出力された D1 の `database_id` を `wrangler.jsonc` に書く
2. **お試し中**は `preview.donz-lab.com` をカスタムドメインにする（`wrangler.jsonc` の `routes` に `{ "pattern": "preview.donz-lab.com", "custom_domain": true }`）
3. `pnpm deploy`
4. Cloudflare Access で `preview.donz-lab.com` にアプリを作り、丼ちゃんのメールアドレスだけを許可する
5. 本番の管理画面でセットアップ（管理者はパスキー）→ シードの適用 → `scripts/enable-ja-search.sh <本番URL>` で日本語検索を有効化
6. **一般公開するとき**は、カスタムドメインを `donz-lab.com` に付け替え、Access を外す。決定は `docs/DECISION_LOG.md` に記録する

AI 用の MCP トークンは、本番では Contributor ロールのユーザーで発行する（公開は人間だけ）。

## チェック

```bash
pnpm typecheck
pnpm build
```
