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
import chess
import psycopg2
from configparser import ConfigParser
# https://python-chess.readthedocs.io/en/latest/


app = Flask(__name__)


def config(filename='database.ini', section='postgresql'):
    """
    read config for postgres db from database.ini
    """
    # https://www.postgresqltutorial.com/postgresql-python/connect/
    parser = ConfigParser()
    parser.read(filename)

    db ={}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f"Section {section} not found in file {filename}")
    return db


def connect():
    """
    connect to postgresql database
    """
    conn = None
    try:
        params = config()

        # do the connecting
        print("Connecting to PostgreSQL db...")
        conn = psycopg2.connect(**params)

        # create cursor
        cur = conn.cursor()

        # execute a stmt.

        cur.execute("SELECT version()")
        db_version = cur.fetchone()
        print(f"PostgreSQL version: {db_version}")

        # close connection
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed")


@app.route('/')
def hello_world():
    connect()
    return 'Hello World!'


@app.route('/new_board')
def new_board():
    new_board = chess.Board()
    legal_moves = [str(move) for move in new_board.legal_moves]
    return {'board': str(new_board), 'possible_moves': legal_moves}


@app.route('/make_move/<move>', methods=['POST'])
def make_move(move):
    # TODO: This call won't come from the front-end, it will come from the backend
    # execute a move and return the new board and moves
    return f"Executing move: {move}"


if __name__ == '__main__':

    app.run()
