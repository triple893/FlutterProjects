import 'package:flutter/material.dart';

import '../puzzle/puzzle.dart';
import 'panel_view.dart';

const _labels = 'ABCDEFGH';

String optionLabel(int index) => _labels[index];

/// 選択肢のグリッド。[selected] を強調表示し、[correct] があれば正誤も色で示す。
class OptionGrid extends StatelessWidget {
  const OptionGrid({
    super.key,
    required this.puzzle,
    this.selected,
    this.onSelected,
    this.revealCorrect = false,
  });

  final Puzzle puzzle;
  final int? selected;
  final ValueChanged<int>? onSelected;

  /// 正解・不正解を色分けして見せるか（振り返り用）。
  final bool revealCorrect;

  @override
  Widget build(BuildContext context) {
    final columns = puzzle.options.length == 6 ? 3 : 4;
    return GridView.count(
      crossAxisCount: columns,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      mainAxisSpacing: 8,
      crossAxisSpacing: 8,
      childAspectRatio: 0.86,
      children: [
        for (var i = 0; i < puzzle.options.length; i++) _option(context, i),
      ],
    );
  }

  Widget _option(BuildContext context, int index) {
    final scheme = Theme.of(context).colorScheme;
    final isSelected = selected == index;
    final isAnswer = index == puzzle.answerIndex;

    var borderColor = scheme.outlineVariant;
    var background = scheme.surfaceContainerLowest;
    if (revealCorrect && isAnswer) {
      borderColor = Colors.green.shade600;
      background = Colors.green.withValues(alpha: 0.12);
    } else if (revealCorrect && isSelected) {
      borderColor = scheme.error;
      background = scheme.errorContainer.withValues(alpha: 0.5);
    } else if (isSelected) {
      borderColor = scheme.primary;
      background = scheme.primaryContainer.withValues(alpha: 0.6);
    }

    return Semantics(
      button: onSelected != null,
      selected: isSelected,
      label: '選択肢 ${optionLabel(index)}',
      child: Material(
        color: background,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(10),
          side: BorderSide(
            color: borderColor,
            width: isSelected || (revealCorrect && isAnswer) ? 2.5 : 1,
          ),
        ),
        clipBehavior: Clip.antiAlias,
        child: InkWell(
          key: ValueKey('option-$index'),
          onTap: onSelected == null ? null : () => onSelected!(index),
          child: Padding(
            padding: const EdgeInsets.fromLTRB(6, 4, 6, 6),
            child: Column(
              children: [
                Text(
                  optionLabel(index),
                  style: Theme.of(context).textTheme.labelMedium?.copyWith(
                    color: scheme.onSurfaceVariant,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                Expanded(
                  child: Center(child: PanelView(panel: puzzle.options[index])),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
