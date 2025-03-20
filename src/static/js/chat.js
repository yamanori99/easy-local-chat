let ws = null;
// const clientId = "client-" + Math.random().toString(36).substr(2, 5);

// 黄金比を使用してより均一な分布を得る
const GOLDEN_RATIO = 0.618033988749895;

// シード値から擬似乱数を生成するジェネレータ
function createRandomGenerator(seed) {
    // シード値からハッシュ値を生成
    let hash = 0;
    for (let i = 0; i < seed.length; i++) {
        hash = seed.charCodeAt(i) + ((hash << 5) - hash);
    }
    
    // 擬似乱数生成関数を返す
    return function() {
        // xorshiftアルゴリズムを使用
        hash ^= hash << 13;
        hash ^= hash >> 17;
        hash ^= hash << 5;
        return (hash >>> 0) / 4294967296; // 0から1の範囲に正規化
    };
}

// より多様な色を生成するバージョン
function getColorFromClientId(clientId) {
    const random = createRandomGenerator(clientId);
    
    // 複数の要素から色を生成
    const baseHue = (random() + GOLDEN_RATIO) % 1;
    const hueOffset = random() * 30 - 15;  // ±15度のばらつき
    
    const h = Math.floor((baseHue * 360 + hueOffset + 360) % 360);
    const s = 65 + random() * 25;  // 彩度: 65-90%
    const l = 50 + random() * 15;  // 明度: 50-65%
    
    return `hsl(${h}, ${s}%, ${l}%)`;
}

// 色のプリセットを定義（必要に応じて）
const COLOR_PRESETS = {
    'admin': 'hsl(210, 80%, 60%)',      // 管理者用の青
    'moderator': 'hsl(280, 75%, 60%)',  // モデレーター用の紫
    'system': 'hsl(0, 0%, 50%)'         // システムメッセージ用のグレー
};

// クライアントIDから色を取得（プリセットがある場合はそちらを優先）
function getClientColor(clientId) {
    return COLOR_PRESETS[clientId] || getColorFromClientId(clientId);
}

let clientId;

function connect() {
    // クエリパラメータからclient_idを取得
    const urlParams = new URLSearchParams(window.location.search);
    clientId = urlParams.get('client_id');

    if (!clientId) {
        alert('Client ID is required.');
        window.location.href = '/'; // ログインページに戻す
        return;
    }

    ws = new WebSocket(`ws://${window.location.host}/ws`);
    
    ws.onopen = function() {
        document.getElementById('status-text').textContent = 'Online';
        document.getElementById('status-icon').className = 'online';
        document.getElementById('client-id').textContent = `Client ID: ${clientId}`;
        // 参加メッセージを送信
        sendSystemMessage('join');
    };

    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        displayMessage(data);
    };

    ws.onclose = function(event) {
        if (event.reason === "Client ID already in use") {
            alert("This ID is already in use. Please log in with a different ID.");
            window.location.href = '/'; // ログインページに戻す
        } else {
            document.getElementById('status-text').textContent = 'Offline';
            document.getElementById('status-icon').className = 'offline';
            console.log('WebSocket closed:', event);
        }
    };

    ws.onerror = function(error) {
        console.error('WebSocket error:', error);
    };
}

function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (message && ws && ws.readyState === WebSocket.OPEN) {
        const messageData = {
            type: 'message',
            client_id: clientId,
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
            client_id: clientId,
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
        iconDiv.style.backgroundColor = data.client_id === clientId ? getColorFromClientId(clientId) : getColorFromClientId(data.client_id); // 自分のメッセージには自分の色、それ以外はクライアントIDから生成
        const img = document.createElement('img');
        img.src = `/static/images/default_icon.png`; // アイコンのパス
        iconDiv.appendChild(img);
        messageContainer.appendChild(iconDiv);

        // メッセージテキストを表示
        const messageTextDiv = document.createElement('div');
        messageTextDiv.className = 'message-text';
        // クライアントIDを表示
        const clientIdSpan = document.createElement('span');
        clientIdSpan.className = 'client-id';
        clientIdSpan.textContent = `Client ID: ${data.client_id}`;
        messageTextDiv.appendChild(clientIdSpan);
        messageTextDiv.appendChild(document.createElement('br')); // 改行を追加
        messageTextDiv.appendChild(document.createTextNode(data.message)); // メッセージを追加

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

// 色の衝突を検証するテスト関数
function testColorDistribution(numUsers) {
    const colors = new Set();
    for (let i = 0; i < numUsers; i++) {
        const userId = `user${i}`;
        colors.add(getClientColor(userId));
    }
    console.log(`Unique colors: ${colors.size} / ${numUsers}`);
}

// テスト実行
// testColorDistribution(100); 