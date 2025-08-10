import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from decouple import config
import datetime

# Get the database URL from environment variables, provided by GitHub Secrets
DATABASE_URL = config("DATABASE_URL", default=None)

if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    # This is a fallback for local testing without a DB, though the script will fail on API key.
    # A better local setup would use a local Postgres or SQLite DB.
    print("WARNING: DATABASE_URL not found. Using in-memory SQLite database.")
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Fixture(Base):
    __tablename__ = "fixtures"

    id = Column(Integer, primary_key=True, index=True) # Fixture ID from API
    date = Column(DateTime, default=datetime.datetime.utcnow)
    home_team_name = Column(String, index=True)
    away_team_name = Column(String, index=True)
    league_name = Column(String, index=True)

    value_bets = relationship("ValueBet", back_populates="fixture", cascade="all, delete-orphan")

class ValueBet(Base):
    __tablename__ = "value_bets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fixture_id = Column(Integer, ForeignKey("fixtures.id"))
    market = Column(String)
    bet_value = Column(String) # e.g., 'Home', 'Over', 'Yes'
    probability = Column(Float)
    odds = Column(Float)
    value = Column(Float) # The result of prob * odds

    fixture = relationship("Fixture", back_populates="value_bets")

def init_db():
    """
    Initializes the database and creates tables if they don't exist.
    """
    if not engine:
        raise Exception("Database engine not initialized. DATABASE_URL may be missing.")
    Base.metadata.create_all(bind=engine)
