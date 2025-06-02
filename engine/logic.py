import chess
import chess.pgn
import io
# Creating board
# Make move, validate the move

# consumers.new_move -> engine.make_move(fen from opponent) -> fen, SAN(move), is_checkmate

def create_board(fen=None):
    if fen:
        board = chess.Board(fen)
    board = chess.Board()
    return board

def make_move(board:chess.Board, pos1:str, pos2:str):
    move = chess.Move.from_uci(pos1 + pos2)
    if move in board.legal_moves:
        board.push(move)
        fen = board.fen()
        check = board.is_check()
        checkmate = board.is_checkmate()
        return {
            'fen': fen,
            'move': move,
            'check': check,
            'checkmate': checkmate
        }
    return {
        'error': 'illegal move'
    }

def board_to_pgn(board):
    game = chess.pgn.Game.from_board(board)
    exporter = io.StringIO()
    print(game, file=exporter, end="\n\n")
    return exporter.getvalue()