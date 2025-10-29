from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import json
import uuid


class MessageMetadata(BaseModel):
    """メッセージのメタデータ"""
    char_count: int = 0
    word_count: int = 0
    client_color: Optional[str] = None


class Message(BaseModel):
    """チャットメッセージモデル"""
    message_id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:12]}")
    session_id: str
    client_id: str
    message_type: str = "message"  # message | system
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    metadata: MessageMetadata = Field(default_factory=MessageMetadata)
    
    def __init__(self, **data):
        super().__init__(**data)
        # メタデータを自動計算
        if self.message_type == "message":
            self.metadata.char_count = len(self.content)
            self.metadata.word_count = len(self.content.split())
    
    def to_dict(self):
        """辞書形式に変換"""
        return self.model_dump()
    
    def to_json(self):
        """JSON文字列に変換"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    def to_csv_row(self):
        """CSV行データに変換"""
        return [
            self.message_id,
            self.session_id,
            self.client_id,
            self.message_type,
            self.content,
            self.timestamp,
            self.metadata.char_count,
            self.metadata.word_count,
            self.metadata.client_color or ""
        ]
    
    @classmethod
    def from_dict(cls, data: dict):
        """辞書からインスタンスを作成"""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str):
        """JSON文字列からインスタンスを作成"""
        return cls.from_dict(json.loads(json_str))

