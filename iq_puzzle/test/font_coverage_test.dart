import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

/// 同梱フォントのサブセットに無い文字を使うと、Web版で文字化け（豆腐）になる。
void main() {
  test('bundled font subset covers every character used in lib/', () {
    final covered = File('assets/fonts/subset_chars.txt')
        .readAsStringSync()
        .runes
        .toSet();
    final missing = <String>{};
    for (final file in Directory(
      'lib',
    ).listSync(recursive: true).whereType<File>()) {
      if (!file.path.endsWith('.dart')) continue;
      for (final rune in file.readAsStringSync().runes) {
        if (rune > 0x7F && !covered.contains(rune)) {
          missing.add(String.fromCharCode(rune));
        }
      }
    }
    expect(
      missing,
      isEmpty,
      reason: 'python3 tool/subset_fonts.py でフォントを作り直してください',
    );
  });
}
