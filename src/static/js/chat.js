let ws = null;
const clientId = Math.random().toString(36).substr(2, 9);

function connect() {
    ws = new WebSocket(`ws://${window.location.host}/ws/${clientId}`);
    
    ws.onopen = function() {
        document.getElementById('connection-status').textContent = 'Status: Online';
        document.getElementById('client-id').textContent = `Client ID: ${clientId}`;
        // 参加メッセージを送信
        sendSystemMessage('join');
    };

    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        displayMessage(data);
    };

    ws.onclose = function() {
        document.getElementById('connection-status').textContent = 'Status: Offline';
        // 3秒後に再接続を試みる
        setTimeout(connect, 3000);
    };

    ws.onerror = function(error) {
        console.error('WebSocket error:', error);
    };
}

function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (message && ws) {
        const messageData = {
            type: 'message',
            message: message,
            timestamp: new Date().toISOString()
        };
        
        ws.send(JSON.stringify(messageData));
        input.value = '';
    }
}

function sendSystemMessage(type) {
    if (ws) {
        const messageData = {
            type: type,
            timestamp: new Date().toISOString()
        };
        ws.send(JSON.stringify(messageData));
    }
}

function displayMessage(data) {
    const messageArea = document.getElementById('messageArea');
    const messageDiv = document.createElement('div');

    // システムメッセージの場合、特別なクラスを追加
    if (data.type === 'system') {
        messageDiv.className = `message system`;
        messageDiv.textContent = data.message; // メッセージ内容を直接設定
    } else {
        messageDiv.className = `message ${data.client_id === clientId ? 'self' : 'other'}`;

        // メッセージコンテナを作成
        const messageContainer = document.createElement('div');
        messageContainer.className = 'message-container';

        // アイコンを表示
        const iconDiv = document.createElement('div');
        iconDiv.className = 'message-icon';
        const img = document.createElement('img');
        img.src = `/static/images/default_icon.png`; // アイコンのパス
        iconDiv.appendChild(img);
        messageContainer.appendChild(iconDiv);

        // メッセージテキストを表示
        const messageTextDiv = document.createElement('div');
        messageTextDiv.className = 'message-text';
        messageTextDiv.textContent = data.message;

        const timestamp = document.createElement('div');
        timestamp.className = 'timestamp';
        timestamp.textContent = new Date(data.timestamp).toLocaleString();
        messageTextDiv.appendChild(timestamp);

        messageContainer.appendChild(messageTextDiv);
        messageDiv.appendChild(messageContainer);
    }

    messageArea.appendChild(messageDiv);
    messageArea.scrollTop = messageArea.scrollHeight;
}

// エンターキーでメッセージを送信
document.getElementById('messageInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// 初期接続
connect(); 