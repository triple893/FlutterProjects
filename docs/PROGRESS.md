# PROGRESS.md - FlutterProject 進捗管理

## 2025年8月8日
- 新規プロジェクト「FlutterProject」を発足しました。
- スマホアプリ開発の拠点として、`F:\GeminiCLI\FlutterProject` フォルダを作成しました。
- 中央開発室の標準に準拠した `docs` フォルダと、その配下に `GEMINI.md`, `PROGRESS.md`, `DECISION_LOG.md`, `README.md`, `PROJECT_STATUS_REPORT.md` の作成を開始しました。

## 2026年8月3日
- **フェーズ1「開発基盤の確立」がほぼ完了しました。**
- `devcontainer.json` を現行のDev Containerスキーマに刷新しました。
    - `extensions` / `settings` はトップレベルでは無視されるため、`customizations.vscode` 配下へ移動しました。
    - ベースイメージを、更新が停止している `cirrusci/flutter:latest` から現行の `ghcr.io/cirruslabs/flutter:stable` へ変更しました。
    - 存在しないユーザーを指定して起動失敗するのを避けるため、`remoteUser` の指定を外し、イメージ既定のユーザーに従うようにしました。
    - Webプレビュー用の転送ポートを 3000 から 8080 に変更し、自動プレビューを有効化しました。
- Flutterの初期アプリ（カウンターアプリ）を生成しました（Android / iOS / Web 対応、パッケージ名 `flutter_project`、org `com.triple893`）。
- Flutter 3.44.8 stable（Dart 3.12.2）で以下を確認しました。
    - `flutter analyze`: 指摘なし
    - `flutter test`: 全件成功
    - `flutter build web --release`: ビルド成功
    - `dart format --set-exit-if-changed`: 差分なし
- GitHub Actions による CI（`flutter pub get` → フォーマット確認 → 解析 → テスト → Webビルド）を追加しました。
- リポジトリルートに `README.md` を追加し、技術スタック・開発コマンド・ディレクトリ構成を整理しました。
- `GEMINI.md` に残っていたローカル環境固有のパス（`F:\GeminiCLI\...`）を、リポジトリ相対パスへ修正しました。
- **残課題:** 実際にCodespacesを起動し、環境が自動構築されることの確認（設定変更後の実機検証は未実施）。
