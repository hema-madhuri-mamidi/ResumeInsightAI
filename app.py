from __future__ import annotations

from flask import Flask, render_template
import os

from v2.config import Config
from database import db
from v2.routes import bp as api_bp

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config.from_object(Config)

# Configure SQLAlchemy URI & Track modifications (handling Render/Heroku engine URI mappings)
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "sqlite:///resumeinsightai.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
db.init_app(app)

# Auto-create tables in app context
with app.app_context():
    db.create_all()

app.register_blueprint(api_bp)


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/result")
def result() -> str:
    return render_template("result.html", parsed_data={})


if __name__ == "__main__":
    app.run(debug=True)
