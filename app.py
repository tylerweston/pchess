"""
Simple public chess game
Display a board and collect votes for all possible moves
every five minutes, execute the move with the most votes.
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

from pchess import app

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
