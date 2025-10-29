#!/bin/zsh
# ローカルでチャットサーバーを起動するスクリプト

# プロジェクトのルートディレクトリに移動
cd "$(dirname "$0")/.."

echo "=========================================="
echo "Easy Local Chat - サーバー起動"
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

# Mac miniのIPアドレスを表示
LOCAL_IP=$(ifconfig en0 2>/dev/null | grep "inet " | awk '{print $2}')
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP=$(ifconfig en1 2>/dev/null | grep "inet " | awk '{print $2}')
fi

echo "サーバーを起動しています..."
echo ""
echo "アクセスURL:"
echo "  ローカル: http://localhost:8000"
if [ -n "$LOCAL_IP" ]; then
    echo "  ネットワーク: http://$LOCAL_IP:8000"
fi
echo ""
echo "管理画面: /admin"
echo ""
echo "停止するには Ctrl+C を押してください"
echo "=========================================="
echo ""

# サーバーを起動
uvicorn src.main:app --host 0.0.0.0 --port 8000

