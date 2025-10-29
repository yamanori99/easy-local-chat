#!/bin/zsh
# サーバーの状態を確認するスクリプト

# プロジェクトのルートディレクトリに移動
cd "$(dirname "$0")/.."

echo "=========================================="
echo "Easy Local Chat - サーバー状態"
echo "=========================================="
echo ""

# プロセスの確認
echo "【プロセス】"
PROCESSES=$(ps aux | grep "uvicorn src.main:app" | grep -v grep)
if [ -n "$PROCESSES" ]; then
    echo "✓ サーバーは実行中です"
    echo "$PROCESSES"
else
    echo "✗ サーバーは停止しています"
fi

echo ""
echo "【ポート8000の使用状況】"
PORT_STATUS=$(lsof -i :8000 2>/dev/null)
if [ -n "$PORT_STATUS" ]; then
    echo "$PORT_STATUS"
else
    echo "ポート8000は使用されていません"
fi

echo ""
echo "【IPアドレス】"
LOCAL_IP=$(ifconfig en0 2>/dev/null | grep "inet " | awk '{print $2}')
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP=$(ifconfig en1 2>/dev/null | grep "inet " | awk '{print $2}')
fi
echo "ローカルIP: $LOCAL_IP"

echo ""
echo "【アクセスURL】"
echo "  http://localhost:8000"
if [ -n "$LOCAL_IP" ]; then
    echo "  http://$LOCAL_IP:8000"
fi

echo ""
echo "=========================================="

