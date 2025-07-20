from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AIInteraction(Base):
    __tablename__ = 'ai_interactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    query = Column(String)
    response = Column(JSON)
    feedback_score = Column(Integer)
    created_at = Column(DateTime)
    
    # For continuous learning