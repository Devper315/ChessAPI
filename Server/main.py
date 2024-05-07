from flask import Flask, jsonify, request
from flask_socketio import SocketIO

import chess_engine
import convert_data

app = Flask(__name__)
socketio = SocketIO(app)
game_state = chess_engine.GameState()
valid_moves = game_state.getValidMoves()
white_turn = True
black_turn = False


def swap_turn():
    global white_turn, black_turn
    white_turn = not white_turn
    black_turn = not black_turn


@socketio.on('message')
def handle_message(message):
    print('Received message:', message)
    socketio.send('Response from server: ' + message)


@app.route('/api/v1/valid-move')
def get_valid_move():
    data = convert_data.prepare_data_list_valid_moves(valid_moves)
    return jsonify(data)


@app.route('/api/v1/join-game')
def join_game():
    data = {"color": "white" if white_turn else 'black'}
    swap_turn()
    return jsonify(data)


@app.route('/api/v1/make-move', methods=['POST'])
def make_move():
    global valid_moves
    socketio.send("Đánh 1 nước")
    result = {'result': 'invalid'}
    data_click = request.json['data']
    move = chess_engine.Move(data_click[0], data_click[1], game_state.board)
    for i in range(len(valid_moves)):
        if move == valid_moves[i]:
            game_state.makeMove(valid_moves[i])
            valid_moves = game_state.getValidMoves()
            result.update({
                'result': 'valid',
                'valid_moves': convert_data.prepare_data_list_valid_moves(valid_moves)
            })

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
