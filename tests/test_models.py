from pchess.models import Chessboard, Vote
from pchess import db
import chess


# Models without hitting the database
def test_new_vote():
    vote = Vote(move="a2a3")
    assert vote.move == "a2a3"


def test_new_chessboard():
    chessboard = Chessboard(board=chess.STARTING_FEN)
    assert chessboard.board == chess.STARTING_FEN


def test_vote_transaction(db_session):
    vote = Vote(move="b2b3")
    db.session.add(vote)
    db.session.commit()