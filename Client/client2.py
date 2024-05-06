import socketio

# Tạo một đối tượng SocketIO để kết nối tới máy chủ WebSocket
sio = socketio.Client()


# Hàm được gọi khi kết nối thành công
@sio.event
def connect():
    print('Connected to server')


# Hàm được gọi khi nhận được tin nhắn từ máy chủ
@sio.event
def message(data):
    print('Received message from server:', data)


if __name__ == '__main__':
    sio.connect('http://localhost:5000')
    sio.emit('message', 'Hello from client')
    sio.wait()
