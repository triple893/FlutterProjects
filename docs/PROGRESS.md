# PROGRESS.md - FlutterProject 進捗管理

## 2025年8月8日
- 新規プロジェクト「FlutterProject」を発足しました。
- スマホアプリ開発の拠点として、`F:\GeminiCLI\FlutterProject` フォルダを作成しました。
- 中央開発室の標準に準拠した `docs` フォルダと、その配下に `GEMINI.md`, `PROGRESS.md`, `DECISION_LOG.md`, `README.md`, `PROJECT_STATUS_REPORT.md` の作成を開始しました。

## 2026年10月21日
- 最初のアプリとして、結果まで無料で遊べる行列推理パズル「無料IQパズル」（`iq_puzzle/`）を作成しました。
    - 問題はシード付き乱数で自動生成（5段階・30問・制限時間20分）。
    - 結果画面で推定IQ・上位何%か・難易度別の正答数を表示し、各問題の正解と規則を解説します。
    - Web版は外部CDNに依存せず動くよう、CanvasKitと日本語フォントのサブセットを同梱しました。
- GitHub Actions に `iq_puzzle` の format / analyze / test / Webビルドを追加しました。
