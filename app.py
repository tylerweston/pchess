# Basic app runner for flask server

from pchess import app, socketio


if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0")
    # app.run(debug=True, host="0.0.0.0")
