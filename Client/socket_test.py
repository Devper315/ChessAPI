import pickle
import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("127.0.0.1", 8888))
while True:
    print('Đang chờ dữ liệu mới')
    data_recv = client_socket.recv(4096)
    data = pickle.loads(data_recv)
    print('Dữ liệu nhận được:', data)
