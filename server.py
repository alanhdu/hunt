import threading

from flask import Flask, render_template
from flask.ext.socketio import SocketIO, emit, join_room

import game

def setInterval(interval):
    # use closure to set interval
    def decorator(func):
        def wrap(*args, **kwargs):
            stop = threading.Event()
            def run():
                while not stop.is_set():
                    stop.wait(interval)
                    func(*args, **kwargs)

            t = threading.Timer(0, run)
            t.daemon = True
            t.start()
            return stop
        return wrap
    return decorator

app = Flask(__name__)
socketio = SocketIO(app)

m = game.Game(debug=True)

@app.route("/")
def index():
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

@setInterval(0.2)       # update once every 0.2 seconds
def update():
    print "UPDATING"
    for username, player in m.players.iteritems():
        print username
        emit("update", str(player), room=username)

if __name__ == "__main__":
    app.debug = True
    update()
    socketio.run(app, port=8080)
