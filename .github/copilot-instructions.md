# GitHub Copilot Instructions

## プロジェクト概要

- **目的**: mitmproxy を使用して HTTP パケットをスニッフィングし、MySQL データベースに保存するツール
- **主な機能**:
  - mitmproxy アドオンで HTTP リクエスト / レスポンスを傍受
  - MySQL データベースにパケットデータを保存
  - `ignore_hosts` テーブルで重複接続を段階的に抑制
  - コンテンツタイプの自動判別（Binary/JSON/XML/Text）
  - phpMyAdmin によるデータベース管理
- **対象ユーザー**: 開発者、ネットワーク解析を行うユーザー

## 共通ルール

- 会話は日本語で行う。
- PR とコミットは [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) に従う。
  - `<type>(<scope>): <description>` 形式
  - `<description>` は日本語で記載
  - 例: `feat: HTTP レスポンスキャプチャ機能を追加`
- 日本語と英数字の間には半角スペースを入れる。
- ブランチ命名は [Conventional Branch](https://conventional-branch.github.io) に従う（`feat/`, `fix/` など）。

## 技術スタック

- **言語**: Python 3.x, Bash
- **主要ライブラリ**:
  - mitmproxy 12.2.1
  - aiomysql 0.3.2
- **データベース**: MySQL 9.5.0
- **環境**: Docker Compose
- **管理ツール**: phpMyAdmin 5.2.3
- **CI/CD**: GitHub Actions（Docker イメージビルド）
- **依存関係管理**: Renovate

## コーディング規約

- **Python**:
  - PEP 8 に従う
  - 関数とクラスには docstring を日本語で記載する
  - エラーメッセージは英語で記載する
  - 型ヒントを可能な限り使用する
  - async/await を適切に使用する
- **Bash**:
  - シェバン (`#!/bin/bash`) を必ず記載する
  - エラーハンドリングを適切に行う
- **Docker**:
  - マルチステージビルドを活用する
  - 不要なレイヤーを削減する
  - セキュリティベストプラクティスに従う

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
mitmdump -s /app/main.py --set confdir=/data/mitmproxy-conf/ --set tls_version_client_min=SSL3

# Python 依存関係のインストール（開発時）
pip install -r mitmproxy-addon/requirements.txt
```

## テスト方針

- 現時点ではテストフレームワークは導入されていない
- テストを追加する場合は pytest を使用することを推奨
- mitmproxy アドオンの動作確認は実際の HTTP トラフィックで検証する
- データベース操作は phpMyAdmin で確認する

## セキュリティ / 機密情報

- データベース認証情報は環境変数で管理し、Git にコミットしない。
- ログに個人情報や認証情報を出力しない。
- パスワードやトークンは `.env` ファイルで管理し、`.gitignore` に追加する。
- mitmproxy の証明書ファイル（`data/mitmproxy-conf/`）は Git にコミットしない。

## ドキュメント更新

コードを変更した際は、必要に応じて以下のドキュメントを更新する：

- `README.md`: 新機能の追加、使用方法の変更
- `database/schema/mitm-packet-sniffer.sql`: データベーススキーマの変更
- Docker ファイルのコメント: ビルドプロセスの変更
- この `copilot-instructions.md`: 開発フローやルールの変更

## リポジトリ固有

- **mitmproxy アドオンの構成**:
  - `Database` クラス: MySQL データベース操作を管理
  - `Addon` クラス: mitmproxy のフックを実装
  - `ignore_hosts` テーブル: TLS 接続失敗時の再試行を段階的に制御（1分→5分→30分...）
- **データベーススキーマ**:
  - `responses` テーブル: HTTP リクエスト / レスポンスを保存
  - `ignore_hosts` テーブル: 無視するホストを管理
- **Docker Compose 構成**:
  - `mysql`: MySQL 9.5.0 サーバー
  - `mitmproxy`: mitmproxy アドオンを実行
  - `phpmyadmin`: データベース管理 UI
- **ポート設定**:
  - `10000`: mitmproxy プロキシポート
  - `8080`: phpMyAdmin UI
- **Renovate による自動依存関係更新**:
  - Renovate PR には追加コミットや更新を行わない
- **CI/CD**:
  - PR 作成・更新時に Docker イメージをビルド
  - `book000/templates/.github/workflows/reusable-docker.yml` を使用
  - linux/amd64 と linux/arm64 のマルチアーキテクチャビルド
