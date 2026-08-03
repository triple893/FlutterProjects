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

# Android APK のビルド（出力先: build/app/outputs/flutter-apk/app-release.apk）
flutter build apk --release
```

## スマホ（Android）で試す

PCやFlutter SDKは不要です。CIが自動でビルドしたAPKを、スマホから直接ダウンロードしてインストールできます。

**ダウンロード先:** https://github.com/triple893/FlutterProjects/releases/latest

1. スマホのブラウザで上のページを開き、`app-release.apk` をタップ
2. ダウンロードしたファイルを開く
3. 「提供元不明のアプリ」の許可を求められたら許可する（初回のみ）

`main` ブランチが更新されるたびに、このAPKは自動で最新版に差し替わります。

> **注意**
> - APKはデバッグ用の鍵で署名されているため、Google Playでの配布はできません。手元の端末で動作確認するためのものです。
> - 本リポジトリは公開設定のため、このAPKは誰でもダウンロードできます。
> - プルリクエスト上のビルドはReleaseには公開されません。該当のActions実行ページから、artifact（zip形式・GitHubへのログインが必要）として取得してください。

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
