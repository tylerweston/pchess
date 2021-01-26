from pchess import app, db, celery, socketio
from datetime import datetime
from flask import request, render_template
import chess
from flask_socketio import SocketIO


# Socketio stuff

@socketio.on('json')
def handle_json(json):
    # Here we'll receive move vote in json format?
    print('received json: ' + str(json))

@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))

def some_function():
    # We want to let a client know the remaining time on the countdown timer
    # AND when a timer resets, we'll perform a move and let the front end clients
    # know to reset their timers!
    socketio.emit('some event', {'data': 42})


# Flask routes

@app.route("/new_task/<seconds>", methods=["POST"])
def new_task(seconds):
    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    res = celery_test_task.apply_async(args=[f"{dt_string}"], countdown=float(seconds))
    print(f"Float seconds:{float(seconds)}")
    print(res.id)
    return f"It is now {dt_string}, creating a new task to fire {seconds}s from now"


@app.route("/get_task_state/<task_id>", methods=["POST"])
def get_task_state(task_id):
    exec_time = celery.AsyncResult(task_id).date_done   # something like Tue, 26 Jan 2021 15:20:38 GMT
    task_state = celery.AsyncResult(task_id).status
    return {'exec_time': exec_time, 'task_state': task_state}

def get_time_until_task_fires(task_id):
    task = celery.AsyncResult(task_id)
    # TODO: Check that task really exists
    exec_time = task.date_done
    dt_string = datetime.now().strftime("%d %m %Y %H:%M:%S")
    # TODO: Make sure same timezone



@celery.task(name='pchess.celery_test_task')
def celery_test_task(time_created):
    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"I'm a task that was created at {time_created} and I'm now firing at {dt_string}")


@app.route("/new_game/<game_name>")
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


# TODO: make vote endpoint EITHER POST or GET, POST will take a SINGLE vote
#   where GET will return a count of ALL votes. Then we can use this service
#   internally as well!
@app.route("/get_vote/<vote>", methods=["POST"])
def post_vote(vote):
    # Add this vote to the database
    ip_address = request.remote_addr
    print(f"Requester IP: {ip_address}")
    # check that this user hasn't voted yet
    # if they have do we want to change their vote? or reject it?
    return f"You succesfully voted for {vote}"


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


@app.route("/test_route")
def test_route():
    return "This is only a test on changes to the code"


@app.route("/")
def main_page():
    # If we don't have a game yet, then we need to create one!
    board = get_current_active_game()
    board_str = board.fen()
    # we need to make sure that we get our board as .fen()
    legal_moves = get_legal_moves(board)
    print(f"Boad:{board_str}")
    return render_template('index.html', board=board_str, legal_moves=legal_moves)
