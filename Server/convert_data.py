def prepare_data_list_valid_moves(valid_moves):
    res = []
    for move in valid_moves:
        res.append(prepare_data_valid_move(move))
    return res


def prepare_data_valid_move(move):
    return {
        'start_row': move.start_row,
        'start_col': move.start_col,
        'end_row': move.end_row,
        'end_col': move.end_col,
        'is_enpassant_move': move.is_enpassant_move,
        'is_castle_move': move.is_castle_move,
    }
