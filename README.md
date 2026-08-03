# FlutterProject

AIと共に、アイデアを即座に形にするための、モバイルアプリケーション開発プロジェクトです。

AndroidとiOS、そしてWebで動作するクロスプラットフォームアプリを、GitHub Codespaces上のクラウド開発環境で構築します。

## 技術スタック

| 項目 | 内容 |
| --- | --- |
| フレームワーク | Flutter (stable) |
| 言語 | Dart |
| 対応プラットフォーム | Android / iOS / Web |
| 開発環境 | GitHub Codespaces (Dev Container) |
| CI | GitHub Actions |

## 始め方（GitHub Codespaces）

ローカルマシンにFlutter SDKをインストールする必要はありません。

1. このリポジトリをGitHub上で開きます。
2. 緑色の「Code」ボタンをクリックします。
3. 「Codespaces」タブを選択し、「Create codespace」をクリックします。
4. `.devcontainer/devcontainer.json` に従って開発環境が自動構築され、ブラウザ上でVS Codeが起動します。

## 開発コマンド

```bash
# 依存パッケージの取得
flutter pub get

# 静的解析
flutter analyze

# テスト実行
flutter test

# Webプレビュー（Codespacesではポート8080が自動で転送されます）
flutter run -d web-server --web-port=8080 --web-hostname=0.0.0.0

# Webのリリースビルド
flutter build web --release
```

## ディレクトリ構成

```
.
├── .devcontainer/   # Codespaces 開発環境の定義
├── .github/         # GitHub Actions ワークフロー
├── android/         # Android 固有の設定
├── ios/             # iOS 固有の設定
├── web/             # Web 固有の設定
├── lib/             # アプリケーション本体（Dart）
├── test/            # テスト
└── docs/            # プロジェクトドキュメント
```

## ドキュメント

| ファイル | 内容 |
| --- | --- |
| [docs/GEMINI.md](docs/GEMINI.md) | プロジェクト概要・ビジョン・ロードマップ |
| [docs/PROGRESS.md](docs/PROGRESS.md) | 進捗管理 |
| [docs/DECISION_LOG.md](docs/DECISION_LOG.md) | 意思決定ログ |
| [docs/PROJECT_STATUS_REPORT.md](docs/PROJECT_STATUS_REPORT.md) | ステータスレポート |
