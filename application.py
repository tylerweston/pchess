# Basic app runner for flask server

from pchess import application, socketio


if __name__ == "__main__":
    socketio.run(application, debug=True, host="0.0.0.0")
    # app.run(debug=True, host="0.0.0.0")
