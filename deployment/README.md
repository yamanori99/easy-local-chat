# ローカルサーバー起動スクリプト

ローカル環境でチャットサーバーを簡単に起動・管理するためのスクリプト集です。

## 📁 ファイル一覧

- `start_server.sh` - サーバーを起動（ネットワークアクセス可能）
- `start_server_dev.sh` - 開発モードで起動（自動リロード有効）
- `stop_server.sh` - サーバーを停止
- `server_status.sh` - サーバーの状態を確認

## 🚀 使い方

### サーバーを起動

```bash
./deployment/start_server.sh
```

ブラウザで以下にアクセス:
- ローカル: http://localhost:8000
- 同じネットワーク内: http://[あなたのIP]:8000

### 開発モードで起動（自動リロード）

```bash
./deployment/start_server_dev.sh
```

ファイルを編集すると自動的にサーバーが再起動されます。

### サーバーを停止

```bash
./deployment/stop_server.sh
```

### サーバーの状態確認

```bash
./deployment/server_status.sh
```

## 📝 注意事項

- 初回起動時は仮想環境が自動的に作成されます
- 管理者パスワードは初回起動時に設定します
- サーバーを停止するには Ctrl+C を押すか、`stop_server.sh` を実行してください

