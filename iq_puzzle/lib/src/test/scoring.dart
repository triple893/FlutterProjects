import 'dart:math';

import 'package:flutter/foundation.dart';

/// 正答数から娯楽用の推定IQを出す。
///
/// 母集団の正答数が平均 [populationMean]・標準偏差 [populationSd] の正規分布に
/// 従うと仮定した単純な換算で、標準化された知能検査の結果ではない。
@immutable
class ScoreReport {
  const ScoreReport._({
    required this.correct,
    required this.total,
    required this.iq,
    required this.percentile,
  });

  factory ScoreReport.fromCorrect(int correct, int total) {
    final mean = total * populationMean;
    final sd = total * populationSd;
    final z = (correct - mean) / sd;
    final iq = (100 + 15 * z).round().clamp(minIq, maxIq);
    // 推定IQに合わせてパーセンタイルも同じ範囲に丸める。
    final clampedZ = (iq - 100) / 15;
    return ScoreReport._(
      correct: correct,
      total: total,
      iq: iq,
      percentile: _normalCdf(clampedZ) * 100,
    );
  }

  /// 母集団の平均正答率と標準偏差（正答率ベース）。
  static const double populationMean = 0.5;
  static const double populationSd = 1 / 6;
  static const int minIq = 55;
  static const int maxIq = 145;

  final int correct;
  final int total;
  final int iq;

  /// 推定で自分より下にいる人の割合（%）。
  final double percentile;

  /// 「上位 x%」の x。
  double get topPercent => 100 - percentile;

  /// Abramowitz & Stegun 7.1.26 による誤差関数の近似（誤差 1.5e-7 以下）。
  static double _erf(double x) {
    final sign = x < 0 ? -1 : 1;
    final ax = x.abs();
    final t = 1 / (1 + 0.3275911 * ax);
    final y =
        1 -
        (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t -
                        0.284496736) *
                    t +
                0.254829592) *
            t *
            exp(-ax * ax);
    return sign * y;
  }

  static double _normalCdf(double z) => 0.5 * (1 + _erf(z / sqrt2));
}
