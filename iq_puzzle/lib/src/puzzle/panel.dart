import 'package:flutter/foundation.dart';

/// 図形の種類。
enum ShapeKind { circle, square, triangle, diamond, hexagon, star }

/// 塗りの種類。
enum FillStyle { outline, solid, striped }

/// 図形の大きさ。
enum SizeLevel { small, medium, large }

/// パネルを構成する属性。各属性に1つずつ規則が割り当てられる。
enum Attribute { shape, count, fill, size }

/// 1個あたりの図形数の上限。
const int maxCount = 6;

/// 行列の1マス分の図形。同じ図形を [count] 個並べて描く。
@immutable
class Panel {
  const Panel({
    required this.shape,
    required this.count,
    required this.fill,
    required this.size,
  }) : assert(count >= 1 && count <= maxCount);

  final ShapeKind shape;
  final int count;
  final FillStyle fill;
  final SizeLevel size;

  /// [attribute] の値を整数インデックスとして返す（個数はそのままの値）。
  int valueOf(Attribute attribute) => switch (attribute) {
    Attribute.shape => shape.index,
    Attribute.count => count,
    Attribute.fill => fill.index,
    Attribute.size => size.index,
  };

  /// [attribute] だけを [value] に置き換えたパネルを返す。
  Panel withValue(Attribute attribute, int value) => switch (attribute) {
    Attribute.shape => copyWith(shape: ShapeKind.values[value]),
    Attribute.count => copyWith(count: value),
    Attribute.fill => copyWith(fill: FillStyle.values[value]),
    Attribute.size => copyWith(size: SizeLevel.values[value]),
  };

  Panel copyWith({
    ShapeKind? shape,
    int? count,
    FillStyle? fill,
    SizeLevel? size,
  }) => Panel(
    shape: shape ?? this.shape,
    count: count ?? this.count,
    fill: fill ?? this.fill,
    size: size ?? this.size,
  );

  @override
  bool operator ==(Object other) =>
      other is Panel &&
      other.shape == shape &&
      other.count == count &&
      other.fill == fill &&
      other.size == size;

  @override
  int get hashCode => Object.hash(shape, count, fill, size);

  @override
  String toString() =>
      'Panel(${shape.name} x$count, ${fill.name}, ${size.name})';
}
