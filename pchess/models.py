from pchess import db


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
