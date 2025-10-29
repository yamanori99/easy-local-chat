import os
import json
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path
from ..models.session import Session


class SessionManager:
    """セッション管理クラス"""
    
    def __init__(self, data_dir: str = "data/sessions"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.current_session: Optional[Session] = None
    
    def create_session(self, session_id: Optional[str] = None, password: Optional[str] = None, 
                      require_user_password: bool = False, disable_user_password: bool = False) -> Session:
        """新しいセッションを作成"""
        if session_id is None:
            # タイムスタンプベースのセッションID生成
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        session = Session(
            session_id=session_id, 
            require_user_password=require_user_password,
            disable_user_password=disable_user_password
        )
        
        # パスワードが指定されている場合は設定
        if password:
            session.set_password(password)
        
        self.current_session = session
        self._save_session(session)
        return session
    
    def get_current_session(self) -> Optional[Session]:
        """現在のアクティブなセッションを取得"""
        return self.current_session
    
    def load_session(self, session_id: str) -> Optional[Session]:
        """指定されたセッションをロード"""
        session_file = self.data_dir / f"{session_id}.json"
        if not session_file.exists():
            return None
        
        with open(session_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return Session.from_dict(data)
    
    def get_all_sessions(self) -> List[Session]:
        """全てのセッションを取得"""
        sessions = []
        for session_file in self.data_dir.glob("*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    sessions.append(Session.from_dict(data))
            except Exception as e:
                print(f"Error loading session {session_file}: {e}")
        
        # 作成日時の降順でソート
        sessions.sort(key=lambda s: s.created_at, reverse=True)
        return sessions
    
    def get_active_sessions(self) -> List[Session]:
        """アクティブなセッションのみを取得"""
        return [s for s in self.get_all_sessions() if s.status == "active"]
    
    def update_session(self, session: Session):
        """セッションを更新"""
        self._save_session(session)
    
    def add_participant(self, session_id: str, client_id: str):
        """セッションに参加者を追加"""
        session = self.load_session(session_id)
        if session:
            session.add_participant(client_id)
            self._save_session(session)
            if self.current_session and self.current_session.session_id == session_id:
                self.current_session = session
    
    def remove_participant(self, session_id: str, client_id: str):
        """セッションから参加者を削除"""
        session = self.load_session(session_id)
        if session:
            session.remove_participant(client_id)
            self._save_session(session)
            if self.current_session and self.current_session.session_id == session_id:
                self.current_session = session
    
    def increment_message_count(self, session_id: str):
        """セッションのメッセージ数をインクリメント"""
        session = self.load_session(session_id)
        if session:
            session.increment_message_count()
            self._save_session(session)
            if self.current_session and self.current_session.session_id == session_id:
                self.current_session = session
    
    def end_session(self, session_id: str):
        """セッションを終了"""
        session = self.load_session(session_id)
        if session:
            session.end_session()
            self._save_session(session)
            if self.current_session and self.current_session.session_id == session_id:
                self.current_session = None
    
    def get_session_summary(self, session_id: str) -> Optional[Dict]:
        """セッションのサマリーを取得"""
        session = self.load_session(session_id)
        if not session:
            return None
        
        return {
            "session_id": session.session_id,
            "created_at": session.created_at,
            "ended_at": session.ended_at,
            "status": session.status,
            "participant_count": len(session.participants),
            "participants": session.participants,
            "total_messages": session.total_messages,
            "duration": self._calculate_duration(session),
            "metadata": session.metadata.model_dump()
        }
    
    def _save_session(self, session: Session):
        """セッションをファイルに保存"""
        session_file = self.data_dir / f"{session.session_id}.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            f.write(session.to_json())
    
    def _calculate_duration(self, session: Session) -> Optional[str]:
        """セッションの継続時間を計算"""
        if not session.ended_at:
            return None
        
        try:
            start = datetime.fromisoformat(session.created_at)
            end = datetime.fromisoformat(session.ended_at)
            delta = end - start
            
            hours = delta.seconds // 3600
            minutes = (delta.seconds % 3600) // 60
            seconds = delta.seconds % 60
            
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        except Exception:
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """セッションを削除"""
        session_file = self.data_dir / f"{session_id}.json"
        if session_file.exists():
            os.remove(session_file)
            return True
        return False

