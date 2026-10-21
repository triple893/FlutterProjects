import 'package:flutter_test/flutter_test.dart';
import 'package:iq_puzzle/src/test/scoring.dart';
import 'package:iq_puzzle/src/test/test_session.dart';

void main() {
  group('ScoreReport', () {
    test('average score maps to IQ 100 and the 50th percentile', () {
      final r = ScoreReport.fromCorrect(15, 30);
      expect(r.iq, 100);
      expect(r.percentile, closeTo(50, 0.01));
    });

    test('one SD above average maps to IQ 115', () {
      final r = ScoreReport.fromCorrect(20, 30);
      expect(r.iq, 115);
      expect(r.percentile, closeTo(84.13, 0.05));
    });

    test('is monotonic and clamped', () {
      final iqs = [
        for (var c = 0; c <= 30; c++) ScoreReport.fromCorrect(c, 30).iq,
      ];
      for (var i = 1; i < iqs.length; i++) {
        expect(iqs[i], greaterThanOrEqualTo(iqs[i - 1]));
      }
      expect(iqs.first, ScoreReport.minIq);
      expect(iqs.last, ScoreReport.maxIq);
    });
  });

  group('TestSession', () {
    test('records answers and scores them', () {
      final s = TestSession(seed: 3);
      for (var i = 0; i < s.questionCount; i++) {
        s.goTo(i);
        s.answer(
          i < 20
              ? s.puzzles[i].answerIndex
              : (s.puzzles[i].answerIndex + 1) % s.puzzles[i].options.length,
        );
      }
      expect(s.answeredCount, 30);
      expect(s.correctCount, 20);
      expect(s.byLevel[1], (6, 6));
      expect(s.byLevel[5], (0, 6));
      s.finish();
      expect(s.report.iq, 115);
    });

    test('finishes when time runs out and ignores later input', () {
      final s = TestSession(seed: 3, timeLimit: const Duration(seconds: 2));
      s.tick(const Duration(seconds: 1));
      expect(s.isFinished, isFalse);
      s.tick(const Duration(seconds: 1));
      expect(s.isFinished, isTrue);
      expect(s.remaining, Duration.zero);
      s.answer(0);
      expect(s.answeredCount, 0);
    });

    test('navigation stays in range', () {
      final s = TestSession(seed: 3);
      s.previous();
      expect(s.current, 0);
      s.goTo(29);
      s.next();
      expect(s.current, 29);
    });
  });
}
