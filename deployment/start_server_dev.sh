#!/bin/zsh
# 開発モードでサーバーを起動（自動リロード有効）

# プロジェクトのルートディレクトリに移動
cd "$(dirname "$0")/.."

echo "=========================================="
echo "Easy Local Chat - 開発モード"
echo "=========================================="
echo ""

# 仮想環境の確認
if [ ! -d "venv" ]; then
    echo "仮想環境が見つかりません。作成しています..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo "開発サーバーを起動しています（自動リロード有効）..."
echo ""
echo "アクセスURL: http://localhost:8000"
echo "管理画面: http://localhost:8000/admin"
echo ""
echo "ファイルを編集すると自動的に再起動されます"
echo "停止するには Ctrl+C を押してください"
echo "=========================================="
echo ""

# 開発サーバーを起動（自動リロード有効）
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000

