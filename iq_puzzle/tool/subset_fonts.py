#!/usr/bin/env python3
"""lib/ で使っている文字だけを含む Noto Sans JP のサブセットを作る。

Web版が日本語フォントを外部（fonts.gstatic.com）から取得しなくて済むよう、
アプリに同梱するフォントを小さく保つためのスクリプト。
UIの文言を変えたら再実行し、assets/fonts/ をコミットする。

    pip install fonttools
    curl -LO 'https://raw.githubusercontent.com/google/fonts/main/ofl/notosansjp/NotoSansJP%5Bwght%5D.ttf'
    python3 tool/subset_fonts.py 'NotoSansJP[wght].ttf'
"""

import pathlib
import sys

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "fonts"
WEIGHTS = {"Regular": 400, "Bold": 700}


def used_characters() -> str:
    chars = {chr(c) for c in range(0x20, 0x7F)}  # 数字・英字・記号は常に含める
    for path in sorted((ROOT / "lib").rglob("*.dart")):
        chars.update(c for c in path.read_text(encoding="utf-8") if ord(c) > 0x7F)
    return "".join(sorted(chars))


def main(source: str) -> None:
    text = used_characters()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "subset_chars.txt").write_text(text + "\n", encoding="utf-8")
    for name, weight in WEIGHTS.items():
        font = instancer.instantiateVariableFont(TTFont(source), {"wght": weight})
        options = subset.Options()
        options.layout_features = ["*"]
        subsetter = subset.Subsetter(options)
        subsetter.populate(text=text)
        subsetter.subset(font)
        target = OUT / f"NotoSansJP-{name}.ttf"
        font.save(target)
        print(f"{target.relative_to(ROOT)}: {target.stat().st_size} bytes")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
