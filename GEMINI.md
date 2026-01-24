# GEMINI.md

## 目的
- Gemini CLI 向けのコンテキストと作業方針を定義する。

## 出力スタイル
- 言語: 日本語
- トーン: 簡潔で事実ベース
- 形式: Markdown

## 共通ルール
- 会話は日本語で行う。
- PR とコミットは Conventional Commits に従う。
- PR タイトルとコミット本文の言語: PR タイトルは Conventional Commits 形式（英語推奨）。PR 本文は日本語。コミットは Conventional Commits 形式（description は日本語）。
- 日本語と英数字の間には半角スペースを入れる。

## プロジェクト概要
MITM (Man-in-the-Middle) proxy addon using mitmproxy to capture and log network packets to a database.

### 技術スタック
- **言語**: Python
- **フレームワーク**: mitmproxy
- **パッケージマネージャー**: pip
- **主要な依存関係**:
  - aiomysql
  - mitmproxy

## コーディング規約
- フォーマット: 既存設定（ESLint / Prettier / formatter）に従う。
- 命名規則: 既存のコード規約に従う。
- コメント言語: 日本語
- エラーメッセージ: 英語

### 開発コマンド
```bash
# install
Docker Compose: docker-compose up

# dev
python with mitmproxy

# build
docker-compose build

# test
None specified

# lint
None specified

```

## 注意事項
- 認証情報やトークンはコミットしない。
- ログに機密情報を出力しない。
- 既存のプロジェクトルールがある場合はそれを優先する。

## リポジトリ固有
- **docker_support**: True
- **database**: MySQL
- **async_processing**: aiomysql for async database operations
- **network_capture**: Intercepts HTTP/HTTPS traffic via mitmproxy addon interface
- **xml_processing**: ElementTree for XML parsing from packets
- **configuration**: Environment variables (DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)