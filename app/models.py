from sqlalchemy import Column, String, JSON, DateTime
from sqlalchemy.sql import func
from .database import Base

class Match(Base):
    __tablename__ = "matches"

    match_id = Column(String, primary_key=True, index=True)
    summoner_puuid = Column(String, primary_key=True, index=True)
    data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())