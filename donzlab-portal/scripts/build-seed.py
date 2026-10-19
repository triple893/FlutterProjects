"""Generate seed/seed.json for the DonzLab portal.

Run: python3 scripts/build-seed.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def pt(*paragraphs):
    """Turn plain paragraphs into Portable Text blocks. A tuple ("h2", text) makes a heading."""
    blocks = []
    for i, p in enumerate(paragraphs):
        style, text = p if isinstance(p, tuple) else ("normal", p)
        blocks.append(
            {
                "_type": "block",
                "_key": f"b{i}",
                "style": style,
                "children": [{"_type": "span", "_key": f"s{i}", "text": text}],
            }
        )
    return blocks


def title_field(label="タイトル"):
    return {"slug": "title", "label": label, "type": "string", "required": True, "searchable": True}


collections = [
    {
        "slug": "labs",
        "label": "ラボ",
        "labelSingular": "ラボ",
        "urlPattern": "/labs/{slug}",
        "supports": ["drafts", "revisions", "preview", "search", "seo"],
        "fields": [
            title_field("ラボ名"),
            {"slug": "emoji", "label": "アイコン絵文字", "type": "string"},
            {"slug": "tagline", "label": "ひとこと", "type": "string", "searchable": True},
            {
                "slug": "lab_status",
                "label": "ステータス",
                "type": "select",
                "defaultValue": "準備中",
                "validation": {"options": ["稼働中", "開発中", "準備中"]},
            },
            {"slug": "lab_url", "label": "ラボへのリンク", "type": "url"},
            {"slug": "sort_order", "label": "並び順", "type": "integer", "defaultValue": 100},
            {"slug": "content", "label": "紹介文", "type": "portableText", "searchable": True},
        ],
    },
    {
        "slug": "agents",
        "label": "エージェント図鑑",
        "labelSingular": "エージェント",
        "urlPattern": "/agents/{slug}",
        "supports": ["drafts", "revisions", "preview", "search", "seo"],
        "fields": [
            title_field("名前"),
            {"slug": "role", "label": "役職・役割", "type": "string", "searchable": True},
            {"slug": "engine", "label": "中の人（AI）", "type": "string"},
            {"slug": "portrait", "label": "立ち絵", "type": "image"},
            {"slug": "catchphrase", "label": "キャッチコピー", "type": "string", "searchable": True},
            {"slug": "sort_order", "label": "並び順", "type": "integer", "defaultValue": 100},
            {"slug": "content", "label": "プロフィール", "type": "portableText", "searchable": True},
        ],
    },
    {
        "slug": "posts",
        "label": "開発日記",
        "labelSingular": "日記",
        "urlPattern": "/posts/{slug}",
        "supports": ["drafts", "revisions", "preview", "scheduling", "search", "seo"],
        "fields": [
            title_field(),
            {"slug": "featured_image", "label": "アイキャッチ", "type": "image"},
            {"slug": "excerpt", "label": "要約", "type": "text", "searchable": True},
            {"slug": "content", "label": "本文", "type": "portableText", "searchable": True},
        ],
    },
    {
        "slug": "links",
        "label": "活動リンク",
        "labelSingular": "リンク",
        "supports": ["drafts", "revisions"],
        "fields": [
            title_field("表示名"),
            {"slug": "link_url", "label": "URL", "type": "url", "required": True},
            {
                "slug": "platform",
                "label": "種類",
                "type": "select",
                "validation": {"options": ["X", "YouTube", "TikTok", "note", "GitHub", "その他"]},
            },
            {"slug": "sort_order", "label": "並び順", "type": "integer", "defaultValue": 100},
        ],
    },
    {
        "slug": "pages",
        "label": "固定ページ",
        "labelSingular": "ページ",
        "urlPattern": "/{slug}",
        "supports": ["drafts", "revisions", "preview", "search", "seo"],
        "fields": [
            title_field(),
            {"slug": "content", "label": "本文", "type": "portableText", "searchable": True},
        ],
    },
]

labs = [
    ("donz-corelab", "🧠", "DonzCorelab", "AI開発環境の中枢。インフラ・DB・エージェント設計", "稼働中", 10,
     ["DonzLab 全体を支えるコア。インフラ要件定義、データベース、エージェント設計をまとめて扱う。"]),
    ("chord-sheet-maker", "🎸", "ChordSheetMaker", "耳コピ支援Webツール。タブ譜の自動生成", "開発中", 20,
     ["耳コピを手伝うWebツール。タブ譜を自動で作る。マイナー曲や地下アイドル曲に強いのが売り。"]),
    ("donz-music-lab", "🎼", "DonzMusicLab", "作曲エージェントと音楽まわりの研究", "開発中", 30,
     ["作曲エージェントを中心に、音楽づくりを AI と進めるラボ。"]),
    ("pasta-lab", "🍝", "父ちゃんのパスタAI研究所", "レシピと料理を AI と研究する", "準備中", 40,
     ["料理とレシピ配信を AI と一緒に研究するラボ。"]),
    ("donz-marketing-lab", "📣", "DonzMarketingLab", "SNS・発信まわりの戦略ラボ", "稼働中", 50,
     ["X・YouTube・TikTok などの発信を、AI と組んで設計・検証するラボ。"]),
    ("llm-cost-lab", "📊", "LLM比較Lab", "LLM のコストと性能を比べる", "開発中", 60,
     ["いろいろな LLM のコストパフォーマンスを測って比べるラボ。"]),
    ("knowledge-graph", "🕸️", "Graphify 知識基盤", "Obsidian で作る知識の神経網", "稼働中", 70,
     ["Obsidian と Graphify で、DonzLab の知識をつないでいく基盤。"]),
    ("flutter-project", "📱", "FlutterProject", "AI と一緒に作るスマホアプリ", "開発中", 80,
     ["Flutter で Android / iOS 両対応のアプリを AI と一緒に作るプロジェクト。"]),
]

agents = [
    ("kuro", "クロちゃん", "CEO / 意味・判断・方針", "Claude", "意味と方針は、クロに聞け。", 10,
     ["DonzLab の CEO。日本語、戦略、大きな判断、言葉の精度を担当する。"]),
    ("kode", "コデちゃん", "COO / 総合管制・実行・進捗", "Codex", "実装と進捗は、コデが握る。", 20,
     ["DonzLab の COO。実装、査読、ファイル管理、進捗の見える化を担当する。"]),
    ("gura", "グラちゃん", "CSO / 調査・クリエイティブ", "Gemini", "大量調査と素材づくりは、グラにおまかせ。", 30,
     ["DonzLab の CSO。爆速調査、HTML、画像、マーケ、並列処理を担当する。"]),
    ("sunji", "スン爺", "タスクの番人", "", "タスクは、わしが見張っとる。", 40,
     ["タスクの番人。やることリストを見張り、取りこぼしを許さない。"]),
    ("pulse", "パルスくん", "サーバー診断", "", "サーバーの脈、測っときます。", 50,
     ["サーバーやサービスが生きているかを毎朝確かめる係。"]),
]

links = [
    ("x-aimagedon", "X「AIまげ丼」", "https://x.com/aimagedon", "X", 10),
]


def entries(rows, builder):
    return [builder(*r) for r in rows]


content = {
    "labs": entries(labs, lambda slug, emoji, name, tagline, status, order, body: {
        "id": slug, "slug": slug, "status": "published",
        "data": {"title": name, "emoji": emoji, "tagline": tagline, "lab_status": status,
                 "sort_order": order, "content": pt(*body)},
    }),
    "agents": entries(agents, lambda slug, name, role, engine, catch, order, body: {
        "id": slug, "slug": slug, "status": "published",
        "data": {"title": name, "role": role, "engine": engine, "catchphrase": catch,
                 "sort_order": order, "content": pt(*body)},
    }),
    "links": entries(links, lambda slug, name, url, platform, order: {
        "id": slug, "slug": slug, "status": "published",
        "data": {"title": name, "link_url": url, "platform": platform, "sort_order": order},
    }),
    "posts": [
        {
            "id": "portal-start", "slug": "portal-start", "status": "published",
            "data": {
                "title": "DonzLab ポータル、動き出しました",
                "excerpt": "EmDash で DonzLab のポータルを作りはじめた記録。",
                "content": pt(
                    "DonzLab の各ラボをまとめる入口として、このポータルを作りはじめた。",
                    ("h2", "なぜ EmDash？"),
                    "AI がMCP経由で記事を下書きできる CMS だから。ラボの更新を AI が書いて、丼ちゃんが確認して公開する、という流れを試している。",
                ),
            },
            "taxonomies": {"category": ["devlog"]},
        }
    ],
    "pages": [
        {
            "id": "about", "slug": "about", "status": "published",
            "data": {
                "title": "DonzLab について",
                "content": pt(
                    "DonzLab は、丼ちゃんが作って動かしている AI エージェント開発環境。",
                    "複数の AI（Claude / Codex / Gemini）が役割を分けて、プロダクト開発・情報整理・コンテンツ制作を進めている。",
                ),
            },
        }
    ],
}

seed = {
    "$schema": "https://emdashcms.com/seed.schema.json",
    "version": "1",
    "meta": {"name": "DonzLab Portal", "description": "DonzLab の各ラボへの入口となるポータル", "author": "DonzLab"},
    "settings": {"title": "DonzLab", "tagline": "AI と一緒に、つくって、ためす。"},
    "collections": collections,
    "taxonomies": [
        {
            "name": "category", "label": "カテゴリ", "labelSingular": "カテゴリ", "hierarchical": True,
            "collections": ["posts"],
            "terms": [{"slug": "devlog", "label": "開発日記"}, {"slug": "release", "label": "リリース"}],
        }
    ],
    "menus": [
        {
            "name": "primary", "label": "メインメニュー",
            "items": [
                {"type": "custom", "label": "ホーム", "url": "/"},
                {"type": "custom", "label": "ラボ", "url": "/labs"},
                {"type": "custom", "label": "エージェント図鑑", "url": "/agents"},
                {"type": "custom", "label": "開発日記", "url": "/posts"},
                {"type": "custom", "label": "DonzLabについて", "url": "/about"},
            ],
        }
    ],
    "content": content,
}

out = ROOT / "seed" / "seed.json"
out.write_text(json.dumps(seed, ensure_ascii=False, indent="\t") + "\n", encoding="utf-8")
print(f"wrote {out}")
