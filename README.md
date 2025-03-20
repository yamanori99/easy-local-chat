雑記

# オンライン待合室システム - 使用方法

## セットアップ手順

### 1. 環境要件
- Python 3.8以上
- pip（Pythonパッケージマネージャー）

### 2. 初期セットアップ

```bash
# 1. リポジトリをクローン
git clone https://github.com/yamanori99/OnlineLabEngine.git
cd OnlineLabEngine

# 2. 仮想環境の作成
python3 -m venv venv

# 3. 仮想環境のアクティベート
# macOS/Linux:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate

# 4. 必要なパッケージのインストール
pip install -r requirements.txt
```

### 3. サーバーの起動

```bash
uvicorn src.waiting_room.main:app --reload --host 0.0.0.0 --port 8000
```

## 使用方法

### 1. アクセス方法
- ブラウザで `http://localhost:8000` にアクセス
- 複数のブラウザウィンドウで開くことで、複数ユーザーのテストが可能

### 2. 機能説明

#### チャット機能
- メッセージの入力: テキストボックスにメッセージを入力
- 送信方法:
  - 「送信」ボタンをクリック
  - または Enter キーを押す

#### 表示される情報
- 接続状態: 画面上部に表示
- メッセージ:
  - 自分のメッセージ: 右側に表示
  - 他人のメッセージ: 左側に表示
  - システムメッセージ: 中央に表示
- タイムスタンプ: 各メッセージに付加

#### 自動再接続
- 接続が切れた場合、自動的に再接続を試みます
- 接続状態は画面上部で確認可能

### 3. 注意事項
- ブラウザのJavaScriptを有効にする必要があります
- 開発モードでの使用時は `--reload` オプションにより、コードの変更が自動的に反映されます

## トラブルシューティング

### よくある問題と解決方法

1. サーバーに接続できない場合
   - ポート8000が他のプロセスで使用されていないか確認
   - ファイアウォールの設定を確認

2. メッセージが送信できない場合
   - ブラウザの開発者ツール（F12）でエラーを確認
   - WebSocket接続が確立されているか確認

3. スタイルが適用されない場合
   - ブラウザのキャッシュをクリア
   - 開発者ツールでCSSの読み込みを確認

## 開発者向け情報

### プロジェクト構造
```
OnlineLabEngine/
├── requirements.txt
├── src/
│   └── waiting_room/
│       ├── main.py          # バックエンドサーバー
│       ├── static/
│       │   ├── css/
│       │   │   └── style.css    # スタイルシート
│       │   └── js/
│       │       └── chat.js      # フロントエンドロジック
│       └── templates/
│           └── chat.html        # HTMLテンプレート
└── venv/                    # 仮想環境
```

### 使用技術
- バックエンド: FastAPI
- フロントエンド: HTML, CSS, JavaScript
- 通信プロトコル: WebSocket
- テンプレートエンジン: Jinja2

### デバッグ方法
1. サーバーログの確認
   - uvicornのコンソール出力を監視

2. クライアントサイドのデバッグ
   - ブラウザの開発者ツール（F12）を使用
   - Consoleタブでエラーを確認
   - NetworkタブでWebSocket通信を監視