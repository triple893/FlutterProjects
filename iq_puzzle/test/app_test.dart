import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:iq_puzzle/main.dart';
import 'package:iq_puzzle/src/screens/test_screen.dart';
import 'package:iq_puzzle/src/test/test_session.dart';

void main() {
  testWidgets('home screen starts a test', (tester) async {
    await tester.pumpWidget(const IqPuzzleApp());
    expect(find.text('無料 IQパズル'), findsOneWidget);
    await tester.tap(find.byKey(const ValueKey('start')));
    await tester.pumpAndSettle();
    expect(find.text('問題 1 / 30'), findsOneWidget);
    expect(find.text('?'), findsOneWidget);
  });

  testWidgets('answering every question correctly gives the top score', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(1200, 1600);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.reset);

    final session = TestSession(seed: 11);
    await tester.pumpWidget(MaterialApp(home: TestScreen(session: session)));

    for (var i = 0; i < session.questionCount; i++) {
      expect(find.text('問題 ${i + 1} / 30'), findsOneWidget);
      await tester.tap(
        find.byKey(ValueKey('option-${session.puzzles[i].answerIndex}')),
      );
      await tester.pump(const Duration(milliseconds: 300));
      await tester.pumpAndSettle();
    }

    await tester.tap(find.byKey(const ValueKey('finish')));
    await tester.pumpAndSettle();
    expect(find.textContaining('すべての問題に回答しました'), findsOneWidget);
    await tester.tap(find.byKey(const ValueKey('confirm-finish')));
    await tester.pumpAndSettle();

    expect(find.text('145'), findsOneWidget);
    expect(find.text('正答 30 / 30'), findsOneWidget);
    expect(find.text('上位 0.1%'), findsOneWidget);

    await tester.tap(find.text('1').first);
    await tester.pumpAndSettle();
    expect(find.textContaining('レベル1'), findsOneWidget);
    expect(find.text('規則'), findsOneWidget);
  });

  testWidgets('test ends automatically when time runs out', (tester) async {
    final session = TestSession(seed: 5, timeLimit: const Duration(seconds: 3));
    await tester.pumpWidget(MaterialApp(home: TestScreen(session: session)));
    expect(find.text('00:03'), findsOneWidget);
    await tester.pump(const Duration(seconds: 3));
    await tester.pumpAndSettle();
    expect(find.text('結果'), findsOneWidget);
    expect(find.text('正答 0 / 30'), findsOneWidget);
    expect(find.text('上位 99.9%'), findsOneWidget);
  });
}
