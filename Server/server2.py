import json

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, join_room

app = Flask(__name__)
socketio = SocketIO(app)


@socketio.on('connect')
def handle_connect():
    client_id = request.sid
    join_room(client_id)
    print(f'Client {client_id} connected')
    send_data_to_client(client_id, client_id)


@app.route('/api/v1/test-socket')
def test_socket():
    socket_client_id = request.headers.get('client_id')
    return jsonify(socket_client_id)


def send_data_to_client(client_id, data):
    info = {"Client ID": data}
    json_data = json.dumps(info)
    socketio.emit('message', json_data, room=client_id)


if __name__ == '__main__':
    socketio.run(app, port=5000, allow_unsafe_werkzeug=True)
