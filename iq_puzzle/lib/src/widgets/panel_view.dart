import 'dart:math';

import 'package:flutter/material.dart';

import '../puzzle/panel.dart';

/// [Panel] を正方形のマスに描く。
class PanelView extends StatelessWidget {
  const PanelView({super.key, required this.panel, this.color});

  final Panel panel;

  /// 図形の色。省略時はテーマの文字色。
  final Color? color;

  @override
  Widget build(BuildContext context) {
    return AspectRatio(
      aspectRatio: 1,
      child: CustomPaint(
        painter: PanelPainter(
          panel,
          color ?? Theme.of(context).colorScheme.onSurface,
        ),
      ),
    );
  }
}

class PanelPainter extends CustomPainter {
  PanelPainter(this.panel, this.color);

  final Panel panel;
  final Color color;

  /// 個数ごとの配置（マスを 0〜1 とした中心座標）。
  static const Map<int, List<Offset>> _layouts = {
    1: [Offset(0.5, 0.5)],
    2: [Offset(0.3, 0.5), Offset(0.7, 0.5)],
    3: [Offset(0.5, 0.28), Offset(0.27, 0.72), Offset(0.73, 0.72)],
    4: [Offset(0.3, 0.3), Offset(0.7, 0.3), Offset(0.3, 0.7), Offset(0.7, 0.7)],
    5: [
      Offset(0.24, 0.24),
      Offset(0.76, 0.24),
      Offset(0.5, 0.5),
      Offset(0.24, 0.76),
      Offset(0.76, 0.76),
    ],
    6: [
      Offset(0.2, 0.3),
      Offset(0.5, 0.3),
      Offset(0.8, 0.3),
      Offset(0.2, 0.7),
      Offset(0.5, 0.7),
      Offset(0.8, 0.7),
    ],
  };

  /// 大きさごとの半径（マスの一辺に対する比）。個数によらず一定にして、
  /// 「大きさ」と「個数」が混ざって見えないようにする。
  static double _radiusRatio(SizeLevel size) => switch (size) {
    SizeLevel.small => 0.075,
    SizeLevel.medium => 0.108,
    SizeLevel.large => 0.148,
  };

  @override
  void paint(Canvas canvas, Size size) {
    final side = size.shortestSide;
    final radius = side * _radiusRatio(panel.size);
    final strokeWidth = max(1.5, side * 0.018);
    final stroke = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeJoin = StrokeJoin.round
      ..isAntiAlias = true;
    final fill = Paint()
      ..color = color
      ..style = PaintingStyle.fill
      ..isAntiAlias = true;

    for (final position in _layouts[panel.count]!) {
      final center = Offset(position.dx * side, position.dy * side);
      final path = shapePath(panel.shape, center, radius);
      switch (panel.fill) {
        case FillStyle.solid:
          canvas.drawPath(path, fill);
        case FillStyle.striped:
          _drawStripes(canvas, path, center, radius, strokeWidth);
        case FillStyle.outline:
          break;
      }
      canvas.drawPath(path, stroke);
    }
  }

  void _drawStripes(
    Canvas canvas,
    Path path,
    Offset center,
    double radius,
    double strokeWidth,
  ) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = max(1.0, strokeWidth * 0.7)
      ..isAntiAlias = true;
    final gap = max(strokeWidth * 2.2, radius / 2.6);
    canvas.save();
    canvas.clipPath(path);
    for (var d = -2 * radius; d <= 2 * radius; d += gap) {
      canvas.drawLine(
        center + Offset(d - radius, radius),
        center + Offset(d + radius, -radius),
        paint,
      );
    }
    canvas.restore();
  }

  /// 外接円の半径が [r] になるような図形のパス。
  static Path shapePath(ShapeKind shape, Offset c, double r) {
    switch (shape) {
      case ShapeKind.circle:
        return Path()..addOval(Rect.fromCircle(center: c, radius: r * 0.92));
      case ShapeKind.square:
        return Path()..addRect(
          Rect.fromCenter(center: c, width: r * 1.6, height: r * 1.6),
        );
      case ShapeKind.triangle:
        return _polygon(c, r * 1.08, 3, -pi / 2, dy: r * 0.15);
      case ShapeKind.diamond:
        return _polygon(c, r * 1.05, 4, -pi / 2);
      case ShapeKind.hexagon:
        return _polygon(c, r, 6, 0);
      case ShapeKind.star:
        final path = Path();
        for (var i = 0; i < 10; i++) {
          final rr = i.isEven ? r * 1.05 : r * 0.45;
          final a = -pi / 2 + i * pi / 5;
          final p = c + Offset(cos(a) * rr, sin(a) * rr);
          i == 0 ? path.moveTo(p.dx, p.dy) : path.lineTo(p.dx, p.dy);
        }
        return path..close();
    }
  }

  static Path _polygon(
    Offset c,
    double r,
    int sides,
    double start, {
    double dy = 0,
  }) {
    final path = Path();
    for (var i = 0; i < sides; i++) {
      final a = start + i * 2 * pi / sides;
      final p = c + Offset(cos(a) * r, sin(a) * r + dy);
      i == 0 ? path.moveTo(p.dx, p.dy) : path.lineTo(p.dx, p.dy);
    }
    return path..close();
  }

  @override
  bool shouldRepaint(PanelPainter oldDelegate) =>
      oldDelegate.panel != panel || oldDelegate.color != color;
}
