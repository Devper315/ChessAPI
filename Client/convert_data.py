from chess_engine import Move


def convert_valid_moves_data(valid_moves_data, board):
    res = []
    for data in valid_moves_data:
        start_row = data['start_row']
        start_col = data['start_col']
        end_row = data['end_row']
        end_col = data['end_col']
        is_enpassant_move = data['is_enpassant_move']
        is_castle_move = data['is_castle_move']
        move = Move([start_row, start_col], [end_row, end_col], board, is_enpassant_move, is_castle_move)
        res.append(move)
    return res
