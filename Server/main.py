import json

from flask import Flask, jsonify, request
from flask_socketio import SocketIO, join_room
from room import Room
app = Flask(__name__)
socketio = SocketIO(app)
room_list = []


def send_data_to_client(client_id, data):
    info = {"client_id": data}
    json_data = json.dumps(info)
    socketio.emit('get_client_id', json_data, room=client_id)


def send_move_to_enemy(client_id, data):
    json_data = json.dumps(data)
    socketio.emit('get_enemy_move', json_data, room=client_id)


@app.route('/api/v1/start-game')
def start_game():
    white_client_id = request.headers.get("client_id")
    new_room = Room(white_client_id)
    room_list.append(new_room)
    data = new_room.prepare_data_list_valid_moves()
    return jsonify(data)


@app.route('/api/v1/accept-challenge')
def accept_challenge():
    client_id = request.headers.get('client_id')
    challenger_id = request.json['challenger_id']
    room = find_room_by_player_id(challenger_id)
    room.black_id = client_id
    room.waiting_id = client_id
    data = room.prepare_data_list_valid_moves()
    return jsonify(data)


@socketio.on('connect')
def client_connect_to_server():
    client_id = request.sid
    join_room(client_id)
    print('Client %s connected' % client_id)
    send_data_to_client(client_id, client_id)


def find_room_by_player_id(player_id):
    for room in room_list:
        if room.white_id == player_id or room.black_id == player_id:
            return room


@app.route('/api/v1/make-move', methods=['POST'])
def make_move():
    player_click = request.json['data']
    client_id = request.headers.get("client_id")
    room = find_room_by_player_id(client_id)
    result = room.handle_player_click(player_click)
    if result == 'valid':
        data_for_enemy = {
            'enemy_click': player_click,
            'valid_moves': room.prepare_data_list_valid_moves()
        }
        send_move_to_enemy(room.waiting_id, data_for_enemy)
        room.swap_player()
    if len(room.valid_moves) == 0:
        print('game_over')
        socketio.emit("notificarion", 'Game over')

    return jsonify({'result': result})


if __name__ == '__main__':
    app.run(debug=True)
