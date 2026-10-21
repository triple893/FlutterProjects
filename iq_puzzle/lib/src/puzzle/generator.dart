import 'dart:math';

import 'panel.dart';
import 'puzzle.dart';

/// 難易度ごとの出題パラメータ。
class LevelSpec {
  const LevelSpec({
    required this.varyingAttributes,
    required this.optionCount,
    required this.allowRowShift,
    required this.allowArithmetic,
  });

  /// 規則によって変化する属性の数。
  final int varyingAttributes;

  /// 選択肢の数。
  final int optionCount;

  /// 個数の等差規則で、行ごとに開始値をずらすか。
  final bool allowRowShift;

  /// 個数に足し算・引き算の規則を使うか。
  final bool allowArithmetic;

  static const int minLevel = 1;
  static const int maxLevel = 5;

  static LevelSpec of(int level) => switch (level) {
    1 => const LevelSpec(
      varyingAttributes: 1,
      optionCount: 6,
      allowRowShift: false,
      allowArithmetic: false,
    ),
    2 => const LevelSpec(
      varyingAttributes: 2,
      optionCount: 6,
      allowRowShift: true,
      allowArithmetic: false,
    ),
    3 => const LevelSpec(
      varyingAttributes: 2,
      optionCount: 8,
      allowRowShift: true,
      allowArithmetic: true,
    ),
    4 => const LevelSpec(
      varyingAttributes: 3,
      optionCount: 8,
      allowRowShift: true,
      allowArithmetic: true,
    ),
    5 => const LevelSpec(
      varyingAttributes: 4,
      optionCount: 8,
      allowRowShift: true,
      allowArithmetic: true,
    ),
    _ => throw RangeError.range(level, minLevel, maxLevel, 'level'),
  };
}

/// シード付き乱数から行列推理問題を生成する。同じシードなら同じ問題列になる。
class PuzzleGenerator {
  PuzzleGenerator(int seed) : _rng = Random(seed);

  final Random _rng;

  /// [count] 問を、難易度1から5へ均等に上げながら生成する。
  List<Puzzle> generateTest(int count) => [
    for (var i = 0; i < count; i++)
      generate(LevelSpec.minLevel + i * LevelSpec.maxLevel ~/ count),
  ];

  Puzzle generate(int level) {
    final spec = LevelSpec.of(level);
    final varying = (List.of(
      Attribute.values,
    )..shuffle(_rng)).take(spec.varyingAttributes).toSet();

    final rules = <Attribute, RuleKind>{};
    final values = <Attribute, List<List<int>>>{};
    for (final attribute in Attribute.values) {
      final (kind, grid) = varying.contains(attribute)
          ? _varyingRule(attribute, spec)
          : (RuleKind.constant, _constant(_randomValue(attribute)));
      rules[attribute] = kind;
      values[attribute] = grid;
    }

    final grid = [
      for (var r = 0; r < 3; r++)
        [
          for (var c = 0; c < 3; c++)
            Panel(
              shape: ShapeKind.values[values[Attribute.shape]![r][c]],
              count: values[Attribute.count]![r][c],
              fill: FillStyle.values[values[Attribute.fill]![r][c]],
              size: SizeLevel.values[values[Attribute.size]![r][c]],
            ),
        ],
    ];

    final answer = grid[2][2];
    final distractors = _distractors(
      answer,
      grid,
      varying,
      spec.optionCount - 1,
    );
    final answerIndex = _rng.nextInt(spec.optionCount);
    final options = [...distractors]..insert(answerIndex, answer);

    return Puzzle(
      level: level,
      grid: grid,
      options: options,
      answerIndex: answerIndex,
      rules: rules,
    );
  }

  (RuleKind, List<List<int>>) _varyingRule(
    Attribute attribute,
    LevelSpec spec,
  ) {
    switch (attribute) {
      case Attribute.shape:
        final shapes = List.of(ShapeKind.values)..shuffle(_rng);
        return (
          RuleKind.distribution,
          _latinSquare([for (final s in shapes.take(3)) s.index]),
        );
      case Attribute.fill:
        return (
          RuleKind.distribution,
          _latinSquare(
            [for (final f in FillStyle.values) f.index]..shuffle(_rng),
          ),
        );
      case Attribute.size:
        if (spec.allowRowShift && _rng.nextBool()) {
          return (
            RuleKind.distribution,
            _latinSquare(
              [for (final s in SizeLevel.values) s.index]..shuffle(_rng),
            ),
          );
        }
        final ascending = _rng.nextBool();
        return (
          RuleKind.progression,
          [
            for (var r = 0; r < 3; r++)
              [for (var c = 0; c < 3; c++) ascending ? c : 2 - c],
          ],
        );
      case Attribute.count:
        final roll = _rng.nextInt(spec.allowArithmetic ? 3 : 2);
        if (roll == 2) return (RuleKind.arithmetic, _arithmeticCounts());
        if (roll == 1 && spec.allowRowShift) {
          final counts = List.generate(maxCount, (i) => i + 1)..shuffle(_rng);
          return (RuleKind.distribution, _latinSquare(counts.take(3).toList()));
        }
        return (RuleKind.progression, _progressionCounts(spec.allowRowShift));
    }
  }

  List<List<int>> _constant(int value) => [
    for (var r = 0; r < 3; r++) [value, value, value],
  ];

  /// 各行・各列に [values] が1回ずつ現れる配置。向き（右上がり／右下がり）はランダム。
  List<List<int>> _latinSquare(List<int> values) {
    final shift = _rng.nextBool() ? 1 : 2;
    return [
      for (var r = 0; r < 3; r++)
        [for (var c = 0; c < 3; c++) values[(c + r * shift) % 3]],
    ];
  }

  List<List<int>> _progressionCounts(bool allowRowShift) {
    final step = _rng.nextBool() ? 1 : -1;
    final rowStep = allowRowShift ? _rng.nextInt(2) : 0;
    bool fits(int start) => [
      for (var r = 0; r < 3; r++)
        for (var c = 0; c < 3; c++) start + r * rowStep + c * step,
    ].every((v) => v >= 1 && v <= maxCount);
    final starts = [
      for (var s = 1; s <= maxCount; s++)
        if (fits(s)) s,
    ];
    final start = starts[_rng.nextInt(starts.length)];
    return [
      for (var r = 0; r < 3; r++)
        [for (var c = 0; c < 3; c++) start + r * rowStep + c * step],
    ];
  }

  List<List<int>> _arithmeticCounts() {
    final add = _rng.nextBool();
    final rows = <List<int>>[];
    while (rows.length < 3) {
      final a = 1 + _rng.nextInt(maxCount);
      final b = 1 + _rng.nextInt(maxCount);
      final c = add ? a + b : a - b;
      final duplicate = rows.any((row) => row[0] == a && row[1] == b);
      // 上2行の3列目が同じだと「3列目は常に同じ値」とも読めてしまう。
      final ambiguous = rows.length == 1 && rows[0][2] == c;
      if (c < 1 || c > maxCount || duplicate || ambiguous) continue;
      rows.add([a, b, c]);
    }
    return rows;
  }

  int _randomValue(Attribute attribute) => switch (attribute) {
    Attribute.shape => _rng.nextInt(ShapeKind.values.length),
    Attribute.count => 1 + _rng.nextInt(4),
    Attribute.fill => _rng.nextInt(FillStyle.values.length),
    Attribute.size => _rng.nextInt(SizeLevel.values.length),
  };

  /// [answer] と異なる、もっともらしい誤答を [n] 個作る。
  ///
  /// 「隣のマスをそのまま写す」罠、変化している属性を1つだけずらしたもの、
  /// 2つの属性をずらしたもの、の順に優先する。
  List<Panel> _distractors(
    Panel answer,
    List<List<Panel>> grid,
    Set<Attribute> varying,
    int n,
  ) {
    final picked = <Panel>{};
    void addFrom(Iterable<Panel> candidates, int limit) {
      for (final candidate in candidates) {
        if (picked.length >= limit) return;
        if (candidate != answer) picked.add(candidate);
      }
    }

    final traps = [grid[2][1], grid[1][2]];
    final singles = <Panel>[
      for (final attribute in Attribute.values)
        for (final value in _alternatives(attribute, answer, grid))
          answer.withValue(attribute, value),
    ]..shuffle(_rng);
    // 変化している属性のずらしを先に出す。
    singles.sort(
      (a, b) =>
          _varyingDiffs(b, answer, varying) - _varyingDiffs(a, answer, varying),
    );

    final doubles = <Panel>[
      for (final first in Attribute.values)
        for (final second in Attribute.values)
          if (first.index < second.index)
            for (final v1 in _alternatives(first, answer, grid))
              for (final v2 in _alternatives(second, answer, grid))
                answer.withValue(first, v1).withValue(second, v2),
    ]..shuffle(_rng);

    addFrom(traps, 1 + _rng.nextInt(2));
    // 1属性ずらしばかりだと「他の選択肢と最も共通点が多いもの」が正解だと
    // 見抜けてしまうため、2属性ずらしを必ず混ぜる。
    addFrom(singles, n - (n ~/ 3));
    addFrom(doubles, n);
    addFrom(singles, n);

    return picked.toList()..shuffle(_rng);
  }

  int _varyingDiffs(Panel panel, Panel answer, Set<Attribute> varying) =>
      varying.where((a) => panel.valueOf(a) != answer.valueOf(a)).length;

  /// [answer] の [attribute] を置き換える候補値。行列内に現れる値を優先する。
  List<int> _alternatives(
    Attribute attribute,
    Panel answer,
    List<List<Panel>> grid,
  ) {
    final current = answer.valueOf(attribute);
    final seen = <int>{
      for (final row in grid)
        for (final panel in row) panel.valueOf(attribute),
    };
    final Iterable<int> domain = switch (attribute) {
      Attribute.shape =>
        seen.length > 1
            ? seen
            : List.generate(ShapeKind.values.length, (i) => i),
      Attribute.count => {
        ...seen,
        current - 1,
        current + 1,
      }.where((v) => v >= 1 && v <= maxCount),
      Attribute.fill => List.generate(FillStyle.values.length, (i) => i),
      Attribute.size => List.generate(SizeLevel.values.length, (i) => i),
    };
    return [
      for (final v in domain)
        if (v != current) v,
    ];
  }
}
