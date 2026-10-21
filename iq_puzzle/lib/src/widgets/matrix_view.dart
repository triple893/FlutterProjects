import 'package:flutter/material.dart';

import '../puzzle/puzzle.dart';
import 'panel_view.dart';

/// 3×3 の問題行列。右下は「？」または [filledAnswer] で埋める。
class MatrixView extends StatelessWidget {
  const MatrixView({super.key, required this.puzzle, this.showAnswer = false});

  final Puzzle puzzle;

  /// 右下に正解を表示するか（解説用）。
  final bool showAnswer;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final border = BorderSide(color: scheme.outlineVariant);
    return AspectRatio(
      aspectRatio: 1,
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: scheme.surfaceContainerLowest,
          border: Border.fromBorderSide(border),
        ),
        child: Column(
          children: [
            for (var r = 0; r < 3; r++)
              Expanded(
                child: Row(
                  children: [
                    for (var c = 0; c < 3; c++)
                      Expanded(
                        child: DecoratedBox(
                          decoration: BoxDecoration(
                            border: Border(
                              right: c < 2 ? border : BorderSide.none,
                              bottom: r < 2 ? border : BorderSide.none,
                            ),
                          ),
                          child: Padding(
                            padding: const EdgeInsets.all(4),
                            child: r == 2 && c == 2
                                ? _missingCell(context)
                                : PanelView(panel: puzzle.grid[r][c]),
                          ),
                        ),
                      ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _missingCell(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    if (showAnswer) {
      return PanelView(panel: puzzle.answer, color: scheme.primary);
    }
    return Semantics(
      label: '空欄',
      child: Center(
        child: FittedBox(
          child: Text(
            '?',
            style: TextStyle(
              fontSize: 48,
              fontWeight: FontWeight.w700,
              color: scheme.primary,
            ),
          ),
        ),
      ),
    );
  }
}
