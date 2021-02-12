# Database models for pchess
from pchess import db


class SingleGame(db.Model):
    __tablename__ = 'single_game'
    # We don't really care about the game a chess board belongs to, do we?!
    id = db.Column(db.Integer, primary_key=True)    # this will let us make decisions on which side a player will be on
    start_datetime = db.Column(db.DateTime)         # keep track of how long games last
    # boards = db.relationship("Chessboard")


class Chessboard(db.Model):
    __tablename__ = 'chessboard'
    id = db.Column(db.Integer, primary_key=True)
    board = db.Column(db.String())
    legal_moves = db.relationship('LegalMove', backref='chessboard', lazy=True)
    # moves = db.Column(db.String())    # moves is a list so we don't want to store it like this?
    # parent_id = db.Column(db.Integer, db.ForeignKey('single_game.id'))
    # votes = db.relationship("Vote")


class LegalMove(db.Model):
    __tablename__ = 'legalmove'
    id = db.Column(db.Integer, primary_key=True)
    move = db.Column(db.String())
    chessboard_id = db.Column(db.Integer, db.ForeignKey('chessboard.id'), nullable=False)


class Vote(db.Model):
    __tablename__ = 'vote'
    id = db.Column(db.Integer, primary_key=True)
    move = db.Column(db.String())
    # board_for_move = db.Column(db.Integer, db.ForeignKey('chessboard.id'))
