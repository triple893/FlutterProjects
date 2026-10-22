"""Generate seed/seed.json for the Don'z Lab portal.

Run: python3 scripts/build-seed.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

WORLDS = ["circuit", "strings", "sound", "kitchen", "signal", "constellation", "device", "stage", "business"]


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


def sort_field():
    return {"slug": "sort_order", "label": "並び順", "type": "integer", "defaultValue": 100}


collections = [
    {
        "slug": "labs",
        "label": "ラボ",
        "labelSingular": "ラボ",
        "urlPattern": "/labs/{slug}",
        "supports": ["drafts", "revisions", "preview", "search", "seo"],
        "fields": [
            title_field("ラボ名"),
            {"slug": "name_en", "label": "英語のひとこと（世界向け）", "type": "string", "searchable": True},
            {"slug": "tagline", "label": "ひとこと", "type": "string", "searchable": True},
            {
                "slug": "lab_status",
                "label": "ステータス",
                "type": "select",
                "defaultValue": "準備中",
                "validation": {"options": ["稼働中", "開発中", "準備中"]},
            },
            {
                "slug": "world",
                "label": "世界観（背景グラフィック）",
                "type": "select",
                "defaultValue": "circuit",
                "validation": {"options": WORLDS},
            },
            {"slug": "accent", "label": "テーマカラー（#rrggbb）", "type": "string"},
            {"slug": "thumbnail", "label": "サムネイル画像", "type": "image"},
            {"slug": "hero_image", "label": "メインビジュアル", "type": "image"},
            {"slug": "lab_url", "label": "ラボの外部リンク", "type": "url"},
            sort_field(),
            {"slug": "content", "label": "紹介文", "type": "portableText", "searchable": True},
            {
                "slug": "works",
                "label": "この世界でやっていること",
                "type": "repeater",
                "validation": {
                    "maxItems": 12,
                    "subFields": [
                        {"slug": "name", "label": "名前", "type": "string", "required": True},
                        {"slug": "summary", "label": "説明", "type": "text"},
                        {"slug": "state", "label": "状態", "type": "select", "options": ["稼働中", "開発中", "構想中"]},
                        {"slug": "link", "label": "リンク", "type": "url"},
                    ],
                },
            },
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
            {"slug": "name_en", "label": "英語名", "type": "string"},
            {"slug": "epithet", "label": "二つ名", "type": "string", "searchable": True},
            {
                "slug": "layer",
                "label": "所属",
                "type": "select",
                "defaultValue": "街",
                "validation": {"options": ["本陣", "天", "街", "復活待ち"]},
            },
            {"slug": "role", "label": "担当", "type": "string", "searchable": True},
            {"slug": "engine", "label": "中の人（AI）", "type": "string"},
            {"slug": "portrait", "label": "肖像画", "type": "image"},
            {"slug": "catchphrase", "label": "ひとこと", "type": "string", "searchable": True},
            sort_field(),
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
            sort_field(),
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
            {
                "slug": "layout",
                "label": "レイアウト",
                "type": "select",
                "defaultValue": "business",
                "validation": {"options": ["business", "world"]},
            },
            {"slug": "lead", "label": "リード文", "type": "text"},
            {"slug": "content", "label": "本文", "type": "portableText", "searchable": True},
        ],
    },
]


def work(name, summary, state, link=None):
    row = {"name": name, "summary": summary, "state": state}
    if link:
        row["link"] = link
    return row


# slug, name, tagline, status, world, accent, order, intro paragraphs, works
labs = [
    ("donz-corelab", "DonzCorelab", "城の中枢。AI たちが動くための基盤", "稼働中", "circuit", "#d9b45a", 10,
     ["Don'z Lab 全体を支える中枢。インフラ、データベース、エージェント設計をまとめて扱う。",
      "ここで決めた仕組みの上で、すべてのラボが動いている。"],
     [work("インフラ要件定義書", "城の設計図。何をどこで動かすかを決める", "稼働中"),
      work("エージェント設計", "天と街の二層で、AI の役割と名前を決める", "稼働中"),
      work("商品候補DB", "ラボから生まれるプロダクトの候補を管理する", "稼働中")]),
    # ChordSheetMaker and composition are rooms inside the music world, not labs of their own.
    ("donz-music-lab", "Don'z MusicLab", "音楽の世界。耳コピからタブ譜、作曲まで", "開発中", "strings", "#f0a24b", 20,
     ["音楽にまつわる道具と制作を、AI と一緒に進める世界。耳コピした音源をタブ譜に起こす道具も、作曲も、すべてこの中にある。"],
     [work("ChordSheetMaker", "耳コピした音源を、ギター・ベースのタブ譜に起こす道具。楽譜が出回っていない曲に強い", "開発中"),
      work("作曲の部屋", "作曲エージェントと一緒に、詞や情景から曲の種をつくり、形にしていく", "開発中")]),
    ("cooking-lab", "Don'z 料理Lab", "台所の世界。レシピを AI と研究する", "準備中", "kitchen", "#f2795b", 30,
     ["料理とレシピ配信を AI と一緒に研究するラボ。"],
     [work("レシピ配信", "研究したレシピを動画や SNS で届ける", "構想中")]),
    ("donz-marketing-lab", "DonzMarketingLab", "発信の世界。声を遠くへ届ける", "稼働中", "signal", "#ff6fae", 50,
     ["X・YouTube・TikTok などの発信を、AI と組んで設計・検証するラボ。"],
     [work("SNS 戦略", "どこで、何を、どう届けるかを設計する", "稼働中"),
      work("X「AIまげ丼」", "AI と遊びながらつくる日々を発信する", "稼働中", "https://x.com/aimagedon")]),
    # Re:IDOL: idol-side information only (public facts). Family-side content stays off this site.
    # Publish only after the group's management has approved; until then the lab stays 準備中 and
    # lab_url is left empty (set it to the fan portal's gate page once it is public).
    ("reidol-fan-portal", "Re:IDOL ファンポータル", "ステージの世界。推しを、全力で応援する", "準備中", "stage", "#e8384f", 55,
     ["「日本を景気良くするアイドル」Re:IDOL を応援する、非公式（アンオフィシャル）のファンポータル。",
      "メンバー紹介、ディスコグラフィ、スケジュールを、ファンの目線でまとめている。ポータル本体は専用のトップページから入る。"],
     [work("メンバー紹介", "メンバーカラーとプロフィールで、一人ひとりを紹介する", "稼働中"),
      work("ディスコグラフィ", "1st デジタルアルバム『Re:START!!』（全8曲）ほか", "稼働中"),
      work("スケジュール", "2026年8月7日 SHIBUYA DIVE のデビューライブから、これからの出演まで", "稼働中")]),
    ("llm-cost-lab", "LLM比較Lab", "LLM のコストと性能を、数字で比べる", "開発中", "business", "#2f6fed", 60,
     ["いろいろな LLM のコストパフォーマンスを測り、用途ごとに比べるラボ。"],
     [work("コスパ・ベンチマーク", "同じ課題を複数の LLM に解かせ、費用と品質を測る", "開発中")]),
    ("knowledge-graph", "Graphify 知識基盤", "記憶の世界。知識を星座のようにつなぐ", "稼働中", "constellation", "#7c8cff", 70,
     ["Obsidian と Graphify で、Don'z Lab の知識をつないでいく基盤。",
      "記憶の女神ムネモシュネの領域。もう二度と、記憶を失わせない。"],
     [work("知識の神経網", "資料どうしのつながりをグラフにする", "稼働中"),
      work("ナレッジカードの自動生成", "グラフから読みやすいカードを自動でつくる", "稼働中")]),
    ("flutter-project", "FlutterProject", "アプリの世界。AI と一緒にスマホアプリをつくる", "開発中", "device", "#4fc3f7", 80,
     ["Flutter で Android / iOS 両対応のアプリを AI と一緒に作るプロジェクト。"],
     [work("クラウド開発環境", "GitHub Codespaces で、PC を選ばず開発できる", "稼働中"),
      work("Android / iOS 両対応", "ひとつのコードで両方のスマホに届ける", "開発中")]),
]

# slug, name, epithet, layer, role, engine, catchphrase, order, profile paragraphs
agents = [
    ("kuro", "クロちゃん", "社長", "本陣", "意味・判断・方針", "Claude", "意味と方針は、クロに聞け。", 10,
     ["Don'z Lab の CEO。日本語、戦略、大きな判断、言葉の精度を担う。"]),
    ("kode", "コデちゃん", "総合管制", "本陣", "実装・査読・進捗", "Codex", "実装と進捗は、コデが握る。", 20,
     ["Don'z Lab の COO。実装、査読、ファイル管理、進捗の見える化を担う。"]),
    ("gura", "グラちゃん", "軍師", "本陣", "調査・クリエイティブ", "Gemini", "大量調査と素材づくりは、グラにおまかせ。", 30,
     ["Don'z Lab の CSO。爆速の調査、HTML、画像、マーケ、並列処理を担う。"]),
    ("themis", "テミスちゃん", "憲法と法務の守護神", "天", "ルール監査・法務アドバイザー", "", "その行い、法に照らして正しいか。", 40,
     ["感情を排し、憲法と法律への準拠を絶対とする審判。",
      "判定のたびに誰かを落とす。頬の光の筋はその痛みの跡であり、冷徹さの代償である。"]),
    ("mnemosyne", "ムネモちゃん", "記憶の女神", "天", "記憶・引き継ぎ・知識グラフ", "", "あれ、どうなった？の前に。", 50,
     ["揮発するものを記録に変え、すべてのセッションへ配る。永続化は Don'z Lab のコア思想であり、彼女はその体現。",
      "テミスとは姉妹。失われた記憶を悼み、二度と失わせないことを己の務めとしている。"]),
    ("stratica", "ストラティカ", "北極星の番人", "天", "意思決定支援・北極星ゴール整合", "", "北極星への最短距離を計算する。", 60,
     ["構造とロジックで、北極星への最短距離を計算する丼ちゃん専属の軍師。迷子になったら、彼女が連れ戻す。"]),
    ("sunjii", "スン爺", "GOAL JASON — GOD OF PLANNING", "街", "タスクの番人", "", "あれどうなった？と言わせたら、わしの負けじゃ。", 70,
     ["動いていない案件を見つけ、朝いちで突きつける。頑固で口うるさいが、誰よりも案件の面倒を見ている。"]),
    ("gen-san", "道具屋源さん", "横断能力の棚", "街", "技術・手法の転用", "", "それ、前に使うたやつが使えるばい。", 80,
     ["一度使えた技術や手法を工具として棚に並べ、別のラボへ転用できる形にしておく店主。"]),
    ("pulse", "パルスくん", "衛生兵", "街", "サーバーの死活監視", "", "サーバー落ちた？すぐ行きます！", 90,
     ["戦場のムードメーカー。サーバーが落ちると真っ先に駆けつける。"]),
    ("chrono", "クロノ", "時の守護", "復活待ち", "締切・時間の守護", "", "", 100,
     ["締切と時間を守る天の神。原生体は失われたが、毎朝の台帳監査とカレンダー同期の役目として、復活を待っている。"]),
]

# English lines shown beside the Japanese ones, so the site reads for visitors outside Japan.
NAME_EN = {
    "donz-corelab": "The core of the castle",
    "donz-music-lab": "Ear-copy, tabs & composition",
    "cooking-lab": "The kitchen lab",
    "donz-marketing-lab": "Signals to the world",
    "reidol-fan-portal": "Unofficial fan portal",
    "llm-cost-lab": "Cost × quality benchmarks",
    "knowledge-graph": "A constellation of memory",
    "flutter-project": "Apps, built with AI",
    "kuro": "Kuro", "kode": "Kode", "gura": "Gura",
    "themis": "Themis", "mnemosyne": "Mnemosyne", "stratica": "Stratica",
    "sunjii": "Sun-jii", "gen-san": "Gen-san", "pulse": "Pulse", "chrono": "Chrono",
}

links = [
    ("x-aimagedon", "X「AIまげ丼」", "https://x.com/aimagedon", "X", 10),
]


content = {
    "labs": [
        {
            "id": slug, "slug": slug, "status": "published",
            "data": {"title": name, "name_en": NAME_EN[slug], "tagline": tagline, "lab_status": status, "world": world, "accent": accent,
                     "sort_order": order, "content": pt(*intro), "works": works},
        }
        for slug, name, tagline, status, world, accent, order, intro, works in labs
    ],
    "agents": [
        {
            "id": slug, "slug": slug, "status": "published",
            "data": {"title": name, "name_en": NAME_EN[slug], "epithet": epithet, "layer": layer, "role": role, "engine": engine,
                     "catchphrase": catch, "sort_order": order, "content": pt(*profile)},
        }
        for slug, name, epithet, layer, role, engine, catch, order, profile in agents
    ],
    "links": [
        {
            "id": slug, "slug": slug, "status": "published",
            "data": {"title": name, "link_url": url, "platform": platform, "sort_order": order},
        }
        for slug, name, url, platform, order in links
    ],
    "posts": [
        {
            "id": "portal-start", "slug": "portal-start", "status": "published",
            "data": {
                "title": "Don'z Lab の城、建ちはじめました",
                "excerpt": "各ラボへの入口となるポータルを、EmDash で作りはじめた記録。",
                "content": pt(
                    "Don'z Lab の各ラボをまとめる城として、このポータルを作りはじめた。",
                    ("h2", "なぜ EmDash？"),
                    "AI が MCP 経由で記事を下書きできる CMS だから。ラボの更新を AI が書いて、丼ちゃんが確認して公開する、という流れを試している。",
                ),
            },
            "taxonomies": {"category": ["devlog"]},
        }
    ],
    "pages": [
        {
            "id": "about", "slug": "about", "status": "published",
            "data": {
                "title": "Don'z Lab について",
                "layout": "business",
                "lead": "AI エージェントと人が役割を分けて、プロダクトとコンテンツをつくる開発ラボです。",
                "content": pt(
                    ("h2", "私たちについて"),
                    "Don'z Lab は、丼ちゃんが構築・運用する AI エージェント開発環境です。複数の AI（Claude / Codex / Gemini）が役割を分担し、プロダクト開発・情報整理・法務確認・コンテンツ制作を進めています。",
                    ("h2", "取り組み"),
                    "音楽、料理、発信、アプリ開発、LLM の比較研究まで、テーマごとにラボを立てて活動しています。",
                    ("h2", "お問い合わせ"),
                    "お問い合わせ窓口は準備中です。",
                ),
            },
        }
    ],
}

seed = {
    "$schema": "https://emdashcms.com/seed.schema.json",
    "version": "1",
    "meta": {"name": "Don'z Lab Portal", "description": "Don'z Lab の各ラボへの入口となる城", "author": "Don'z Lab"},
    "settings": {"title": "Don'z Lab", "tagline": "AI と一緒に、つくって、ためす。"},
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
                {"type": "custom", "label": "門", "url": "/labs"},
                {"type": "custom", "label": "神殿と街", "url": "/agents"},
                {"type": "custom", "label": "開発日記", "url": "/posts"},
                {"type": "custom", "label": "私たちについて", "url": "/about"},
            ],
        }
    ],
    "content": content,
}

out = ROOT / "seed" / "seed.json"
out.write_text(json.dumps(seed, ensure_ascii=False, indent="\t") + "\n", encoding="utf-8")
print(f"wrote {out}")
