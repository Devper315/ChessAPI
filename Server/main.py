from flask import Flask, jsonify, request

import chess_engine
import convert_data

app = Flask(__name__)
game_state = chess_engine.GameState()
valid_moves = game_state.getValidMoves()
white_turn = True
black_turn = False


def swap_turn():
    global white_turn, black_turn
    white_turn = not white_turn
    black_turn = not black_turn


@app.route('/api/v1/valid-move')
def get_valid_move():
    data = convert_data.prepare_data_list_valid_moves(valid_moves)
    return jsonify(data)


@app.route('/api/v1/make-move', methods=['POST'])
def make_move():
    global valid_moves
    result = {'result': 'invalid'}
    data_click = request.json['data']
    move = chess_engine.Move(data_click[0], data_click[1], game_state.board)
    for i in range(len(valid_moves)):
        if move == valid_moves[i]:
            game_state.makeMove(valid_moves[i])
            valid_moves = game_state.getValidMoves()
            result['result'] = 'valid'

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
