import gevent
import markdown
from flask import Flask, render_template, session
from flask import Markup
from flask.ext.socketio import SocketIO, join_room, emit, close_room

from game import Game
import custom_exceptions as excpt

app = Flask(__name__)
app.secret_key = "It's a secret!"
app.debug = True
socketio = SocketIO(app)


@socketio.on_error_default
def exception_handler(value):
    if isinstance(value, excpt.UserError):
        emit("python_error", str(value))
    else:
        raise

game = Game()
running = None
def run(interval=0.025):
    while True:
        gevent.sleep(interval)
        game.update()

        emit = socketio.emit
        scores = game.to_json()
        jobs = [gevent.spawn(emit, "update",
                             {"player": player.to_json(), "scores": scores},
                             room=uname)
                for uname, player in game.players.iteritems()]
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
    elif msg["username"] in game.players:
        raise excpt.UsernameTaken(msg["username"])
    else:
        game.addPlayer(msg["username"])
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
        game.arena[game.players[uname].pos] = " "
        del game.players[uname]
        close_room(uname)

        global running
        if not game.players:
            running.kill()
            running = None


@socketio.on("move")
def move(direction):
    user = session["username"]
    game.players[user].queue("move", direction)


@socketio.on("turn")
def turn(direction):
    user = session["username"]
    game.players[user].queue("turn", direction)


@socketio.on("fire")
def fire():
    user = session["username"]
    game.players[user].queue("fire")


@socketio.on("bomb")
def bomb():
    user = session["username"]
    game.players[user].queue("bomb")


@socketio.on("scan")
def scan():
    user = session["username"]
    game.players[user].scan = not game.players[user].scan


@socketio.on("cloak")
def cloak():
    user = session["username"]
    game.players[user].cloak = not game.players[user].cloak

if __name__ == "__main__":
    socketio.run(app)
