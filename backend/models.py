from sqlalchemy import Column, Integer,Text, String, DateTime, JSON, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
from sqlalchemy.sql import func

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

class Quiz(Base):
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, index=True)
    wikipedia_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    questions = Column(JSON)  # Store questions as JSON
    
    # Relationship
    attempts = relationship("QuizAttempt", back_populates="quiz")

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    user_name = Column(String, nullable=True)
    score = Column(Float)
    total_questions = Column(Integer)
    answers = Column(JSON)  # Store user answers
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    quiz = relationship("Quiz", back_populates="attempts")