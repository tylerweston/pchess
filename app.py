"""
Simple public chess game
Display a board and collect votes for all possible moves
every ten minutes, execute the move with the most votes.
If moves are tie, do a sudden death 2 minute run-off (??)
after that, just choose randomly
When a game ends in checkmate, at the next ten minute interval, start
a brand new game.

TODO:
- how does straw polling work?
    - need a database setup for this
- how do scheduled events work?
    - setup a celery/redis backend for this?

database:
GAME:
board -> move -> move -> ...

wish list:
- user profiles, if a move you voted for is chosen, you get points
- leader boards

"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import chess
# import psycopg2
# from configparser import ConfigParser
# https://python-chess.readthedocs.io/en/latest/


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:password@localhost:5432/pchess"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class SingleGame(db.Model):
    __tablename__ = 'single_game'
    # We don't really care about the game a chess board belongs to, do we?!
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    boards = db.relationship("Chessboard")


class Chessboard(db.Model):
    __tablename__ = 'chessboard'
    id = db.Column(db.Integer, primary_key=True)
    board = db.Column(db.String())
    parent_id = db.Column(db.Integer, db.ForeignKey('single_game.id'))


@app.route('/new_game/<game_name>', methods=['POST'])
def create_new_game(game_name):
    # Create a new chessboard in the opening position
    board = Chessboard(board=chess.STARTING_BOARD_FEN)
    # Create a new game
    game = SingleGame(name=game_name, boards=[board])
    # Add the board and the game to our database
    db.session.add(board)
    db.session.add(game)
    db.session.commit()
    return f"Create new game named {game_name}"


@app.route('/get_current_board')
def get_current_board():
    # returns a string representation of the currently active board
    # cur_board = Chessboard.query.all()[-1]
    # board = chess.Board(cur_board.board)
    board = get_current_active_game()
    #legal_moves = [str(move) for move in board.legal_moves]
    legal_moves = get_legal_moves(board)
    return {'board': str(board), 'possible_moves': legal_moves}

def get_current_active_game():
    cur_board = Chessboard.query.all()[-1]
    board = chess.Board(cur_board.board)
    return board

def get_legal_moves(board):
    return [str(move) for move in board.legal_moves]

@app.route('/make_move/<move>', methods=['POST'])
def make_move(move):
    curboard = get_current_active_game()
    legal_moves = get_legal_moves(curboard)
    if move not in legal_moves:
        return "Invalid move!"
    curboard.push_uci(move)
    board = Chessboard(board=curboard.fen())
    db.session.add(board)
    db.session.commit()
    return f"Made move {move}"


@app.route('/')
def hello_world():
    # connect()
    return 'Hello World! Changed version!'


@app.route('/new_board')
def new_board():
    new_board = chess.Board()
    legal_moves = [str(move) for move in new_board.legal_moves]
    return {'board': str(new_board), 'possible_moves': legal_moves}


if __name__ == '__main__':

    app.run(debug=True, host='0.0.0.0')
