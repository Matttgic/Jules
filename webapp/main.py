from flask import Flask, render_template, g
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from . import database
from .database import ValueBet, Fixture, SessionLocal

app = Flask(__name__)

# Database session management
@app.before_request
def before_request():
    """Opens a new database connection for each request."""
    g.db = SessionLocal()

@app.teardown_request
def teardown_request(exception):
    """Closes the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route("/")
def index():
    """
    Root endpoint for the web application.
    Fetches all value bets from the last 24 hours and renders them in an HTML template.
    """
    db: Session = g.db
    time_threshold = datetime.utcnow() - timedelta(days=1)

    recent_bets = (
        db.query(ValueBet)
        .join(Fixture)
        .filter(Fixture.date >= time_threshold)
        .order_by(Fixture.date.desc())
        .all()
    )

    return render_template("index.html", bets=recent_bets)
