import 'dart:async';
import 'dart:math';

import 'package:flutter/material.dart';

import '../test/test_session.dart';
import '../widgets/matrix_view.dart';
import '../widgets/option_grid.dart';
import 'result_screen.dart';

class TestScreen extends StatefulWidget {
  const TestScreen({super.key, required this.session});

  final TestSession session;

  @override
  State<TestScreen> createState() => _TestScreenState();
}

class _TestScreenState extends State<TestScreen> {
  static const _tick = Duration(seconds: 1);
  Timer? _timer;

  TestSession get _session => widget.session;

  @override
  void initState() {
    super.initState();
    _session.addListener(_onSessionChanged);
    _timer = Timer.periodic(_tick, (_) => _session.tick(_tick));
  }

  @override
  void dispose() {
    _timer?.cancel();
    _session.removeListener(_onSessionChanged);
    super.dispose();
  }

  void _onSessionChanged() {
    if (_session.isFinished) {
      _timer?.cancel();
      _session.removeListener(_onSessionChanged);
      Navigator.of(context).pushReplacement(
        MaterialPageRoute<void>(
          builder: (_) => ResultScreen(session: _session),
        ),
      );
      return;
    }
    setState(() {});
  }

  void _select(int option) {
    _session.answer(option);
    if (_session.current < _session.questionCount - 1) {
      // 選んだ印が見えるよう少し待ってから次へ。
      final question = _session.current;
      Future<void>.delayed(const Duration(milliseconds: 250), () {
        if (mounted && _session.current == question && !_session.isFinished) {
          _session.next();
        }
      });
    }
  }

  Future<void> _confirmFinish() async {
    final unanswered = _session.questionCount - _session.answeredCount;
    final ok = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('テストを終了しますか？'),
        content: Text(
          unanswered > 0
              ? '未回答が$unanswered問あります。未回答は不正解として採点されます。'
              : 'すべての問題に回答しました。採点します。',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('続ける'),
          ),
          FilledButton(
            key: const ValueKey('confirm-finish'),
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('終了して採点'),
          ),
        ],
      ),
    );
    if (ok == true) _session.finish();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final puzzle = _session.currentPuzzle;
    final remaining = _session.remaining;
    final lowTime = remaining < const Duration(minutes: 2);
    final mm = remaining.inMinutes.toString().padLeft(2, '0');
    final ss = (remaining.inSeconds % 60).toString().padLeft(2, '0');

    final matrix = ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 420),
      child: MatrixView(puzzle: puzzle),
    );
    final options = ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 480),
      child: OptionGrid(
        key: ValueKey('options-${_session.current}'),
        puzzle: puzzle,
        selected: _session.answerAt(_session.current),
        onSelected: _select,
      ),
    );

    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, _) {
        if (!didPop) _confirmFinish();
      },
      child: Scaffold(
        appBar: AppBar(
          automaticallyImplyLeading: false,
          title: Text('問題 ${_session.current + 1} / ${_session.questionCount}'),
          actions: [
            Semantics(
              label: '残り時間 ${remaining.inMinutes}分${remaining.inSeconds % 60}秒',
              child: Chip(
                avatar: Icon(
                  Icons.timer_outlined,
                  size: 18,
                  color: lowTime ? theme.colorScheme.error : null,
                ),
                label: Text(
                  '$mm:$ss',
                  style: TextStyle(
                    fontFeatures: const [FontFeature.tabularFigures()],
                    color: lowTime ? theme.colorScheme.error : null,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ),
            const SizedBox(width: 8),
            TextButton(
              key: const ValueKey('finish'),
              onPressed: _confirmFinish,
              child: const Text('終了'),
            ),
            const SizedBox(width: 8),
          ],
          bottom: PreferredSize(
            preferredSize: const Size.fromHeight(4),
            child: LinearProgressIndicator(
              value: _session.answeredCount / _session.questionCount,
            ),
          ),
        ),
        body: SafeArea(
          child: LayoutBuilder(
            builder: (context, constraints) {
              final wide = constraints.maxWidth >= 820;
              final content = wide
                  ? Row(
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        Expanded(child: Center(child: matrix)),
                        const SizedBox(width: 24),
                        Expanded(child: Center(child: options)),
                      ],
                    )
                  : Column(
                      children: [matrix, const SizedBox(height: 16), options],
                    );
              return SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: ConstrainedBox(
                  constraints: BoxConstraints(
                    minHeight: max(0, constraints.maxHeight - 32),
                  ),
                  child: Center(child: content),
                ),
              );
            },
          ),
        ),
        bottomNavigationBar: SafeArea(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 12),
            child: Row(
              children: [
                OutlinedButton.icon(
                  key: const ValueKey('previous'),
                  onPressed: _session.current > 0 ? _session.previous : null,
                  icon: const Icon(Icons.chevron_left),
                  label: const Text('前へ'),
                ),
                const Spacer(),
                Text(
                  '回答済み ${_session.answeredCount}',
                  style: theme.textTheme.bodySmall,
                ),
                const Spacer(),
                if (_session.current < _session.questionCount - 1)
                  OutlinedButton.icon(
                    key: const ValueKey('next'),
                    onPressed: _session.next,
                    icon: const Icon(Icons.chevron_right),
                    label: const Text('次へ'),
                  )
                else
                  FilledButton(
                    onPressed: _confirmFinish,
                    child: const Text('採点する'),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
