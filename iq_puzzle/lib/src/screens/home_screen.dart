import 'package:flutter/material.dart';

import '../test/test_session.dart';
import 'test_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  void _start(BuildContext context) {
    final session = TestSession(seed: DateTime.now().millisecondsSinceEpoch);
    Navigator.of(context).push(
      MaterialPageRoute<void>(builder: (_) => TestScreen(session: session)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final minutes = TestSession.defaultTimeLimit.inMinutes;
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 520),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Icon(
                    Icons.extension,
                    size: 56,
                    color: theme.colorScheme.primary,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    '無料 IQパズル',
                    textAlign: TextAlign.center,
                    style: theme.textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '結果まで完全無料。登録も課金もありません。',
                    textAlign: TextAlign.center,
                    style: theme.textTheme.bodyLarge,
                  ),
                  const SizedBox(height: 32),
                  _InfoRow(
                    icon: Icons.grid_view,
                    text:
                        '${TestSession.defaultQuestionCount}問の行列推理パズル（だんだん難しくなります）',
                  ),
                  _InfoRow(icon: Icons.timer_outlined, text: '制限時間 $minutes分'),
                  const _InfoRow(
                    icon: Icons.lightbulb_outline,
                    text: '縦・横の並びの規則を見つけて、「？」に入る図形を選んでください',
                  ),
                  const _InfoRow(
                    icon: Icons.skip_next_outlined,
                    text: '分からない問題は飛ばして、あとで戻ってこられます',
                  ),
                  const SizedBox(height: 32),
                  FilledButton.icon(
                    key: const ValueKey('start'),
                    onPressed: () => _start(context),
                    icon: const Icon(Icons.play_arrow),
                    label: const Padding(
                      padding: EdgeInsets.symmetric(vertical: 14),
                      child: Text('テストを始める', style: TextStyle(fontSize: 18)),
                    ),
                  ),
                  const SizedBox(height: 24),
                  Text(
                    '※ 推定IQは娯楽用の目安です。医療・教育・採用などで使われる'
                    '標準化された知能検査の代わりにはなりません。',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  const _InfoRow({required this.icon, required this.text});

  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 22, color: Theme.of(context).colorScheme.primary),
          const SizedBox(width: 12),
          Expanded(child: Text(text)),
        ],
      ),
    );
  }
}
