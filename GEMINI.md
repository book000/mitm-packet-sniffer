# Gemini CLI 向けコンテキストと作業方針

## 目的

このドキュメントは、Gemini CLI 向けのコンテキストと作業方針を定義します。

## 出力スタイル

### 言語

- **会話**: 日本語
- **コード内コメント**: 日本語
- **エラーメッセージ**: 英語

### トーン

- 簡潔で明確なコミュニケーション
- 技術的に正確な情報提供
- 最新の情報に基づいた提案

### 形式

- マークダウン形式で出力
- コードブロックは適切な言語指定（python, bash, sql など）
- リストや表を活用して情報を整理

## 共通ルール

- **会話言語**: 日本語
- **コミット規約**: [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) に従う
  - `<type>(<scope>): <description>` 形式
  - `<description>` は日本語で記載
  - 例: `feat: MySQL 接続プールのサイズを最適化`
- **日本語と英数字の間**: 半角スペースを挿入
- **ブランチ命名**: [Conventional Branch](https://conventional-branch.github.io) に従う
  - `<type>/<description>` 形式（`<type>` は短縮形: feat, fix）

## プロジェクト概要

- **目的**: mitmproxy を使用して HTTP パケットをスニッフィングし、MySQL データベースに保存するツール
- **主な機能**:
  - HTTP リクエスト / レスポンスの傍受と保存
  - TLS 接続の追跡と重複接続の抑制
  - コンテンツタイプの自動判別（Binary/JSON/XML/Text）
  - phpMyAdmin によるデータベース管理

## 技術スタック

- **言語**: Python 3.x, Bash
- **主要ライブラリ**:
  - mitmproxy 12.2.1
  - aiomysql 0.3.2
- **データベース**: MySQL 9.5.0
- **環境**: Docker Compose
- **管理ツール**: phpMyAdmin 5.2.3
- **CI/CD**: GitHub Actions

## コーディング規約

- **フォーマット**: PEP 8（Python）
- **命名規則**:
  - クラス名: PascalCase（例: `Database`, `Addon`）
  - 関数名: snake_case（例: `insert_response`, `is_ignore_hosts`）
  - 変数名: snake_case（例: `next_check_phase`, `last_seen_at`）
- **コメント言語**: 日本語
- **エラーメッセージ**: 英語
- **型ヒント**: 可能な限り使用（例: `def get_contenttype(self, content: bytes | None) -> str:`）
- **非同期処理**: `async`/`await` を使用

## 開発コマンド

```bash
# サービス起動
docker compose up

# サービス停止
docker compose down

# コンテナビルド
docker compose build

# データベースのみ起動
docker compose -f compose-db.yaml up

# データのエクスポート
docker compose -f compose-export.yaml up

# データのインポート
docker compose -f compose-import.yaml up

# mitmproxy 起動（コンテナ内）
mitmdump -s /app/main.py --set confdir=/data/mitmproxy-conf/ --set tls_version_client_min=TLS1_2

# Python 依存関係のインストール（開発時）
pip install -r mitmproxy-addon/requirements.txt
```

## アーキテクチャ

```
[クライアント] → [mitmproxy:10000] → [インターネット]
                       ↓
              [mitmproxy-addon/main.py]
                       ↓
                  [MySQL:3306]
                       ↓
              [phpMyAdmin:8080]
```

- **mitmproxy**: HTTP/HTTPS プロキシとして動作
- **mitmproxy-addon**: トラフィックを処理し、MySQL に保存
- **MySQL**: パケットデータとホスト情報を保存
- **phpMyAdmin**: データベース管理 UI

## 注意事項

### 認証情報のコミット禁止

- データベース認証情報は環境変数で管理し、Git にコミットしない
- `compose.yaml` に記載された認証情報は開発用のみであり、本番環境では別途設定する

### ログへの機密情報出力禁止

- HTTP リクエスト / レスポンスに含まれる個人情報や認証情報をログに出力しない
- エラーログには必要最小限の情報のみを記録する

### 既存ルールの優先

- プロジェクトの既存のコーディングスタイルやパターンを優先する
- 新しい機能を追加する際は、既存のコードとの整合性を保つ

### 既知の制約

- **mitmproxy のバージョン**: 12.2.1 に固定されており、最新バージョンとは API が異なる可能性がある
- **MySQL のバージョン**: 9.5.0 を使用しており、古いバージョンとは互換性がない可能性がある
- **TLS バージョン**: 本番環境では `tls_version_client_min=TLS1_2` 以上のみを許可し、古い SSL/TLS プロトコルは利用しない（レガシー互換が必要な場合は限定的なテスト環境などに切り出す）

## リポジトリ固有

### mitmproxy アドオンの仕組み

- `Addon` クラスが mitmproxy のフックを実装
  - `running`: アドオン起動時にデータベースに接続
  - `response`: HTTP レスポンス受信時にデータベースに保存
  - `tls_clienthello`: TLS Client Hello 時に `ignore_hosts` をチェック
  - `tls_established_client`: TLS 確立時に `ignore_hosts` に追加
  - `tls_failed_client`: TLS 失敗時に `ignore_hosts` から削除

### ignore_hosts テーブルの段階的チェック

- `next_check_phase` カラムで再試行間隔を管理
- 再試行間隔: 1分→5分→30分→1時間→3時間→6時間→12時間→24時間→48時間→無制限
- `is_next_check` メソッドで次回チェック時刻を判定

### コンテンツタイプの自動判別

- `get_contenttype` メソッドでコンテンツタイプを判別
  - `NULL`: コンテンツが存在しない
  - `BINARY`: バイナリデータ（Base64 エンコードして保存）
  - `JSON`: JSON 形式のテキスト
  - `XML`: XML 形式のテキスト
  - `TEXT`: その他のテキスト

### Docker Compose の役割

- `compose.yaml`: 全サービス起動（mysql, mitmproxy, phpmyadmin）
- `compose-db.yaml`: データベースのみ起動
- `compose-export.yaml`: データベースのダンプをエクスポート
- `compose-import.yaml`: データベースのダンプをインポート

### Renovate による依存関係更新

- Renovate が自動的に依存関係の更新 PR を作成
- Renovate PR には追加コミットや更新を行わない

### CI/CD フロー

- PR 作成・更新時に GitHub Actions が起動
- `book000/templates/.github/workflows/reusable-docker.yml` を使用
- Docker イメージをビルドし、GitHub Container Registry に公開
- linux/amd64 と linux/arm64 のマルチアーキテクチャビルド

## Gemini CLI への期待

Gemini CLI には以下の場合に相談することを期待します：

- **最新の仕様確認**:
  - mitmproxy の最新バージョンの API 変更
  - MySQL の最新バージョンの新機能や非推奨機能
  - Python の最新バージョンの型ヒント構文
- **外部サービスの制限やクォータ**:
  - GitHub Container Registry の利用制限
  - Docker Hub のレート制限
- **セキュリティベストプラクティス**:
  - mitmproxy のセキュリティ設定
  - MySQL のセキュリティ設定
  - Docker のセキュリティベストプラクティス
