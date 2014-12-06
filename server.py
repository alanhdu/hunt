import gevent
import markdown
from flask import Flask, render_template, session
from flask import Markup
from flask.ext.socketio import SocketIO, join_room, emit

import game
import custom_exceptions as excpt

app = Flask(__name__)
app.secret_key = "It's a secret!"
app.debug = True
socketio = SocketIO(app)

@socketio.on_error_default
def exception_handler(value):
    if isinstance(value, excpt.UserError):
        emit("error", str(value))
    else:
        raise value

m = game.Game(debug=True)
running = None
def run(interval=0.025):
    while True:
        gevent.sleep(interval)
        m.update()

        emit = socketio.emit
        jobs = [gevent.spawn(emit, "update",
                     {"player": player.to_json(), "scores": m.to_json()},
                     room=uname)
                for uname, player in m.players.iteritems()]
        gevent.joinall(jobs)

@app.route("/")
def index():
    return render_template("play.html")

@app.route("/instructions")
def instruct():
    with open("INSTRUCTIONS.md") as fin:
        content = markdown.markdown(fin.read())
        content = content.replace("<code>", "<code class='square'>")
        # Markup to escape html characters
        return render_template("instructions.html", content=Markup(content))

@socketio.on("begin")
def begin(msg):
    if "username" in session:
        raise excpt.AlreadyLoggedIn()
    elif msg["username"] in m.players:
        raise excpt.UsernameTaken(msg["username"])
    else:
        m.addPlayer(msg["username"])
        session["username"] = msg["username"]
        join_room(msg["username"])

        socketio.emit("acknowledged", {}, room=msg["username"])

    global running
    if running is None:
        running = gevent.spawn(run)

@socketio.on("disconnect")
def logoff():
    if "username" in session:
        uname = session["username"]
        m.arena[m.players[uname].pos] = " "
        del m.players[uname]

        global running
        if not m.players:
            running.kill()
            running = None

@socketio.on("move")
def move(direction):
    user = session["username"]
    m.players[user].queue("move", direction)

@socketio.on("turn")
def turn(direction):
    user = session["username"]
    m.players[user].queue("turn", direction)

@socketio.on("fire")
def fire():
    user = session["username"]
    m.players[user].queue("fire")

@socketio.on("bomb")
def bomb():
    user = session["username"]
    m.players[user].queue("bomb")

@socketio.on("scan")
def scan():
    user = session["username"]
    m.players[user].scan = not m.players[user].scan

@socketio.on("cloak")
def cloak():
    user = session["username"]
    m.players[user].cloak = not m.players[user].cloak

if __name__ == "__main__":
    socketio.run(app)
