#!/bin/zsh
# サーバーを停止するスクリプト

# プロジェクトのルートディレクトリに移動
cd "$(dirname "$0")/.."

echo "サーバーを停止しています..."

# uvicornプロセスを検索して停止
pkill -f "uvicorn src.main:app"

if [ $? -eq 0 ]; then
    echo "✓ サーバーが停止されました"
else
    echo "実行中のサーバーが見つかりませんでした"
fi

