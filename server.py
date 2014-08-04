from flask import Flask, render_template, url_for
from flask.ext.socketio import SocketIO, emit

import game

app = Flask(__name__)
socketio = SocketIO(app)

@app.route("/")
def index():
    return render_template("play.html")

@socketio.on("begin")
def blah(msg):
    print "Connection"
    m = game.Arena(w=msg["width"], h=msg["height"])
    emit("update", str(m))


if __name__ == "__main__":
    socketio.run(app)
