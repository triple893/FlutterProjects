# DECISION_LOG.md - FlutterProject 意思決定ログ

## 2025年8月8日

- **決定事項:**
    - **クロスプラットフォーム開発フレームワークとして、Flutterを採用することを決定。**
    - **開発環境として、ローカルPCへのインストールを必要としないクラウドベースのGitHub Codespacesを利用することを決定。**

- **背景:**
    - 複数のOS（Android, iOS）に対応するアプリを、効率的に開発する必要があった。
    - 開発者（丼ちゃん）のPCに、複雑な開発環境をインストールする負担をなくし、AIエージェント（あるま）が環境構築を自動化できる方法を模索していた。

- **理由:**
    - **Flutter:** Googleが主導で開発しており、高いパフォーマンスと美しいUIの実現に定評がある。単一のコードベースで複数のプラットフォームに対応できるため、開発効率が飛躍的に向上する。
    - **GitHub Codespaces:** `.devcontainer.json` という設定ファイルを用いることで、開発環境の構築をコード化し、完全に自動化できる。これにより、AIエージェントによるセットアップが可能となり、開発者は本来のアプリケーション開発に集中できる。

- **検証:**
    - AIエージェント（あるま）による事前調査の結果、GitHub Codespaces上で、コマンドライン操作を主体としたFlutter開発環境の自動構築が可能であると判断した。

## 2026年8月3日

- **決定事項:**
    - **Dev Containerのベースイメージを `cirrusci/flutter:latest` から `ghcr.io/cirruslabs/flutter:stable` へ変更することを決定。**
    - **`devcontainer.json` の `extensions` / `settings` を `customizations.vscode` 配下へ移行することを決定。**
    - **`remoteUser` を明示指定せず、ベースイメージ既定のユーザーに従うことを決定。**
    - **Webプレビュー用の転送ポートを 3000 から 8080 に変更することを決定。**
    - **CIをGitHub Actionsで整備し、解析・テスト・Webビルドを自動実行することを決定。**

- **背景:**
    - フェーズ1の総仕上げとして開発環境設定を点検したところ、既存の `devcontainer.json` が現行仕様と乖離しており、このままではCodespacesを起動しても意図通りに動作しない見込みであることが判明した。

- **理由:**
    - **イメージの変更:** Docker Hub の `cirrusci/flutter` は更新が停止しており、現在メンテナンスされているのは GitHub Container Registry 上の `ghcr.io/cirruslabs/flutter` であるため。
    - **`customizations.vscode` への移行:** 現行のDev Container仕様では、トップレベルの `extensions` / `settings` は読み込まれず、拡張機能もエディタ設定も適用されないため。あわせて非推奨の `terminal.integrated.shell.linux` を `terminal.integrated.defaultProfile.linux` へ置き換えた。
    - **`remoteUser` の削除:** 従来指定していた `flutter` ユーザーが新しいイメージに存在する保証がなく、存在しない場合はコンテナの起動自体が失敗するため。既定ユーザーに委ねるほうが安全と判断した。
    - **ポートの変更:** Flutter web の起動コマンドで指定する 8080 に揃え、Codespacesでの自動プレビューを機能させるため。
    - **CIの整備:** ロードマップで将来的な導入を掲げていたが、アプリ本体の追加により解析・テスト対象が生じたため、この時点で導入するのが合理的と判断した。

- **検証:**
    - `ghcr.io/cirruslabs/flutter:stable` がGitHub Container Registry上に存在することを確認した。
    - Flutter 3.44.8 stable（Dart 3.12.2）にて、`flutter analyze`（指摘なし）、`flutter test`（全件成功）、`flutter build web --release`（成功）、`dart format --set-exit-if-changed`（差分なし）を確認した。
    - なお、更新後の `devcontainer.json` によるCodespacesの実起動確認は未実施であり、次のマイルストーンとして残している。
