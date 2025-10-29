from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Form, Cookie
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, Response
from typing import Dict, Optional
import json
import random
import os
import hashlib
import secrets
from datetime import datetime
from pathlib import Path

from .models.session import Session
from .models.message import Message
from .managers.session_manager import SessionManager
from .managers.message_store import MessageStore
from .exporters.data_exporter import DataExporter

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
client_sessions: Dict[str, str] = {} # クライアントIDとセッションIDの対応を保持

# データ管理のインスタンス
session_manager = SessionManager()
message_store = MessageStore()
data_exporter = DataExporter()

# 管理者認証用
ADMIN_PASSWORD_FILE = "data/admin_password.txt"
admin_tokens: Dict[str, bool] = {}  # トークン: 認証済みフラグ

def get_admin_password_hash() -> Optional[str]:
    """管理者パスワードハッシュを取得"""
    if os.path.exists(ADMIN_PASSWORD_FILE):
        with open(ADMIN_PASSWORD_FILE, 'r') as f:
            return f.read().strip()
    return None

def set_admin_password(password: str):
    """管理者パスワードを設定"""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    Path(ADMIN_PASSWORD_FILE).parent.mkdir(parents=True, exist_ok=True)
    with open(ADMIN_PASSWORD_FILE, 'w') as f:
        f.write(password_hash)
    print(f"Admin password set successfully.")

def verify_admin_password(password: str) -> bool:
    """管理者パスワードを検証"""
    stored_hash = get_admin_password_hash()
    if not stored_hash:
        return False
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return password_hash == stored_hash

def generate_admin_token() -> str:
    """管理者認証トークンを生成"""
    token = secrets.token_urlsafe(32)
    admin_tokens[token] = True
    return token

def verify_admin_token(token: Optional[str]) -> bool:
    """管理者トークンを検証"""
    if not token:
        return False
    return admin_tokens.get(token, False)

# アプリケーション起動時の処理
@app.on_event("startup")
async def startup_event():
    global session_manager
    
    # 管理者パスワードのチェック
    stored_password = get_admin_password_hash()
    if not stored_password:
        print("\n" + "="*60)
        print("ADMIN PASSWORD SETUP")
        print("="*60)
        print("No admin password found. Please set an admin password.")
        print("You can set it via environment variable or enter it now:")
        print()
        
        # 環境変数からパスワードを取得
        env_password = os.environ.get('ADMIN_PASSWORD')
        if env_password:
            set_admin_password(env_password)
            print("Admin password set from environment variable.")
        else:
            # 標準入力からパスワードを取得
            import getpass
            while True:
                password = getpass.getpass("Enter admin password: ")
                if len(password) < 4:
                    print("Password must be at least 4 characters long.")
                    continue
                confirm = getpass.getpass("Confirm admin password: ")
                if password != confirm:
                    print("Passwords do not match. Please try again.")
                    continue
                set_admin_password(password)
                break
        print("="*60 + "\n")
    
    # 既存のアクティブなセッションをチェック
    active_sessions = session_manager.get_active_sessions()
    
    if active_sessions:
        print(f"Found {len(active_sessions)} active session(s):")
        for session in active_sessions:
            print(f"  - {session.session_id}")
    else:
        print("No active sessions found. Please create a session from the admin panel.")

@app.get("/")
async def get(request: Request):
    # アクティブなセッションがあるかチェック
    active_sessions = session_manager.get_active_sessions()
    
    if not active_sessions:
        # アクティブなセッションがない場合は管理画面にリダイレクト
        return RedirectResponse(url="/admin", status_code=302)
    
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/viewer")
async def viewer(request: Request, session_id: str, admin_token: Optional[str] = Cookie(None)):
    """管理者用のセッションビューワー（読み取り専用）"""
    # 認証チェック
    if not verify_admin_token(admin_token):
        return RedirectResponse(url="/admin/login", status_code=302)
    
    # セッションが存在するか確認
    session = session_manager.load_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return templates.TemplateResponse("viewer.html", {
        "request": request,
        "session_id": session_id
    })

@app.get("/chat")
async def chat(request: Request, client_id: str, session_id: str = None, 
               session_password: str = None, user_password: str = None):
    # session_idが指定されていない場合は、現在のセッションを使用
    if not session_id:
        current_session = session_manager.get_current_session()
        session_id = current_session.session_id if current_session else "no_session"
        session = current_session
    else:
        # 指定されたセッションが存在するか確認
        session = session_manager.load_session(session_id)
        if not session or session.status != "active":
            # セッションが存在しないか終了している場合は、現在のセッションを使用
            current_session = session_manager.get_current_session()
            session_id = current_session.session_id if current_session else "no_session"
            session = current_session
    
    # セッション全体のパスワード保護チェック
    if session and session.password_protected:
        if not session_password or not session.verify_password(session_password):
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "セッションパスワードが正しくありません"
            })
    
    # ユーザーIDのパスワード保護チェック
    if session:
        # 既存の保護されたIDの場合
        if session.has_user_password(client_id):
            if not user_password or not session.verify_user_password(client_id, user_password):
                return templates.TemplateResponse("login.html", {
                    "request": request,
                    "error": f"ユーザーID '{client_id}' のパスワードが正しくありません"
                })
        # セッションがユーザーパスワード必須の場合、新規ユーザーもパスワードが必要
        elif session.require_user_password and not session.has_user_password(client_id):
            if not user_password:
                return templates.TemplateResponse("login.html", {
                    "request": request,
                    "error": "このセッションではユーザーパスワードが必須です"
                })
    
    return templates.TemplateResponse("chat.html", {
        "request": request, 
        "client_id": client_id,
        "session_id": session_id
    })

@app.websocket("/ws/viewer")
async def websocket_viewer_endpoint(websocket: WebSocket, session_id: str):
    """管理者用の読み取り専用WebSocket接続"""
    await websocket.accept()
    
    # セッションが存在するか確認
    if session_id:
        session = session_manager.load_session(session_id)
        if not session:
            await websocket.close(code=1000, reason="Session not found")
            return
    else:
        await websocket.close(code=1000, reason="Session ID required")
        return
    
    # 管理者ID（特殊なID）
    viewer_id = f"admin_viewer_{id(websocket)}"
    active_connections[viewer_id] = websocket
    client_sessions[viewer_id] = session_id
    
    print(f"[Viewer] Admin connected to session: {session_id}")
    
    try:
        # 管理者はメッセージを受信するだけ（送信しない）
        while True:
            # メッセージを受信し続けるが、何もしない
            data = await websocket.receive_json()
            # 管理者からのメッセージは無視
            pass
    except WebSocketDisconnect:
        if viewer_id in active_connections:
            del active_connections[viewer_id]
        if viewer_id in client_sessions:
            del client_sessions[viewer_id]
        print(f"[Viewer] Admin disconnected from session: {session_id}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, session_id: str = None):
    await websocket.accept()
    client_id = None
    
    # session_idが指定されている場合は、そのセッションを使用
    if session_id:
        session = session_manager.load_session(session_id)
        if not session or session.status != "active":
            await websocket.close(code=1000, reason="Invalid or inactive session")
            return
    else:
        # 指定されていない場合は現在のセッションを使用
        current_session = session_manager.get_current_session()
        if not current_session:
            await websocket.close(code=1000, reason="No active session")
            return
        session_id = current_session.session_id
    
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
                    client_sessions[client_id] = session_id  # セッションIDを記録
                    
                    # セッションに参加者を追加
                    session_manager.add_participant(session_id, client_id)
                    
                    # システムメッセージを作成・保存
                    join_message = Message(
                        session_id=session_id,
                        client_id=client_id,
                        message_type="system",
                        content=f"Client {client_id} has joined the room",
                        timestamp=data["timestamp"]
                    )
                    message_store.save_message(join_message)
                    
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
                # ユーザーメッセージを保存
                user_message = Message(
                    session_id=session_id,
                    client_id=client_id,
                    message_type="message",
                    content=data["message"],
                    timestamp=data["timestamp"]
                )
                message_store.save_message(user_message)
                
                # セッションのメッセージ数をインクリメント
                session_manager.increment_message_count(session_id)
                
                message = {
                    "type": "message",
                    "client_id": client_id,
                    "message": data["message"],
                    "timestamp": data["timestamp"],
                }
                await broadcast_message(message)
            elif data["type"] == "join":
                # 新規参加者の通知（既に上で処理済み）
                pass

    except WebSocketDisconnect:
        if client_id:
            if client_id in active_connections:
                del active_connections[client_id]
            if client_id in client_sessions:
                del client_sessions[client_id]
            
            # セッションから参加者を削除
            session_manager.remove_participant(session_id, client_id)
            
            # 切断メッセージを保存
            leave_message = Message(
                session_id=session_id,
                client_id=client_id,
                message_type="system",
                content=f"Client {client_id} has left the room",
                timestamp=datetime.now().isoformat()
            )
            message_store.save_message(leave_message)
            
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

# ========== 管理API エンドポイント ==========

@app.get("/admin/login")
async def admin_login_page(request: Request):
    """管理者ログイン画面"""
    return templates.TemplateResponse("admin_login.html", {"request": request})

@app.post("/admin/auth")
async def admin_authenticate(password: str = Form(...)):
    """管理者認証"""
    if verify_admin_password(password):
        token = generate_admin_token()
        response = RedirectResponse(url="/admin", status_code=302)
        response.set_cookie(key="admin_token", value=token, httponly=True, max_age=86400)  # 24時間有効
        return response
    else:
        # 認証失敗
        return RedirectResponse(url="/admin/login?error=1", status_code=302)

@app.get("/admin/logout")
async def admin_logout():
    """管理者ログアウト"""
    response = RedirectResponse(url="/admin/login", status_code=302)
    response.delete_cookie(key="admin_token")
    return response

@app.get("/admin")
async def admin_page(request: Request, admin_token: Optional[str] = Cookie(None)):
    """管理画面"""
    # 認証チェック
    if not verify_admin_token(admin_token):
        return RedirectResponse(url="/admin/login", status_code=302)
    
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/api/sessions")
async def get_sessions():
    """全セッションの取得"""
    sessions = session_manager.get_all_sessions()
    return JSONResponse(content={
        "sessions": [s.to_dict() for s in sessions]
    })

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """特定のセッション情報を取得"""
    summary = session_manager.get_session_summary(session_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Session not found")
    return JSONResponse(content=summary)

@app.get("/api/sessions/{session_id}/messages")
async def get_session_messages(session_id: str):
    """セッションのメッセージを取得"""
    messages = message_store.get_messages_by_session(session_id)
    return JSONResponse(content={
        "messages": [m.to_dict() for m in messages]
    })

@app.get("/api/sessions/{session_id}/statistics")
async def get_session_statistics(session_id: str):
    """セッションの統計情報を取得"""
    stats = message_store.get_session_statistics(session_id)
    return JSONResponse(content=stats)

@app.post("/api/sessions/{session_id}/set_user_password")
async def set_user_password(session_id: str, client_id: str, password: str):
    """ユーザーIDにパスワードを設定"""
    session = session_manager.load_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.set_user_password(client_id, password)
    session_manager.update_session(session)
    
    return JSONResponse(content={
        "status": "success",
        "message": f"Password set for user {client_id}"
    })

@app.get("/api/sessions/{session_id}/check_user_password")
async def check_user_password(session_id: str, client_id: str):
    """ユーザーIDがパスワード保護されているか確認"""
    session = session_manager.load_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return JSONResponse(content={
        "has_password": session.has_user_password(client_id),
        "protected_users": session.get_protected_users()
    })

@app.get("/api/sessions/current/info")
async def get_current_session_info():
    """現在のセッション情報を取得"""
    current_session = session_manager.get_current_session()
    if not current_session:
        raise HTTPException(status_code=404, detail="No active session")
    
    summary = session_manager.get_session_summary(current_session.session_id)
    stats = message_store.get_session_statistics(current_session.session_id)
    
    return JSONResponse(content={
        "session": summary,
        "statistics": stats
    })

@app.post("/api/sessions/{session_id}/export")
async def export_session_data(session_id: str, format: str = "json"):
    """セッションデータをエクスポート"""
    try:
        if format == "csv":
            filepath = data_exporter.export_messages_to_csv(session_id, message_store)
        elif format == "json":
            filepath = data_exporter.export_messages_to_json(session_id, message_store)
        elif format == "complete":
            files = data_exporter.export_complete_dataset(session_id, session_manager, message_store)
            return JSONResponse(content={"files": files})
        else:
            raise HTTPException(status_code=400, detail="Invalid format")
        
        return FileResponse(filepath, filename=filepath.split('/')[-1])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sessions/{session_id}/end")
async def end_session(session_id: str, admin_token: Optional[str] = Cookie(None)):
    """セッションを終了"""
    # 認証チェック
    if not verify_admin_token(admin_token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    # このセッションに接続している全ユーザーに通知
    session_end_message = {
        "type": "session_end",
        "message": "This session has been ended by admin.",
        "timestamp": datetime.now().isoformat()
    }
    
    # セッションに属する全クライアントを特定して通知
    clients_to_notify = [client_id for client_id, sess_id in client_sessions.items() if sess_id == session_id]
    for client_id in clients_to_notify:
        if client_id in active_connections:
            try:
                await active_connections[client_id].send_json(session_end_message)
            except Exception as e:
                print(f"Error notifying client {client_id}: {e}")
    
    # セッションを終了
    session_manager.end_session(session_id)
    return JSONResponse(content={"status": "success", "message": "Session ended"})

@app.delete("/api/sessions/{session_id}/delete")
async def delete_session(session_id: str, admin_token: Optional[str] = Cookie(None)):
    """セッションを削除"""
    # 認証チェック
    if not verify_admin_token(admin_token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    success = session_manager.delete_session(session_id)
    if success:
        # メッセージデータも削除
        message_store.delete_session_messages(session_id)
        return JSONResponse(content={"status": "success", "message": "Session deleted"})
    else:
        raise HTTPException(status_code=404, detail="Session not found")

@app.post("/api/sessions/new")
async def create_new_session(end_previous: bool = True, password: Optional[str] = None,
                            require_user_password: bool = False,
                            disable_user_password: bool = False,
                            admin_token: Optional[str] = Cookie(None)):
    """新しいセッションを作成
    
    Args:
        end_previous: Trueの場合、既存のアクティブセッションを全て終了（デフォルト）
        password: セッションのパスワード（オプション）
        require_user_password: ユーザーパスワード必須（True=必須、False=任意）
        disable_user_password: ユーザーパスワード完全無効（True=パスワードなし強制）
    """
    # 認証チェック
    if not verify_admin_token(admin_token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    if end_previous:
        # 接続中の全ユーザーにセッション終了を通知
        if active_connections:
            session_end_message = {
                "type": "session_end",
                "message": "セッションが終了しました。新しいセッションが開始されます。",
                "timestamp": datetime.now().isoformat()
            }
            await broadcast_message(session_end_message)
        
        # 全てのアクティブなセッションを終了
        active_sessions = session_manager.get_active_sessions()
        for old_session in active_sessions:
            session_manager.end_session(old_session.session_id)
            print(f"Previous session ended: {old_session.session_id}")
    
    # 新しいセッションを作成
    session = session_manager.create_session(
        password=password, 
        require_user_password=require_user_password,
        disable_user_password=disable_user_password
    )
    password_status = "with password" if password else "without password"
    user_pw_status = "required" if require_user_password else "optional" if not disable_user_password else "disabled"
    print(f"New session created: {session.session_id} ({password_status}, user password: {user_pw_status})")
    
    message = "New session created"
    if end_previous:
        message = "Previous sessions ended, new session created"
    
    return JSONResponse(content={
        "status": "success",
        "session": session.to_dict(),
        "message": message
    })