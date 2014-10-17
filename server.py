import subprocess
import glob

import gevent
import markdown
from flask import Flask, render_template, copy_current_request_context, request
from flask import Markup
from flask.ext.socketio import SocketIO, emit, join_room
from socketio.namespace import BaseNamespace

import game
import custom_exceptions as excpt

app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on_error_default
def exception_handler(value):
    if isinstance(value, excpt.UserError):
        emit("error", str(value))
    else:
        raise value

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

@app.route("/instructions")
def instruct():
    with open("INSTRUCTIONS.md") as fin:
        content = markdown.markdown(fin.read())
        # Markup to escape html characters
        return render_template("instructions.html", content=Markup(content))

@socketio.on("begin")
def begin(msg):
    m.addPlayer(msg["username"])
    player = m.players[msg["username"]]
    join_room(msg["username"])

    socketio.emit("acknowledged", {}, room=msg["username"])

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

@socketio.on("bomb")
def bomb(msg):
    user = msg["username"]
    m.players[user].queue("bomb")

@socketio.on("scan")
def scan(msg):
    user = msg["username"]
    m.players[user].scan = not m.players[user].scan

@socketio.on("cloak")
def scan(msg):
    user = msg["username"]
    m.players[user].cloak = not m.players[user].cloak

if __name__ == "__main__":
    socketio.run(app, port=8080)
