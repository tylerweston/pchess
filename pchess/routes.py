from pchess import app, db, celery, socketio
from datetime import datetime
from flask import request, render_template
from flask_socketio import SocketIO
import chess
from pchess.models import Vote
from collections import Counter

main_timer_id = None

# Socket.io stuff

@socketio.on('json')
def handle_json(json):
    # Here we'll receive move vote in json format?
    print('received json: ' + str(json))


@socketio.on('event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))


@socketio.on('vote')
def handle_vote(json):
    this_vote = Vote(move=json['data'])
    db.session.add(this_vote)
    db.session.commit()
    print('receive vote: ' + str(json))


def tell_client_timer_expire():
    # socketio = SocketIO(message_queue='redis://redis:6379')
    print("Telling clients the timer expired!")
    # todo: we need to send new legal moves, and a new board position here
    send_client_new_board_pos(get_current_board())
    socketio.emit('reset_time', broadcast=True)


@socketio.on('new_board_pos')
def send_client_new_board_pos(new_board):
    # socketio = SocketIO(message_queue='redis://redis:6379')
    print("Sending new board to client:")
    print(new_board)
    socketio.emit('new_board_pos', str(new_board.fen()), broadcast=True)


def some_function():
    # We want to let a client know the remaining time on the countdown timer
    # AND when a timer resets, we'll perform a move and let the front end clients
    # know to reset their timers!
    # This will send a message to ALL connected clients
    socketio.emit('some event', {'data': 42})


# Flask routes
@app.route("/reset", methods=["POST"])
def reset_time():
    # this is a test route, TODO: Remove
    # server_timer_expire()
    tell_client_timer_expire()
    return "Time reset"


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


@celery.task(name="pchess.timer")
def main_timer():
    with app.app_context():
        print("Main timer going off!")
        # send off timer expire function
        server_timer_expire()
        tell_client_timer_expire()
        # start a new timer for sixty seconds from now
        # we'll write this to a database
        start_main_timer()


def start_main_timer():
    print("Starting a new timer")
    main_timer_id = main_timer.apply_async(countdown=10)


@celery.task(name='pchess.celery_test_task')
def celery_test_task(time_created):
    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"I'm a task that was created at {time_created} and I'm now firing at {dt_string}")


@app.route("/new_game")
def create_new_game():
    print("Creating a new game")
    from pchess.models import Chessboard, SingleGame
    # Create a new chessboard in the opening position
    board = Chessboard(board=chess.STARTING_BOARD_FEN)
    # Create a new game
    game = SingleGame(boards=[board])
    # Add the board and the game to our database
    db.session.add(board)
    db.session.add(game)
    db.session.commit()
    # make sure we have no votes left
    clear_votes()
    # Launch a new timer!
    start_main_timer()
    return f"Created a new game"


@app.route("/get_vote/<vote>", methods=["POST"])
def post_vote(vote):
    # Add this vote to the database
    ip_address = request.remote_addr
    print(f"Requester IP: {ip_address}")
    # check that this user hasn't voted yet
    # if they have do we want to change their vote? or reject it?
    return f"You succesfully voted for {vote}"


# @app.route("/get_current_board")
# def get_current_board():
#     # returns a string representation of the currently active board
#     board = get_current_active_game()
#     if board is None:
#         return "No current board"
#     legal_moves = get_legal_moves(board)
#     return {"board": str(board), "possible_moves": legal_moves}


def get_current_board():
    from pchess.models import Chessboard
    cur_board = Chessboard.query.all()
    if len(cur_board) > 0:
        cur_board = cur_board[-1]
    else:
        create_new_game()
        return get_current_board()
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
    curboard = get_current_board()
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


@app.route("/about")
def about():
    return "This will be the about page"


@app.route("/index")
def index():
    return main_page()


@app.route("/")
def main_page():
    # If we don't have a game yet, then we need to create one!
    board = get_current_board()
    board_str = board.fen()
    # we need to make sure that we get our board as .fen()
    legal_moves = get_legal_moves(board)
    print(f"Boad:{board_str}")
    white_turn = board_str.split(' ')[1] == 'w'
    return render_template('index.html', board=board_str, legal_moves=legal_moves, white_turn=white_turn)


def server_timer_expire():
    # pass
    # count all votes
    chosen_move = count_votes()
    # remove old votes
    clear_votes()
    if len(chosen_move) > 0:
        # make the chosen move happen
        make_move(chosen_move[0])


def count_votes():
    # This counts the votes currently in the data base and returns the
    # most voted for move, and the number of votes it received
    print("Counting votes")
    # with app.app_context():
    all_votes = Vote.query.all()
    # print([vote.move for vote in all_votes])
    count = Counter([vote.move for vote in all_votes])
    chosen_move = count.most_common(1)
    if len(chosen_move) > 0:
        chosen_move = chosen_move[0]
    else:
        print("No votes!")
    print(chosen_move)
    return chosen_move


def clear_votes():
    # remove all votes in the database and make way for new ones
    # no need to store old votes
    print("Clearing votes")
    results = db.session.query(Vote)
    if results:
        results.delete()
    db.session.commit()
