from flask import Flask, render_template, url_for

import game

app = Flask(__name__)

@app.route("/")
def index():
    m = game.Arena()
    return render_template("play.html", arena=str(m))

if __name__ == "__main__":
    app.run(port = 8080, debug=True)
