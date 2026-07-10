# GitHub Copilot Instructions

GitHub Copilot によるコードレビュー用の指示。レビュー時に重点確認すべき点と、フラグすべきでない既知パターンを示す。

## プロジェクト概要

mitmproxy アドオンで HTTP リクエスト / レスポンスを傍受し、MySQL に保存するツール。`ignore_hosts` テーブルで TLS 接続失敗ホストの再チェック間隔を段階的に延長し、重複接続を抑制する。phpMyAdmin で DB を管理する。

## 技術スタック

- 言語: Python 3.x, Bash（Alpine 環境は `ash`）
- 主要ライブラリ: mitmproxy 12.2.3 / aiomysql 0.3.2
- データベース: MySQL 9.7.1、スキーマ管理は sqldef（mysqldef）
- 環境: Docker Compose、phpMyAdmin 5.2.3
- CI/CD: GitHub Actions（`book000/templates` の再利用ワークフローで Docker イメージをビルド）

## レビューで重点確認する点

- **非同期 DB 操作**: DB アクセスは `aiomysql` による `async`/`await` で行うこと。同期的な DB 呼び出しの混入を指摘する。
- **SQL の組み立て**: ユーザー由来の値（傍受した HTTP の host/path/query 等）を SQL に渡す箇所は、文字列連結ではなくプレースホルダでパラメータ化されていること。
- **機密情報のログ出力**: 傍受した HTTP ボディやヘッダには個人情報・認証情報が含まれ得る。これらをログへ出力していないこと。
- **例外処理**: `except: pass` による握りつぶしは最小限であること。握りつぶす場合は理由が妥当か確認する。
- **型ヒントと docstring**: 関数・クラスに型ヒント（可能な限り）と日本語 docstring（PEP 257 準拠）があること。
- **コンテンツタイプ判別**: バイナリは Base64 エンコードして保存する前提。判別ロジック（Binary/JSON/XML/Text）の変更時は保存形式との整合を確認する。

## コーディング規約（レビュー基準）

- Python は PEP 8 準拠。コメント・docstring は日本語、エラーメッセージは英語。
- 日本語と英数字の間には半角スペースを入れる。
- エラーメッセージの先頭に絵文字を付ける既存慣習がある。周辺のエラーメッセージが絵文字付きなら、追加分も内容に即した一文字の絵文字を付けて統一する。
- コミットは [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)（`<description>` は日本語）、ブランチは [Conventional Branch](https://conventional-branch.github.io) 短縮形（`feat/`, `fix/` 等）。

## フラグすべきでない既知パターン

- `compose*.yaml` にハードコードされた DB 認証情報は開発用のデフォルトであり意図的。本番は環境変数で上書きする前提。
- `mitmproxy-addon/entrypoint.sh` で `tls_version_client_min` を明示指定していないのは意図的（明示指定すると OpenSSL ビルドによっては mitmproxy が起動時クラッシュするため）。「TLS 最小バージョン未設定」を欠陥として指摘しない。
- 同 `entrypoint.sh` の異常終了時 30 秒 `sleep` は、ホストへの再起動連打を避けるための意図的な待機。
- Renovate が作成した PR には追加コミットを行わない運用のため、依存バージョン更新の指摘は不要。

## セキュリティ

- DB 認証情報・トークンをコミットしない（開発用デフォルトを除く）。
- mitmproxy の証明書は `data/mitmproxy-conf/` に置かれ `.gitignore` 済み。証明書や鍵をリポジトリに追加しない。
- 傍受データ・ログに個人情報や認証情報を残さない。
