import subprocess
import glob

import gevent
from flask import Flask, render_template, copy_current_request_context
from flask.ext.socketio import SocketIO, emit, join_room

import game

app = Flask(__name__)
socketio = SocketIO(app)

m = game.Game()

@app.route("/")
def index(interval=0.05):
    @copy_current_request_context
    def run():
        while True:
            gevent.sleep(interval)
            m.update()
            for username, player in m.players.viewitems():
                socketio.emit("update", player.to_json(), room=username)
    gevent.spawn(run)   # use separate thread

    return render_template("play.html")

@socketio.on("begin")
def begin(msg):
    try:
        m.addPlayer(msg["username"])
        player = m.players[msg["username"]]
        join_room(msg["username"])
        emit("ack user")
    except ValueError:
        emit("error", "name already taken")

@socketio.on("move")
def move(msg):
    direction = msg["direction"]
    user = msg["username"]

    m.players[user].queue("move", direction)

@socketio.on("turn")
def turn(msg):
    direction = msg["direction"]
    user = msg["username"]
    m.players[user].queue("turn", direction)

@socketio.on("fire")
def fire(msg):
    user = msg["username"]
    m.players[user].queue("fire")

if __name__ == "__main__":
    app.debug = True
    for path in glob.glob("static/*.coffee"):
        subprocess.call(["coffee", "-c", path])
    socketio.run(app, port=8080)
