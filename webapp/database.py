from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
import datetime

DATABASE_URL = "sqlite:///./bets.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Fixture(Base):
    __tablename__ = "fixtures"

    id = Column(Integer, primary_key=True, index=True) # This is the fixture ID from the API
    date = Column(DateTime, default=datetime.datetime.utcnow)
    home_team_name = Column(String, index=True)
    away_team_name = Column(String, index=True)
    league_name = Column(String, index=True)

    value_bets = relationship("ValueBet", back_populates="fixture")

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
    Base.metadata.create_all(bind=engine)

def get_db():
    """
    Dependency for FastAPI to get a DB session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
