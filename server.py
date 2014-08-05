from flask import Flask, render_template, url_for
from flask.ext.socketio import SocketIO, emit

import game

app = Flask(__name__)
socketio = SocketIO(app)

m = game.Game()

@app.route("/")
def index():
    return render_template("play.html")

@socketio.on("begin")
def blah(msg):
    user = msg["username"]

    m.addPlayer(user)
    print str(m.players[user])
    emit("update", str(m.players[user]))

@socketio.on("move")
def move(msg):
    direction = msg["direction"]
    user = msg["username"]

    print direction
    m.players[user].move(direction)
    print str(m.players[user])
    emit("update", str(m.players[user]))

if __name__ == "__main__":
    socketio.run(app, port=8080, host='0.0.0.0')
