# Claude Code 作業方針

## 目的

このドキュメントは、Claude Code がこのリポジトリで作業を行う際の方針とプロジェクト固有のルールを定義します。

## 判断記録のルール

判断は必ずレビュー可能な形で記録すること：

1. **判断内容の要約**: 何を決定したか
2. **検討した代替案**: 他にどのような選択肢があったか
3. **採用しなかった案とその理由**: なぜその案を選ばなかったか
4. **前提条件・仮定・不確実性**: 判断の前提となる条件や不確実な要素
5. **他エージェントによるレビュー可否**: Codex CLI や Gemini CLI でレビュー可能か

**重要**: 前提・仮定・不確実性を明示し、仮定を事実のように扱わない。

## プロジェクト概要

- **目的**: mitmproxy を使用して HTTP パケットをスニッフィングし、MySQL データベースに保存するツール
- **主な機能**:
  - HTTP リクエスト / レスポンスの傍受と保存
  - TLS 接続の追跡と重複接続の抑制
  - コンテンツタイプの自動判別（Binary/JSON/XML/Text）
  - phpMyAdmin によるデータベース管理

## 重要ルール

### 会話と言語

- **会話言語**: 日本語
- **コード内コメント**: 日本語
- **docstring**: 日本語（Python の docstring など）
- **エラーメッセージ**: 英語
- **日本語と英数字の間**: 半角スペースを挿入

### コミット規約

- **コミットメッセージ**: [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) に従う
  - `<type>(<scope>): <description>` 形式
  - `<description>` は日本語で記載
  - 例: `feat: ignore_hosts テーブルの段階的チェック機能を追加`

## 環境のルール

### ブランチ命名

- [Conventional Branch](https://conventional-branch.github.io) に従う
- `<type>/<description>` 形式（`<type>` は短縮形: feat, fix）
- 例: `feat/add-tls-error-handling`, `fix/database-connection-leak`

### GitHub リポジトリ調査

- 調査のために GitHub リポジトリを参照する場合は、テンポラリディレクトリに git clone してコード検索する

### Renovate PR の扱い

- Renovate が作成した既存のプルリクエストに対して、追加コミットや更新を行わない

## コード改修時のルール

### エラーメッセージ

- 既存のエラーメッセージで先頭に絵文字がある場合は、全体でエラーメッセージに絵文字を設定する
- 絵文字はエラーメッセージに即した一文字の絵文字である必要がある

### docstring の記載

- 関数やクラスには docstring を日本語で記載・更新する
- Python では PEP 257 に従った docstring を記載する

### 型ヒント

- Python では可能な限り型ヒントを使用する
- `from typing import ...` で必要な型をインポートする

## 相談ルール

### Codex CLI（ask-codex）への相談

以下の場合に Codex CLI に相談する：

- 実装コードに対するソースコードレビュー
- 関数設計、モジュール内部の実装方針などの局所的な技術判断
- アーキテクチャ、モジュール間契約、パフォーマンス / セキュリティといった全体影響の判断
- 実装の正当性確認、機械的ミスの検出、既存コードとの整合性確認

### Gemini CLI（ask-gemini）への相談

以下の場合に Gemini CLI に相談する：

- SaaS 仕様、言語・ランタイムのバージョン差、料金・制限・クォータといった、最新の適切な情報が必要な外部依存の判断
- 外部一次情報の確認、最新仕様の調査、外部前提条件の検証

### 他エージェントの指摘への対応

他エージェントが指摘・異議を提示した場合、Claude Code は必ず以下のいずれかを行う。黙殺・無言での不採用は禁止する。

- 指摘を受け入れ、判断を修正する
- 指摘を退け、その理由を明示する

### 相談時の注意事項

- 他エージェントの提案を鵜呑みにせず、その根拠や理由を理解する
- 自身の分析結果と他エージェントの意見が異なる場合は、双方の視点を比較検討する
- 最終的な判断は、両者の意見を総合的に評価した上で、自身で下す

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

## アーキテクチャと主要ファイル

### アーキテクチャサマリー

```
[mitmproxy] → [mitmproxy-addon/main.py] → [MySQL]
                                            ↓
                                       [phpMyAdmin]
```

- **mitmproxy**: HTTP/HTTPS プロキシとして動作し、トラフィックを傍受
- **mitmproxy-addon/main.py**: アドオンとしてトラフィックを処理し、MySQL に保存
- **MySQL**: パケットデータとホスト情報を保存
- **phpMyAdmin**: データベース管理 UI

### 主要ディレクトリとファイル

- `mitmproxy-addon/`: mitmproxy アドオンのコード
  - `main.py`: アドオンのメインロジック（`Database` クラス、`Addon` クラス）
  - `requirements.txt`: Python 依存関係
  - `Dockerfile`: mitmproxy コンテナのビルド定義
  - `entrypoint.sh`: コンテナのエントリーポイント
- `database/`: データベース関連
  - `schema/mitm-packet-sniffer.sql`: MySQL スキーマ定義
  - `entrypoint.sh`: データベース初期化スクリプト
  - `Dockerfile`: データベースコンテナのビルド定義
- `compose.yaml`: メインの Docker Compose 設定
- `compose-db.yaml`: データベースのみの Docker Compose 設定
- `compose-export.yaml`: データエクスポート用 Docker Compose 設定
- `compose-import.yaml`: データインポート用 Docker Compose 設定
- `.github/workflows/docker.yml`: Docker イメージビルドの CI/CD

### データベーススキーマ

- **`responses` テーブル**: HTTP リクエスト / レスポンスを保存
  - `id`, `host`, `port`, `method`, `scheme`, `authority`, `path`, `path_hash`, `query`
  - `request_content`, `request_content_type`, `http_version`, `request_headers`
  - `status_code`, `response_headers`, `response_content`, `response_content_type`
  - `created_at`
- **`ignore_hosts` テーブル**: 無視するホストを管理
  - `address`, `created_at`, `last_seen_at`, `next_check_phase`

## 実装パターン

### 推奨パターン

- **非同期処理**: `async`/`await` を使用した非同期データベース操作
- **コンテンツタイプ判別**: バイナリ / JSON / XML / テキストを自動判別
- **段階的チェック**: `ignore_hosts` テーブルで再試行間隔を段階的に延長（1分→5分→30分→1時間→...）
- **環境変数**: データベース接続情報は環境変数で管理
- **エラーハンドリング**: 例外を適切にキャッチし、ログに記録

### 非推奨パターン

- 同期的なデータベース操作（aiomysql の非同期機能を使用すること）
- ハードコードされた認証情報
- エラーの無視（`except: pass` は最小限に）

## テスト

### テスト方針

- 現時点ではテストフレームワークは導入されていない
- テストを追加する場合は pytest を使用する
- mitmproxy アドオンの動作確認は実際の HTTP トラフィックで検証する

### テスト追加条件

以下の場合にテストを追加する：

- データベース操作ロジックの変更
- コンテンツタイプ判別ロジックの変更
- `ignore_hosts` の段階的チェックロジックの変更

## ドキュメント更新ルール

### 更新対象

- `README.md`: 新機能の追加、使用方法の変更
- `database/schema/mitm-packet-sniffer.sql`: データベーススキーマの変更
- `CLAUDE.md`（このファイル）: 開発フローやルールの変更
- `.github/copilot-instructions.md`: 開発ルールの変更
- `AGENTS.md`: 基本方針の変更
- `GEMINI.md`: コンテキストの変更

### 更新タイミング

- 新機能の追加時
- アーキテクチャの変更時
- 開発フローの変更時

## 作業チェックリスト

### 新規改修時

新規改修を行う前に、以下を必ず確認する：

1. プロジェクトについて詳細に探索し理解すること
2. 作業を行うブランチが適切であること。すでに PR を提出しクローズされたブランチでないこと
3. 最新のリモートブランチに基づいた新規ブランチであること
4. PR がクローズされ、不要となったブランチは削除されていること
5. Docker Compose で依存サービスを起動したこと

### コミット・プッシュ前

コミット・プッシュする前に、以下を必ず確認する：

1. コミットメッセージが [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) に従っていること（`<description>` は日本語）
2. コミット内容にセンシティブな情報が含まれていないこと
3. 動作確認を行い、期待通り動作すること
4. Python コードの構文エラーがないこと

### PR 作成前

プルリクエストを作成する前に、以下を必ず確認する：

1. プルリクエストの作成をユーザーから依頼されていること
2. コミット内容にセンシティブな情報が含まれていないこと
3. コンフリクトする恐れが無いこと

### PR 作成後

プルリクエストを作成した後は、以下を必ず実施する（PR 作成後のプッシュ時に毎回実施）：

1. コンフリクトが発生していないこと
2. PR 本文の内容は、ブランチの現在の状態を、今までのこの PR での更新履歴を含むことなく、最新の状態のみ、漏れなく日本語で記載されていること
3. `gh pr checks <PR ID> --watch` で GitHub Actions CI を待ち、その結果がエラーとなっていないこと
4. `request-review-copilot https://github.com/$OWNER/$REPO/pull/$PR_NUMBER` で GitHub Copilot へレビューを依頼すること（コマンドが存在する場合）
5. 10分以内に投稿される GitHub Copilot レビューへの対応を行うこと
6. `/code-review:code-review` によるコードレビューを実施し、**スコアが 50 以上の指摘事項** に対して対応すること

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

### Docker Compose の役割

- `compose.yaml`: 全サービス起動（mysql, mitmproxy, phpmyadmin）
- `compose-db.yaml`: データベースのみ起動
- `compose-export.yaml`: データベースのダンプをエクスポート
- `compose-import.yaml`: データベースのダンプをインポート

### ポート設定

- `10000`: mitmproxy プロキシポート（ホスト側）
- `8080`: phpMyAdmin UI（ホスト側）

### CI/CD フロー

- PR 作成・更新時に GitHub Actions が起動
- `book000/templates/.github/workflows/reusable-docker.yml` を使用
- Docker イメージをビルドし、GitHub Container Registry に公開
- linux/amd64 と linux/arm64 のマルチアーキテクチャビルド

### セキュリティ

- データベース認証情報は環境変数で管理（`compose.yaml` に記載）
- mitmproxy の証明書ファイルは `data/mitmproxy-conf/` に保存（`.gitignore` に追加済み）
- ログに個人情報や認証情報を出力しない
