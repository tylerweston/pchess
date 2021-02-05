from pchess import app, db, celery, socketio
from datetime import datetime
from flask import request, render_template
from flask_socketio import SocketIO
import chess
from pchess.models import Vote, Chessboard
from collections import Counter

main_timer_id = None


@socketio.on("vote")
def handle_vote(json):
    this_vote = Vote(move=json["data"])
    db.session.add(this_vote)
    db.session.commit()
    print("receive vote: " + str(json))


def tell_client_timer_expire():
    send_client_new_board_pos(get_current_board())
    socketio.emit("reset_time", broadcast=True)


@socketio.on("new_board_pos")
def send_client_new_board_pos(new_board):
    socketio.emit("new_board_pos", str(new_board.fen()), broadcast=True)


def get_time_until_task_fires(task_id):
    task = celery.AsyncResult(task_id)
    # TODO: Check that task really exists
    exec_time = task.date_done
    dt_string = datetime.now().strftime("%d %m %Y %H:%M:%S")
    # TODO: Make sure same timezone


@celery.task(name="pchess.timer")
def main_timer(make_new_game):
    with app.app_context():
        if make_new_game:
            create_new_game()
        else:
            # send off timer expire function
            server_timer_expire()
            tell_client_timer_expire()
            # start a new timer for sixty seconds from now
            # we'll write this to a database
            _, checkmate = check_mate_status()
            if checkmate:
                start_main_timer(make_new_game=True)
            else:
                start_main_timer(make_new_game=False)


def start_main_timer(make_new_game):
    print("Starting a new timer")
    main_timer_id = main_timer.apply_async(args=[make_new_game], countdown=30)


@app.route("/new_game")
def create_new_game():
    # Remove all boards in the database
    clear_chessboards()
    # Create a new chessboard in the opening position
    board = Chessboard(board=chess.STARTING_FEN)
    # Create a new game
    # game = SingleGame(
    #     boards=[board]
    # )  # TODO: We don't actually do anything with the game?
    # Add the board and the game to our database
    db.session.add(board)
    # db.session.add(game)
    db.session.commit()
    # make sure we have no votes left
    clear_votes()
    # Launch a new timer!
    start_main_timer(make_new_game=False)
    return f"Created a new game"


def get_current_board():
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
    # we want to get the current active board to make sure we can
    # grab the proper parent from our board as well!
    # so that way we can keep a series of boards organized into
    # their proper games!
    curboard = get_current_board()
    legal_moves = get_legal_moves(curboard)
    if (
        move not in legal_moves
    ):  # should never happen since only legal moves are presented to users
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
    print(f"Board:{board_str}")
    white_turn = board_str.split(" ")[1] == "w"
    check, checkmate = check_mate_status()
    return render_template(
        "index.html",
        board=board_str,
        legal_moves=legal_moves,
        white_turn=white_turn,
        check=check,
        checkmate=checkmate,
    )


def check_mate_status():
    board = get_current_board()
    return board.is_check(), board.is_checkmate()


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
    all_votes = Vote.query.all()
    # print([vote.move for vote in all_votes])
    count = Counter([vote.move for vote in all_votes])
    chosen_move = count.most_common(1)
    if len(chosen_move) > 0:
        chosen_move = chosen_move[0]
    else:
        print("No votes!")
    return chosen_move


def clear_votes():
    # remove all votes in the database and make way for new ones
    # no need to store old votes
    results = db.session.query(Vote)
    if results:
        results.delete()
    db.session.commit()

def clear_chessboards():
    # Remove chessboards once we've finished a game
    results = db.session.query(Chessboard)
    if results:
        results.delete()
    db.session.commit()