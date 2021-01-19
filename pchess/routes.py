from pchess import app, db, celery
from datetime import datetime
import chess
from celery.result import AsyncResult

print("in pchess routes.py")

@app.route("/new_task/<seconds>", methods=["POST"])
def new_task(seconds):
    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    res = celery_test_task.apply_async(args=[f"{dt_string}"], countdown=float(seconds))
    print(f"Float seconds:{float(seconds)}")
    print(res.id)
    return f"It is now {dt_string}, creating a new task to fire {seconds}s from now"

@app.route("/get_task_state/<task_id>", methods=["POST"])
def get_tasl_state(task_id):
    return celery.AsyncResult(task_id).status

@celery.task(name='pchess.celery_test_task')
def celery_test_task(time_created):
    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"I'm a task that was created at {time_created} and I'm now firing at {dt_string}")

@app.route("/new_game/<game_name>", methods=["POST"])
def create_new_game(game_name):
    from pchess.models import Chessboard, SingleGame
    # Create a new chessboard in the opening position
    board = Chessboard(board=chess.STARTING_BOARD_FEN)
    # Create a new game
    game = SingleGame(name=game_name, boards=[board])
    # Add the board and the game to our database
    db.session.add(board)
    db.session.add(game)
    db.session.commit()
    return f"Create new game named {game_name}"


@app.route("/get_current_board")
def get_current_board():
    # returns a string representation of the currently active board
    board = get_current_active_game()
    if board is None:
        return "No current board"
    legal_moves = get_legal_moves(board)
    return {"board": str(board), "possible_moves": legal_moves}


def get_current_active_game():
    from pchess.models import Chessboard

    cur_board = Chessboard.query.all()[-1]
    if cur_board is None:
        return None
    board = chess.Board(cur_board.board)
    return board


def get_legal_moves(board):
    return [str(move) for move in board.legal_moves]


@app.route("/make_move/<move>", methods=["POST"])
def make_move(move):
    from pchess.models import Chessboard
    # we want to get the current active board to make sure we can
    # grab the proper parent from our board as well!
    # so that way we can keep a series of boards organized into
    # their proper games!
    curboard = get_current_active_game()
    legal_moves = get_legal_moves(curboard)
    if move not in legal_moves: # should never happen since only legal moves are presented to users
        return "Invalid move!"
    curboard.push_uci(move)
    # here we would look for check/mate?
    board = Chessboard(board=curboard.fen())
    db.session.add(board)
    db.session.commit()
    # pack this up with a status flag that indicates if check or mate
    # or something has been reached
    return f"Made move {move}"


@app.route("/")
def hello_world():
    return "pchess v0.01 - Tyler Weston 2020"