from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.database import Base

class DebugSession(Base):
    __tablename__ = "debug_sessions"

    id = Column(Integer, primary_key=True, index=True)
    error = Column(String, index=True)
    language = Column(String, index=True)
    confidence = Column(Float)
    trace_id = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
