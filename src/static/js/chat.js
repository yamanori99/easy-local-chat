let ws = null;
const clientId = Math.random().toString(36).substr(2, 9);

function connect() {
    ws = new WebSocket(`ws://${window.location.host}/ws/${clientId}`);
    
    ws.onopen = function() {
        document.getElementById('connection-status').textContent = '接続状態: 接続済み';
        // 参加メッセージを送信
        sendSystemMessage('join');
    };

    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        displayMessage(data);
    };

    ws.onclose = function() {
        document.getElementById('connection-status').textContent = '接続状態: 切断';
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
    
    if (data.type === 'system') {
        messageDiv.className = 'message system';
        messageDiv.textContent = data.message;
    } else {
        messageDiv.className = `message ${data.client_id === clientId ? 'self' : 'other'}`;
        messageDiv.textContent = data.message;
    }
    
    const timestamp = document.createElement('div');
    timestamp.className = 'timestamp';
    timestamp.textContent = new Date(data.timestamp).toLocaleString();
    messageDiv.appendChild(timestamp);
    
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