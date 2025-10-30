# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-29

### Added
- 初回リリース
- WebSocketベースのリアルタイムチャット機能
- セッション管理機能
- メッセージ保存機能（研究用）
- 管理画面（/admin）
- データエクスポート機能（JSON/CSV）
- パスワード保護機能
  - セッション全体のパスワード保護
  - ユーザーIDごとのパスワード保護
- レスポンシブデザイン
- 自動再接続機能
- `deployment/` ディレクトリ - ローカルサーバー起動用の便利なスクリプト集
  - `start_server.sh` - サーバーを起動（ネットワークアクセス可能）
  - `start_server_dev.sh` - 開発モードで起動（自動リロード有効）
  - `stop_server.sh` - サーバーを停止
  - `server_status.sh` - サーバーの状態を確認
  - `README.md` - deployment スクリプトの使い方ガイド

### Security
- .gitignore による機密情報の保護
  - data/ ディレクトリ（研究データ）を除外
  - exports/ ディレクトリを除外
  - 認証ファイル（.pem, .key, *credentials*）を除外

