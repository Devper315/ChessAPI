import pickle
import socket
import threading

# Hàm xử lý kết nối của client
def handle_client(client_socket):
    while True:
        s = input('Nhập dữ liệu gửi client: ')
        data = pickle.dumps(s)
        client_socket.send(data)

# Khởi tạo socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 8888))
server_socket.listen(5)

print("Server listening on port 8888")

while True:
    # Chấp nhận kết nối từ client
    client_socket, addr = server_socket.accept()
    print("Connected to", addr)
    # Bắt đầu một luồng mới để xử lý kết nối
    client_handler = threading.Thread(target=handle_client, args=(client_socket,))
    client_handler.start()
