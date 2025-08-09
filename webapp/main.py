from fastapi import FastAPI, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from . import database
from .database import ValueBet, Fixture

app = FastAPI()

templates = Jinja2Templates(directory="webapp/templates")

@app.get("/")
def read_root(request: Request, db: Session = Depends(database.get_db)):
    """
    Root endpoint for the web application.
    Fetches all value bets from the last 24 hours and renders them in an HTML template.
    """
    time_threshold = datetime.utcnow() - timedelta(days=1)

    recent_bets = (
        db.query(ValueBet)
        .join(Fixture)
        .filter(Fixture.date >= time_threshold)
        .order_by(Fixture.date.desc())
        .all()
    )

    return templates.TemplateResponse("index.html", {"request": request, "bets": recent_bets})
