import sys
import traceback

from flask import Flask, render_template, url_for
from flask.ext.socketio import SocketIO, emit

import game

app = Flask(__name__)
socketio = SocketIO(app)

m = game.Game(debug=True)

# TODO make this work!
def onError(self, t, value, trace):
    message = "".join(traceback.format_exception(t, value, trace))
    print "ERROR\t", message
    emit("error", message)

@app.route("/")
def index():
    return render_template("play.html")

@socketio.on("begin")
def begin(msg):
    try:
        m.addPlayer(msg["username"])
        player = m.players[msg["username"]]
        emit("ack user")
    except ValueError:
        emit("error", "name already taken")

@socketio.on("move")
def move(msg):
    direction = msg["direction"]
    user = msg["username"]

    m.players[user].move(direction)

@socketio.on("turn")
def turn(msg):
    direction = msg["direction"]
    user = msg["username"]

    m.players[user].turn(direction)

@socketio.on("request frame")
def updateMap(msg):
    user = msg["username"]
    emit("frame", str(m.players[user]))

if __name__ == "__main__":
    app.debug = True
    sys.excepthook = onError
    socketio.run(app, port=8080)
