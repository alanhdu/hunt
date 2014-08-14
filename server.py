import gevent
from flask import Flask, render_template, copy_current_request_context
from flask.ext.socketio import SocketIO, emit, join_room

import game

app = Flask(__name__)
socketio = SocketIO(app)

m = game.Game(debug=True)

@app.route("/")
def index(interval=0.2):
    @copy_current_request_context
    def run():
        while True:
            gevent.sleep(interval)
            for username, player in m.players.viewitems():
                socketio.emit("update", str(player), room=username)
    gevent.spawn(run)   # use separate thread

    return render_template("play.html")

@socketio.on("begin")
def begin(msg):
    m.addPlayer(msg["username"])
    player = m.players[msg["username"]]
    join_room(msg["username"])

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

if __name__ == "__main__":
    app.debug = True
    socketio.run(app, port=8080)
