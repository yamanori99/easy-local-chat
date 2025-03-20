from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from typing import Dict
import json

app = FastAPI()

# 静的ファイルとテンプレートの設定
app.mount("/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/templates")

# 接続中のクライアントを保持する辞書
# key: クライアントID, value: WebSocket接続
active_connections: Dict[str, WebSocket] = {}

@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    active_connections[client_id] = websocket
    
    try:
        while True:
            data = await websocket.receive_json()
            # メッセージの種類に応じて処理
            if data["type"] == "message":
                # 全ての接続中のクライアントにメッセージを送信
                message = {
                    "type": "message",
                    "client_id": client_id,
                    "message": data["message"],
                    "timestamp": data["timestamp"]
                }
                await broadcast_message(message)
            elif data["type"] == "join":
                # 新規参加者の通知
                message = {
                    "type": "system",
                    "message": f"Client {client_id} has joined the room",
                    "timestamp": data["timestamp"]
                }
                await broadcast_message(message)
                
    except WebSocketDisconnect:
        # クライアントが切断した場合の処理
        del active_connections[client_id]
        message = {
            "type": "system",
            "message": f"Client {client_id} has left the room",
            "timestamp": data["timestamp"]
        }
        await broadcast_message(message)

async def broadcast_message(message: dict):
    """全ての接続中のクライアントにメッセージをブロードキャストする"""
    for connection in active_connections.values():
        await connection.send_json(message)