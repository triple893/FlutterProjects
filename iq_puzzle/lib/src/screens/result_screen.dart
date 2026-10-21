import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../puzzle/panel.dart';
import '../puzzle/puzzle.dart';
import '../test/test_session.dart';
import '../widgets/matrix_view.dart';
import '../widgets/option_grid.dart';
import 'home_screen.dart';

class ResultScreen extends StatelessWidget {
  const ResultScreen({super.key, required this.session});

  final TestSession session;

  String _shareText() {
    final report = session.report;
    return '無料IQパズルで推定IQ ${report.iq}（上位${_formatTop(report.topPercent)}%）でした！'
        ' 正答 ${report.correct}/${report.total} #無料IQパズル';
  }

  /// 端の値は四捨五入すると「上位0%」「上位100%」になるため小数1桁で出す。
  static String _formatTop(double top) =>
      top < 1 || top > 99 ? top.toStringAsFixed(1) : top.round().toString();

  Future<void> _share(BuildContext context) async {
    await Clipboard.setData(ClipboardData(text: _shareText()));
    if (!context.mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('結果をコピーしました。SNSに貼り付けてシェアできます')),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final report = session.report;
    final levels = session.byLevel;

    return Scaffold(
      appBar: AppBar(title: const Text('結果'), automaticallyImplyLeading: false),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 560),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.symmetric(
                          vertical: 28,
                          horizontal: 16,
                        ),
                        child: Column(
                          children: [
                            Text('推定IQ', style: theme.textTheme.titleMedium),
                            Text(
                              '${report.iq}',
                              key: const ValueKey('iq'),
                              style: theme.textTheme.displayLarge?.copyWith(
                                fontWeight: FontWeight.w800,
                                color: theme.colorScheme.primary,
                              ),
                            ),
                            Text(
                              '上位 ${_formatTop(report.topPercent)}%',
                              style: theme.textTheme.titleLarge,
                            ),
                            const SizedBox(height: 8),
                            Text(
                              '正答 ${report.correct} / ${report.total}',
                              key: const ValueKey('correct'),
                              style: theme.textTheme.bodyLarge,
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    Text('難易度別の正答', style: theme.textTheme.titleMedium),
                    const SizedBox(height: 8),
                    for (final entry in levels.entries)
                      _LevelBar(
                        level: entry.key,
                        correct: entry.value.$1,
                        total: entry.value.$2,
                      ),
                    const SizedBox(height: 20),
                    Row(
                      children: [
                        Expanded(
                          child: FilledButton.icon(
                            onPressed: () => _share(context),
                            icon: const Icon(Icons.share),
                            label: const Text('結果をシェア'),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: OutlinedButton.icon(
                            key: const ValueKey('retry'),
                            onPressed: () => Navigator.of(context)
                                .pushReplacement(
                                  MaterialPageRoute<void>(
                                    builder: (_) => const HomeScreen(),
                                  ),
                                ),
                            icon: const Icon(Icons.refresh),
                            label: const Text('もう一度'),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 24),
                    Text('問題の振り返り', style: theme.textTheme.titleMedium),
                    const SizedBox(height: 4),
                    Text(
                      'タップすると正解と規則の解説が見られます',
                      style: theme.textTheme.bodySmall,
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        for (var i = 0; i < session.questionCount; i++)
                          _ReviewChip(session: session, index: i),
                      ],
                    ),
                    const SizedBox(height: 24),
                    Text(
                      '※ 推定IQは正答数を仮の分布（平均50%・標準偏差約17%）に当てはめた'
                      '娯楽用の目安です。標準化された知能検査の結果ではありません。',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _LevelBar extends StatelessWidget {
  const _LevelBar({
    required this.level,
    required this.correct,
    required this.total,
  });

  final int level;
  final int correct;
  final int total;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          SizedBox(width: 72, child: Text('レベル$level')),
          Expanded(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: LinearProgressIndicator(
                value: total == 0 ? 0 : correct / total,
                minHeight: 10,
              ),
            ),
          ),
          SizedBox(
            width: 52,
            child: Text('$correct/$total', textAlign: TextAlign.end),
          ),
        ],
      ),
    );
  }
}

class _ReviewChip extends StatelessWidget {
  const _ReviewChip({required this.session, required this.index});

  final TestSession session;
  final int index;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final answered = session.answerAt(index) != null;
    final correct = session.isCorrect(index);
    final color = correct
        ? Colors.green.shade600
        : answered
        ? scheme.error
        : scheme.outline;
    return Semantics(
      label:
          '問題${index + 1} ${correct
              ? '正解'
              : answered
              ? '不正解'
              : '未回答'}',
      button: true,
      child: InkWell(
        borderRadius: BorderRadius.circular(8),
        onTap: () => Navigator.of(context).push(
          MaterialPageRoute<void>(
            builder: (_) => ReviewScreen(session: session, index: index),
          ),
        ),
        child: Container(
          width: 44,
          height: 44,
          alignment: Alignment.center,
          decoration: BoxDecoration(
            border: Border.all(color: color, width: 2),
            borderRadius: BorderRadius.circular(8),
            color: color.withValues(alpha: 0.1),
          ),
          child: Text(
            '${index + 1}',
            style: TextStyle(color: color, fontWeight: FontWeight.w700),
          ),
        ),
      ),
    );
  }
}

/// 1問分の正解と規則の解説。
class ReviewScreen extends StatelessWidget {
  const ReviewScreen({super.key, required this.session, required this.index});

  final TestSession session;
  final int index;

  static String _attributeName(Attribute attribute) => switch (attribute) {
    Attribute.shape => '形',
    Attribute.count => '個数',
    Attribute.fill => '塗り',
    Attribute.size => '大きさ',
  };

  static String _ruleText(Attribute attribute, RuleKind rule) => switch (rule) {
    RuleKind.constant => 'すべて同じ',
    RuleKind.progression =>
      attribute == Attribute.count ? '左から右へ1つずつ増える（または減る）' : '左から右へ一定の順で変わる',
    RuleKind.distribution => 'どの行・列にも3種類が1回ずつ現れる',
    RuleKind.arithmetic => '左 ± 中央 = 右（足し算または引き算）',
  };

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final Puzzle puzzle = session.puzzles[index];
    final selected = session.answerAt(index);
    return Scaffold(
      appBar: AppBar(title: Text('問題 ${index + 1}（レベル${puzzle.level}）')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 480),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    MatrixView(puzzle: puzzle, showAnswer: true),
                    const SizedBox(height: 12),
                    Text(
                      selected == null
                          ? '未回答 ・ 正解は ${optionLabel(puzzle.answerIndex)}'
                          : 'あなたの回答 ${optionLabel(selected)} ・ 正解 ${optionLabel(puzzle.answerIndex)}',
                      style: theme.textTheme.titleMedium,
                    ),
                    const SizedBox(height: 12),
                    OptionGrid(
                      puzzle: puzzle,
                      selected: selected,
                      revealCorrect: true,
                    ),
                    const SizedBox(height: 16),
                    Text('規則', style: theme.textTheme.titleMedium),
                    const SizedBox(height: 4),
                    for (final attribute in Attribute.values)
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 2),
                        child: Text(
                          '・${_attributeName(attribute)}：${_ruleText(attribute, puzzle.rules[attribute]!)}',
                        ),
                      ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
