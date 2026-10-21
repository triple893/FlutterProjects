import 'package:flutter/material.dart';

import 'src/screens/home_screen.dart';

void main() {
  runApp(const IqPuzzleApp());
}

class IqPuzzleApp extends StatelessWidget {
  const IqPuzzleApp({super.key});

  @override
  Widget build(BuildContext context) {
    const seed = Color(0xFF3F51B5);
    const fontFamily = 'NotoSansJP';
    return MaterialApp(
      title: '無料IQパズル',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        fontFamily: fontFamily,
        colorScheme: ColorScheme.fromSeed(seedColor: seed),
      ),
      darkTheme: ThemeData(
        fontFamily: fontFamily,
        colorScheme: ColorScheme.fromSeed(
          seedColor: seed,
          brightness: Brightness.dark,
        ),
      ),
      home: const HomeScreen(),
    );
  }
}
