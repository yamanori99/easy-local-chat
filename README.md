ちゃっぴーが作った雑記

# ローカルチャットシステム

シンプルで使いやすいローカルチャットシステムです。WebSocketを使用したリアルタイムコミュニケーションを実現します。

## 機能概要
- リアルタイムチャット機能
- 複数ユーザー同時接続対応
- 自動再接続機能
- レスポンシブデザイン
- システムメッセージ表示

## 必要条件
- Python 3.8以上
- pip（Pythonパッケージマネージャー）
- モダンブラウザ（Chrome, Firefox, Safari, Edge等）

## クイックスタート

### 1. インストール
```bash
# リポジトリのクローン
git clone https://github.com/yamanori99/easy-local-chat.git
cd easy-local-chat

# 仮想環境のセットアップ
python3 -m venv venv

# 仮想環境の有効化
# macOS/Linux:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate

# 依存パッケージのインストール
pip install -r requirements.txt
```

### 2. サーバーの起動
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. アプリケーションへのアクセス
ブラウザで以下のURLにアクセス：
```
http://localhost:8000
```

## 詳細な使用方法

### ログイン機能
- **ログイン方法**
  - 初回アクセス時にログイン画面が表示
  - クライアントIDを入力して入室
  - 一度入力したIDは自動的に保存（ブラウザセッション中）

- **ユーザー識別**
  - 各ユーザーに固有の色を自動割り当て
  - メッセージにユーザー名とカラーコードを表示
  - システムメッセージでユーザーの入退室を通知

- **セキュリティ**
  - クライアントIDの重複チェック
  - 不正なIDの入力防止（文字数制限、使用可能文字の制限）
  - WebSocket接続の認証確認

### チャット機能
- **メッセージ送信**
  - テキストボックスに入力
  - 送信ボタンまたはEnterキーで送信
- **メッセージ表示**
  - 自分のメッセージ：右側
  - 他のユーザーのメッセージ：左側
  - システムメッセージ：中央
  - すべてのメッセージにタイムスタンプ付き

### システム機能
- **自動再接続**
  - 接続が切れた場合に自動的に再接続
  - 接続状態をヘッダーに表示
- **マルチユーザー対応**
  - 複数ブラウザウィンドウでの同時接続可能
  - ユーザー参加/退出の通知

## セキュリティ設定

### クライアントID制限
- 最小文字数: 3文字
- 最大文字数: 20文字
- 使用可能文字: 英数字、アンダースコア(_)、ハイフン(-)
- 予約語の使用禁止（admin, system等）

### 接続制限
- 同一IPアドレスからの最大接続数: 5
- 接続タイムアウト: 60秒
- 再接続試行回数: 3回

### データ保護
- メッセージの一時保存のみ（永続化なし）
- クライアント情報の暗号化
- セッション管理によるセキュリティ確保

## 設定のカスタマイズ

### サーバー設定
```bash
# ポート番号の変更
uvicorn src.main:app --port 3000

# ホストの制限
uvicorn src.main:app --host 127.0.0.1

# SSL/TLS対応（開発環境）
uvicorn src.main:app --ssl-keyfile=./key.pem --ssl-certfile=./cert.pem
```

### クライアント設定
- ブラウザのローカルストレージでユーザー設定を保存
- カスタムテーマの選択（ライト/ダーク）
- メッセージ表示設定のカスタマイズ

## トラブルシューティング

### 一般的な問題
1. **接続エラー**
   - ポート8000の使用状況を確認
   - ファイアウォール設定の確認
   - `netstat -ano | grep 8000` でポート状態確認

2. **表示の問題**
   - ブラウザのキャッシュをクリア
   - JavaScript有効化の確認
   - 開発者ツール（F12）でエラーを確認

## 開発者向け情報

### プロジェクト構造
```
easy-local-chat/
├── README.md
├── requirements.txt
└── src/
    ├── main.py          # サーバーサイドロジック
    ├── static/          # 静的ファイル
    │   ├── css/
    │   └── js/
    └── templates/       # HTMLテンプレート
```

### 使用技術
- **バックエンド**
  - FastAPI (Pythonフレームワーク)
  - WebSocket (リアルタイム通信)
- **フロントエンド**
  - HTML5
  - CSS3
  - JavaScript (ES6+)
- **開発ツール**
  - uvicorn (ASGIサーバー)
  - Jinja2 (テンプレートエンジン)

### デバッグ方法
- **サーバーサイド**
  - uvicornログの監視
  - FastAPIのデバッグモード活用

- **クライアントサイド**
  - 開発者ツール（F12）の使用
  - WebSocket通信の監視
  - コンソールログの確認

