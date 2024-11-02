
// Установите WebSocket-соединение
const socket = new WebSocket('wss://shipkz.ru:8001/ws/support/');

// Обработка события открытия соединения
socket.onopen = function(event) {
    console.log('WebSocket is open now.');
    // Здесь можно отправить сообщение сразу после открытия соединения
    socket.send(JSON.stringify({ message: 'Hello, Server!' }));
};

// Обработка сообщения от сервера
socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Message from server:', data);
    // Здесь можно обновить UI или выполнять другие действия
};

// Обработка ошибок
socket.onerror = function(error) {
    console.error('WebSocket Error:', error);
};

// Обработка закрытия соединения
socket.onclose = function(event) {
    console.log('WebSocket is closed now.');
};
