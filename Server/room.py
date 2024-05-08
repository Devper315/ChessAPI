from chess_engine import GameState, Move


class Room:
    def __init__(self, white_id):
        self.white_id = white_id
        self.playing_id = white_id
        self.waiting_id = None
        self.black_id = None
        self.game_state = GameState()
        self.valid_moves = self.game_state.getValidMoves()

    def handle_player_click(self, player_click):
        move = Move(player_click[0], player_click[1], self.game_state.board)
        for i in range(len(self.valid_moves)):
            if move == self.valid_moves[i]:
                self.game_state.makeMove(move)
                self.update_valid_moves()
                return 'valid'
        return 'invalid'

    def prepare_data_list_valid_moves(self):
        res = []
        for move in self.valid_moves:
            res.append({
                'start_row': move.start_row,
                'start_col': move.start_col,
                'end_row': move.end_row,
                'end_col': move.end_col,
                'is_enpassant_move': move.is_enpassant_move,
                'is_castle_move': move.is_castle_move,
            })
        return res

    def update_valid_moves(self):
        self.valid_moves = self.game_state.getValidMoves()

    def swap_player(self):
        tmp = self.playing_id
        self.playing_id = self.waiting_id
        self.waiting_id = tmp
