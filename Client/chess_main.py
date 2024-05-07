import json
import threading
import pygame as p
import requests
import chess_engine
import sys
import convert_data
import socketio

BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250  # độ dài của bảng ghi chép nước đi
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8  # số hàng,cột trên bàn cờ
SQUARE_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 60
IMAGES = {}
chess_api = 'http://127.0.0.1:5000/api/v1/'
game_state = chess_engine.GameState()
sio = socketio.Client()
screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
clock = p.time.Clock()
my_turn = True
valid_moves = []
api_headers = {}


def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))


def get_valid_move_from_server():
    response = requests.get(chess_api + 'valid-move', headers=api_headers)
    valid_move_data = response.json()
    return convert_data.convert_valid_moves_data(valid_move_data, game_state.board)


def join_game():
    response = requests.get(chess_api + 'join-game')
    color = response.json()['color']
    return True if color == 'white' else False


@sio.event
def get_client_id(data):
    print(data)
    data_dict = json.loads(data)
    api_headers['client_id'] = data_dict['client_id']


@sio.event
def get_enemy_move(data_recv):
    global valid_moves, my_turn
    data = json.loads(data_recv)
    data_click = data['enemy_click']
    move = chess_engine.Move(data_click[0], data_click[1], game_state.board)
    game_state.makeMove(move)
    animateMove(move, screen, game_state.board, clock)
    valid_moves = convert_data.convert_valid_moves_data(data['valid_moves'], game_state.board)
    print('enemy running')
    my_turn = True


@sio.event
def notificarion(data):
    print('Thông báo server:', data)


def web_socket_start():
    sio.connect('http://localhost:5000')
    sio.emit('message', 'Hello from client')
    sio.wait()


def main():
    global my_turn, valid_moves
    websocket_thread = threading.Thread(target=web_socket_start)
    websocket_thread.daemon = True
    websocket_thread.start()
    my_turn = join_game()
    valid_moves = get_valid_move_from_server()
    p.init()
    p.display.set_caption("Player " + "white" if my_turn else "Player black")
    screen.fill(p.Color("white"))
    move_made = False
    animate = False
    loadImages()
    running = True
    square_selected = ()
    player_clicks = []
    game_over = False
    move_log_font = p.font.SysFont("Arial", 14, False, False)

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                sys.exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos()
                    col = location[0] // SQUARE_SIZE
                    row = location[1] // SQUARE_SIZE
                    if square_selected == (row, col) or col >= 8:  # click 1 ô 2 lần
                        square_selected = ()  # deselect
                        player_clicks = []  # clear clicks
                    else:
                        square_selected = (row, col)
                        player_clicks.append(square_selected)  # thêm ô thứ nhất và ô thứ 2
                    if len(player_clicks) == 2 and my_turn:  # sau khi chọn ô 2 (nước đi)
                        # gửi tọa độ nước đi cho server
                        data_click = [player_clicks[0], player_clicks[1]]
                        data = {
                            'data': data_click
                        }
                        response = requests.post(url=chess_api + '/make-move', json=data, headers=api_headers)
                        data_recv = response.json()
                        if data_recv['result'] == 'valid':
                            move_made = True
                            animate = True
                            move = chess_engine.Move(data_click[0], data_click[1], game_state.board)
                            game_state.makeMove(move)
                            # valid_moves = convert_data.convert_valid_moves_data(data_recv['valid_moves'],
                            #                                                     game_state.board)
                            if len(valid_moves) == 0:
                                print('game over')
                            valid_moves = []
                            my_turn = False
                        if not move_made:
                            player_clicks = [square_selected]
                        else:
                            square_selected = ()
                            player_clicks = []

        if move_made:
            if animate:
                animateMove(game_state.move_log[-1], screen, game_state.board, clock)
            move_made = False
            animate = False
        drawGameState(screen, game_state, valid_moves, square_selected)
        if not game_over:
            drawMoveLog(screen, game_state, move_log_font)
        if game_state.checkmate:
            game_over = True
            if game_state.white_to_move:
                drawEndGameText(screen, "Phe đen thắng - chiếu hết")
            else:
                drawEndGameText(screen, "Phe trắng thắng - chiếu hết")
        elif game_state.stalemate:
            game_over = True
            drawEndGameText(screen, "Stalemate")
        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, game_state, valid_moves, square_selected):
    drawBoard(screen)  # draw squares on the board
    highlightSquares(screen, game_state, valid_moves, square_selected)
    drawPieces(screen, game_state.board)  # draw pieces on top of those squares


def drawBoard(screen):
    """
    Draw the squares on the board.
    The top left square is always light.
    """
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[((row + column) % 2)]
            p.draw.rect(screen, color, p.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def highlightSquares(screen, game_state, valid_moves, square_selected):
    """
    Highlight square selected and moves for piece selected.
    """
    global my_turn
    if (len(game_state.move_log)) > 0:
        last_move = game_state.move_log[-1]
        s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
        s.set_alpha(100)
        s.fill(p.Color('green'))
        screen.blit(s, (last_move.end_col * SQUARE_SIZE, last_move.end_row * SQUARE_SIZE))
    if square_selected != ():
        row, col = square_selected
        # if game_state.board[row][col][0] == ('w' if my_turn else 'b'):
        if my_turn:
            s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))
            s.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.start_row == row and move.start_col == col:
                    screen.blit(s, (move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE))


def drawPieces(screen, board):
    """
    Draw the pieces on the board using the current game_state.board
    """
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def drawMoveLog(screen, game_state, font):
    """
    Draws the move log.

    """
    move_log_rect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color('black'), move_log_rect)
    move_log = game_state.move_log
    move_texts = []
    for i in range(0, len(move_log), 2):
        move_string = str(i // 2 + 1) + '. ' + str(move_log[i]) + " "
        if i + 1 < len(move_log):
            move_string += str(move_log[i + 1]) + "  "
        move_texts.append(move_string)

    moves_per_row = 3
    padding = 5
    line_spacing = 2
    text_y = padding
    for i in range(0, len(move_texts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i + j]

        text_object = font.render(text, True, p.Color('white'))
        text_location = move_log_rect.move(padding, text_y)
        text_y += text_object.get_height() + line_spacing


def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(text, False, p.Color("gray"))
    text_location = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - text_object.get_width() / 2,
                                                                 BOARD_HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, False, p.Color('black'))
    screen.blit(text_object, text_location.move(2, 2))


def animateMove(move, screen, board, clock):
    """
    Animating a move
    """
    global colors
    d_row = move.end_row - move.start_row
    d_col = move.end_col - move.start_col
    frames_per_square = 10  # frames to move one square
    frame_count = (abs(d_row) + abs(d_col)) * frames_per_square
    for frame in range(frame_count + 1):
        row, col = (move.start_row + d_row * frame / frame_count, move.start_col + d_col * frame / frame_count)
        drawBoard(screen)
        drawPieces(screen, board)
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        p.draw.rect(screen, color, end_square)
        if move.piece_captured != '--':
            if move.is_enpassant_move:
                enpassant_row = move.end_row + 1 if move.piece_captured[0] == 'b' else move.end_row - 1
                end_square = p.Rect(move.end_col * SQUARE_SIZE, enpassant_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            screen.blit(IMAGES[move.piece_captured], end_square)
        screen.blit(IMAGES[move.piece_moved], p.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        p.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
