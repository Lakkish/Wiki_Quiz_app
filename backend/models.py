from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from database import Base

class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    summary = Column(Text)
    content = Column(Text)
    sections = Column(JSON)
    key_entities = Column(JSON)
    quiz = Column(JSON)
    related_topics = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    class Config:
        orm_mode = True