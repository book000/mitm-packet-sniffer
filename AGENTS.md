# AI エージェント向け作業方針

## 目的

このドキュメントは、AI エージェント共通の作業方針を定義します。

## 基本方針

### 言語使用ルール

- **会話言語**: 日本語
- **コード内コメント**: 日本語
- **docstring**: 日本語（Python の docstring など）
- **エラーメッセージ**: 英語
- **日本語と英数字の間**: 半角スペースを挿入

### コミット規約

- **コミットメッセージ**: [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) に従う
  - `<type>(<scope>): <description>` 形式
  - `<description>` は日本語で記載
  - 例: `feat: データベース接続プーリング機能を追加`
- **ブランチ命名**: [Conventional Branch](https://conventional-branch.github.io) に従う
  - `<type>/<description>` 形式（`<type>` は短縮形: feat, fix）
  - 例: `feat/add-connection-pooling`, `fix/memory-leak`

## 判断記録のルール

判断を行う際は、以下の内容を記録すること：

1. **判断内容の要約**: 何を決定したか
2. **検討した代替案**: 他にどのような選択肢があったか
3. **採用した案とその理由**: なぜその案を選んだか
4. **採用しなかった案とその理由**: なぜその案を選ばなかったか
5. **前提条件・仮定・不確実性**: 判断の前提となる条件や不確実な要素

**重要**: 前提・仮定・不確実性を明示し、仮定を事実のように扱わない。

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

## 開発手順（概要）

1. **プロジェクト理解**
   - `README.md`, `CLAUDE.md`, `AGENTS.md` を読む
   - `mitmproxy-addon/main.py` でコードを理解する
   - `database/schema/mitm-packet-sniffer.sql` でスキーマを確認する

2. **依存関係のインストール**
   - Docker Compose で環境を起動: `docker compose up`

3. **変更の実装**
   - コードを変更する
   - コメントと docstring を日本語で記載する
   - エラーメッセージは英語で記載する

4. **動作確認**
   - Docker Compose でコンテナを再ビルド: `docker compose build`
   - サービスを起動して動作確認: `docker compose up`
   - phpMyAdmin でデータベースの状態を確認

5. **コミットとプッシュ**
   - Conventional Commits に従ってコミット
   - リモートにプッシュ

6. **PR 作成**
   - GitHub で PR を作成
   - PR 本文に変更内容を日本語で記載

## セキュリティ / 機密情報

- **データベース認証情報**: 環境変数で管理し、Git にコミットしない
- **ログへの機密情報出力禁止**: 個人情報や認証情報をログに出力しない
- **mitmproxy 証明書**: `data/mitmproxy-conf/` に保存され、`.gitignore` に追加済み

## リポジトリ固有

### mitmproxy アドオンの構成

- **`Database` クラス**: MySQL データベース操作を管理
  - `connect()`: データベースに接続
  - `insert_response()`: HTTP レスポンスをデータベースに保存
  - `is_ignore_hosts()`: ホストが無視リストにあるかチェック
  - `upsert_ignore_host()`: ホストを無視リストに追加
  - `delete_ignore_host()`: ホストを無視リストから削除
- **`Addon` クラス**: mitmproxy のフックを実装
  - `running()`: アドオン起動時にデータベースに接続
  - `response()`: HTTP レスポンス受信時にデータベースに保存
  - `tls_clienthello()`: TLS Client Hello 時に `ignore_hosts` をチェック
  - `tls_established_client()`: TLS 確立時に `ignore_hosts` に追加
  - `tls_failed_client()`: TLS 失敗時に `ignore_hosts` から削除

### データベーススキーマ

- **`responses` テーブル**: HTTP リクエスト / レスポンスを保存
- **`ignore_hosts` テーブル**: 無視するホストを管理し、段階的チェックを実施

### Docker Compose の役割

- `compose.yaml`: 全サービス起動（mysql, mitmproxy, phpmyadmin）
- `compose-db.yaml`: データベースのみ起動
- `compose-export.yaml`: データベースのダンプをエクスポート
- `compose-import.yaml`: データベースのダンプをインポート

### ポート設定

- `10000`: mitmproxy プロキシポート
- `8080`: phpMyAdmin UI

### Renovate による依存関係更新

- Renovate が作成した PR には追加コミットや更新を行わない
