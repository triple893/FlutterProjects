import 'package:flutter/foundation.dart';

import 'panel.dart';

/// 属性に適用される規則の種類。
enum RuleKind {
  /// 全マスで同じ値。
  constant,

  /// 列ごとに一定量ずつ増減する。
  progression,

  /// 各行・各列に3種類の値が1回ずつ現れる（ラテン方陣）。
  distribution,

  /// 3列目 = 1列目 ± 2列目。
  arithmetic,
}

/// 3×3 行列推理問題。右下のマス（`grid[2][2]`）が空欄になる。
@immutable
class Puzzle {
  const Puzzle({
    required this.level,
    required this.grid,
    required this.options,
    required this.answerIndex,
    required this.rules,
  });

  /// 難易度（1〜5）。
  final int level;

  /// 3×3 のパネル。`grid[2][2]` が正解パネル。
  final List<List<Panel>> grid;

  /// 選択肢。`options[answerIndex]` が正解。
  final List<Panel> options;
  final int answerIndex;

  /// 各属性に使われた規則（解説表示用）。
  final Map<Attribute, RuleKind> rules;

  Panel get answer => grid[2][2];
}
