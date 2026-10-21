import 'package:flutter_test/flutter_test.dart';
import 'package:iq_puzzle/src/puzzle/generator.dart';
import 'package:iq_puzzle/src/puzzle/panel.dart';
import 'package:iq_puzzle/src/puzzle/puzzle.dart';

List<List<int>> valuesOf(Puzzle p, Attribute a) => [
  for (final row in p.grid) [for (final panel in row) panel.valueOf(a)],
];

void expectRuleHolds(Puzzle p, Attribute a) {
  final v = valuesOf(p, a);
  final rule = p.rules[a]!;
  final reason = '${a.name} ${rule.name} $v';
  switch (rule) {
    case RuleKind.constant:
      expect(v.expand((r) => r).toSet(), hasLength(1), reason: reason);
    case RuleKind.progression:
      final step = v[0][1] - v[0][0];
      expect(step.abs(), 1, reason: reason);
      for (final row in v) {
        expect(row[1] - row[0], step, reason: reason);
        expect(row[2] - row[1], step, reason: reason);
      }
    case RuleKind.distribution:
      final values = v[0].toSet();
      expect(values, hasLength(3), reason: reason);
      for (var i = 0; i < 3; i++) {
        expect(v[i].toSet(), values, reason: reason);
        expect({for (final row in v) row[i]}, values, reason: reason);
      }
    case RuleKind.arithmetic:
      expect(a, Attribute.count, reason: reason);
      final add = v.every((row) => row[0] + row[1] == row[2]);
      final sub = v.every((row) => row[0] - row[1] == row[2]);
      expect(add || sub, isTrue, reason: reason);
      expect(v[0][2] == v[1][2], isFalse, reason: reason);
  }
}

void main() {
  test('generated puzzles are well-formed at every level', () {
    for (var seed = 0; seed < 200; seed++) {
      final generator = PuzzleGenerator(seed);
      for (var level = 1; level <= 5; level++) {
        final p = generator.generate(level);
        final spec = LevelSpec.of(level);

        expect(p.level, level);
        expect(p.options, hasLength(spec.optionCount));
        expect(
          p.options.toSet(),
          hasLength(spec.optionCount),
          reason: 'options must be distinct',
        );
        expect(p.options[p.answerIndex], p.answer);
        expect(p.options.where((o) => o == p.answer), hasLength(1));

        final varying = p.rules.values
            .where((r) => r != RuleKind.constant)
            .length;
        expect(varying, spec.varyingAttributes);
        for (final a in Attribute.values) {
          expectRuleHolds(p, a);
        }
        for (final row in p.grid) {
          for (final panel in row) {
            expect(panel.count, inInclusiveRange(1, maxCount));
          }
        }
        if (!spec.allowArithmetic) {
          expect(p.rules.values, isNot(contains(RuleKind.arithmetic)));
        }
      }
    }
  });

  test('distractors mix single and double attribute changes', () {
    var withDouble = 0;
    for (var seed = 0; seed < 50; seed++) {
      final p = PuzzleGenerator(seed).generate(5);
      final diffs = [
        for (final o in p.options)
          if (o != p.answer)
            Attribute.values
                .where((a) => o.valueOf(a) != p.answer.valueOf(a))
                .length,
      ];
      if (diffs.any((d) => d >= 2)) withDouble++;
    }
    expect(withDouble, 50);
  });

  test('same seed gives the same test', () {
    final a = PuzzleGenerator(42).generateTest(30);
    final b = PuzzleGenerator(42).generateTest(30);
    for (var i = 0; i < 30; i++) {
      expect(a[i].grid, b[i].grid);
      expect(a[i].options, b[i].options);
      expect(a[i].answerIndex, b[i].answerIndex);
    }
  });

  test('test difficulty rises evenly from 1 to 5', () {
    final levels = PuzzleGenerator(7)
        .generateTest(30)
        .map((p) => p.level)
        .toList();
    expect(levels, [for (var l = 1; l <= 5; l++) ...List.filled(6, l)]);
  });

  test('answer position is spread across options', () {
    final positions = {
      for (var seed = 0; seed < 100; seed++)
        PuzzleGenerator(seed).generate(4).answerIndex,
    };
    expect(positions, hasLength(8));
  });
}
