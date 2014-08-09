from flask import Flask, render_template, url_for
from flask.ext.socketio import SocketIO, emit

import game

app = Flask(__name__)
socketio = SocketIO(app)

m = game.Game(debug=True)

@app.route("/")
def index():
    return render_template("play.html")

@socketio.on("begin")
def blah(msg):
    m.addPlayer(msg["username"])
    player = m.players[msg["username"]]
    emit("update", str(player))

@socketio.on("move")
def move(msg):
    direction = msg["direction"]
    user = msg["username"]

    m.players[user].move(direction)
    emit("update", str(m.players[user]))

@socketio.on("turn")
def turn(msg):
    direction = msg["direction"]
    user = msg["username"]

    m.players[user].turn(direction)
    emit("update", str(m.players[user]))

if __name__ == "__main__":
    app.debug = True
    socketio.run(app, port=8080, host='0.0.0.0')
