import 'package:flutter/foundation.dart';

import '../puzzle/generator.dart';
import '../puzzle/puzzle.dart';
import 'scoring.dart';

/// 1回分のテスト。問題・回答・残り時間を保持する。
class TestSession extends ChangeNotifier {
  TestSession({
    required this.seed,
    this.questionCount = defaultQuestionCount,
    this.timeLimit = defaultTimeLimit,
  }) : puzzles = PuzzleGenerator(seed).generateTest(questionCount),
       _answers = List<int?>.filled(questionCount, null),
       _remaining = timeLimit;

  static const int defaultQuestionCount = 30;
  static const Duration defaultTimeLimit = Duration(minutes: 20);

  final int seed;
  final int questionCount;
  final Duration timeLimit;
  final List<Puzzle> puzzles;
  final List<int?> _answers;

  int _current = 0;
  Duration _remaining;
  bool _finished = false;

  int get current => _current;
  Puzzle get currentPuzzle => puzzles[_current];
  Duration get remaining => _remaining;
  bool get isFinished => _finished;
  List<int?> get answers => List.unmodifiable(_answers);
  int get answeredCount => _answers.where((a) => a != null).length;

  int? answerAt(int index) => _answers[index];

  bool isCorrect(int index) => _answers[index] == puzzles[index].answerIndex;

  int get correctCount =>
      [for (var i = 0; i < questionCount; i++) isCorrect(i)]
          .where((c) => c)
          .length;

  ScoreReport get report =>
      ScoreReport.fromCorrect(correctCount, questionCount);

  /// 難易度ごとの（正答数, 問題数）。
  Map<int, (int, int)> get byLevel {
    final result = <int, (int, int)>{};
    for (var i = 0; i < questionCount; i++) {
      final level = puzzles[i].level;
      final (correct, total) = result[level] ?? (0, 0);
      result[level] = (correct + (isCorrect(i) ? 1 : 0), total + 1);
    }
    return result;
  }

  void answer(int optionIndex) {
    if (_finished) return;
    _answers[_current] = optionIndex;
    notifyListeners();
  }

  void goTo(int index) {
    if (_finished || index < 0 || index >= questionCount) return;
    _current = index;
    notifyListeners();
  }

  void next() => goTo(_current + 1);
  void previous() => goTo(_current - 1);

  /// 経過時間を進める。時間切れになったら自動で終了する。
  void tick(Duration elapsed) {
    if (_finished) return;
    _remaining -= elapsed;
    if (_remaining <= Duration.zero) {
      _remaining = Duration.zero;
      _finished = true;
    }
    notifyListeners();
  }

  void finish() {
    if (_finished) return;
    _finished = true;
    notifyListeners();
  }
}
