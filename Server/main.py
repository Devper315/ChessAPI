import json

from flask import Flask, jsonify, request
from flask_socketio import SocketIO, join_room

import chess_engine
import convert_data

app = Flask(__name__)
socketio = SocketIO(app)
game_state = chess_engine.GameState()
valid_moves = game_state.getValidMoves()
white_turn = True
black_turn = False
players = {}


def swap_turn():
    global white_turn, black_turn
    white_turn = not white_turn
    black_turn = not black_turn


def send_data_to_client(client_id, data):
    info = {"client_id": data}
    json_data = json.dumps(info)
    socketio.emit('get_client_id', json_data, room=client_id)


def send_move_to_enemy(client_id, data):
    json_data = json.dumps(data)
    socketio.emit('get_enemy_move', json_data, room=client_id)


@app.route('/api/v1/valid-move')
def get_valid_move():
    data = convert_data.prepare_data_list_valid_moves(valid_moves)
    return jsonify(data)


@app.route('/api/v1/join-game')
def join_game():
    data = {"color": "white" if white_turn else 'black'}
    return jsonify(data)


@socketio.on('connect')
def client_connect_to_server():
    client_id = request.sid
    join_room(client_id)
    if white_turn:
        players['white'] = request.sid
    else:
        players['black'] = request.sid
    swap_turn()
    print(players)
    print(f'Client {client_id} connected')
    send_data_to_client(client_id, client_id)


@app.route('/api/v1/make-move', methods=['POST'])
def make_move():
    global valid_moves
    result = {'result': 'invalid'}
    data_click = request.json['data']
    move = chess_engine.Move(data_click[0], data_click[1], game_state.board)
    for i in range(len(valid_moves)):
        if move == valid_moves[i]:
            current_client_id = request.headers.get("client_id")
            game_state.makeMove(valid_moves[i])
            valid_moves = game_state.getValidMoves()
            data_for_enemy = {
                'enemy_click': data_click,
                'valid_moves': convert_data.prepare_data_list_valid_moves(valid_moves)
            }
            for key in players:
                if players[key] != current_client_id:
                    print('enemy:', players[key])
                    send_move_to_enemy(players[key], data_for_enemy)
            if len(valid_moves) == 0:
                print('game_over')
                socketio.emit("notificarion", 'Game over')
            result.update({
                'result': 'valid',
                # 'valid_moves': convert_data.prepare_data_list_valid_moves(valid_moves)
            })
            break

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
