import subprocess
import glob

import gevent
from flask import Flask, render_template, copy_current_request_context, request
from sockets import SocketIO, join_room, emit
from socketio.namespace import BaseNamespace

import game
import custom_exceptions as excpt

app = Flask(__name__)
socketio = SocketIO(app, excpt.exception_handler)

m = game.Game()

@app.route("/")
def index(interval=0.05):
    @copy_current_request_context
    def run():
        while True:
            gevent.sleep(interval)
            m.update()

            emit = socketio.emit
            jobs = [gevent.spawn(emit, "update", player.to_json(), room=uname)
                    for uname, player in m.players.iteritems()]
            gevent.joinall(jobs)

    gevent.spawn(run)

    return render_template("play.html")

@socketio.on("begin")
def begin(msg):
    m.addPlayer(msg["username"])
    player = m.players[msg["username"]]
    join_room(msg["username"])

@socketio.on("logoff")
def logoff(msg):
    uname = msg["username"]
    del m.players[uname]

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
