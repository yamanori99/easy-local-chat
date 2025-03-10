# オンライン実験システム開発計画

## 1. プロジェクト構造
```python
project_structure = {
    'src/': {
        'auth/': '認証関連',
        'waiting_room/': '待機室関連',
        'bot/': 'Bot対話関連',
        'practice/': '練習関連',
        'experiment/': '実験関連',
        'data/': 'データ管理'
    },
    'tests/': 'テストコード',
    'docs/': 'ドキュメント'
}
```

## 2. 開発優先順位
### Phase 1: 待機室システム（最重要）
```python
class BasicWaitingRoom:
    def __init__(self):
        self.participants = {}
        self.wait_time = 30  # 最小待機時間
    
    async def add_participant(self, participant_id: str):
        """参加者を待機室に追加する最小機能"""
        self.participants[participant_id] = {
            'join_time': time.time(),
            'status': 'waiting'
        }
```

### Phase 2: 認証システム
- パスコード生成
- 参加者認証
- セッション管理

### Phase 3: Bot対話システム
- 基本的な応答機能
- 応答時間制御
- データ記録

## 3. 実装ステップ
1. **待機室の基本機能**
   - WebSocket接続
   - 待機時間管理
   - 他の参加者の存在感演出

2. **認証の実装**
   - パスコード発行
   - セッション管理
   - エラーハンドリング

3. **Bot対話の実装**
   - 基本的な対話機能
   - 応答生成
   - データ記録

## 4. テスト計画
- 待機室機能のユニットテスト
- 認証システムのテスト
- 統合テスト
- 負荷テスト

## 5. 必要な技術スタック
- FastAPI
- WebSocket
- SQLAlchemy
- Redis（セッション管理用）