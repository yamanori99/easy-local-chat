from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from typing import Dict
import json
import random
from datetime import datetime

def generate_random_color():
    return f'#{random.randint(0, 0xFFFFFF):06x}'

app = FastAPI()

# 静的ファイルとテンプレートの設定
app.mount("/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/templates")

# 接続中のクライアントを保持する辞書
# key: クライアントID, value: WebSocket接続
active_connections: Dict[str, WebSocket] = {}
client_colors: Dict[str, str] = {} # クライアントIDと色の対応を保持

@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/chat")
async def chat(request: Request, client_id: str):
    return templates.TemplateResponse("chat.html", {"request": request, "client_id": client_id})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_id = None
    try:
        while True:
            data = await websocket.receive_json()
            if not client_id:
                # クライアントIDがまだ設定されていない場合、初期メッセージから取得
                if "client_id" in data:
                    client_id = data["client_id"]
                    if client_id in active_connections:
                        # 同じクライアントIDが既に接続されている場合は拒否
                        print(f"Client ID {client_id} already in use.")
                        await websocket.close(code=1000, reason="Client ID already in use")
                        return
                    active_connections[client_id] = websocket
                    message = {
                        "type": "system",
                        "message": f"Client {client_id} has joined the room",
                        "timestamp": data["timestamp"]
                    }
                    await broadcast_message(message)
                else:
                    print("No client_id provided in initial message")
                    await websocket.close(code=1000, reason="client_id required")
                    return
            elif data["type"] == "message":
                message = {
                    "type": "message",
                    "client_id": client_id,
                    "message": data["message"],
                    "timestamp": data["timestamp"],
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
        if client_id:
            if client_id in active_connections:
                del active_connections[client_id]
            # 切断メッセージを送信
            message = {
                "type": "system",
                "message": f"Client {client_id} has left the room",
                "timestamp": datetime.now().isoformat()
            }
            await broadcast_message(message)

async def broadcast_message(message: dict):
    """全ての接続中のクライアントにメッセージをブロードキャストする"""
    for connection in active_connections.values():
        await connection.send_json(message)