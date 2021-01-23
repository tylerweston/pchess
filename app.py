# Basic app runner for flask server

from pchess import app
from flask_socketio import SocketIO

if __name__ == "__main__":
    # socketio = SocketIO(app)
    # socketio.run(app)
    app.run(debug=True, host="0.0.0.0")
