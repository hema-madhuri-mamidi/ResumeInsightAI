from __future__ import annotations

from flask import Flask, render_template

from v2.config import Config
from v2.routes import bp as api_bp

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config.from_object(Config)
app.register_blueprint(api_bp)


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/result")
def result() -> str:
    return render_template("result.html", parsed_data={})


if __name__ == "__main__":
    app.run(debug=True)
