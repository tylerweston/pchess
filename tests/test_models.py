from pchess.models import Chessboard, Vote
from pchess import db
from pchess import app
import chess
import pytest


def test_new_vote():
    vote = Vote(move="a2a3")
    assert vote.move == "a2a3"


# @pytest.fixture(scope="function")
def test_new_chessboard(function_scoped_container_getter):
    chessboard = Chessboard(board=chess.STARTING_FEN)
    assert chessboard.board == chess.STARTING_FEN


# Models without hitting the database
# @pytest.fixture(scope="function")
def test_vote_transaction(db_session):
    print(f"database uri: {app.config['SQLALCHEMY_DATABASE_URI']}")
    vote = Vote(move="b2b3")
    db.session.add(vote)
    db.session.commit()

