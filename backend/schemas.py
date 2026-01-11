from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Optional
from datetime import datetime

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    answer: str
    difficulty: str
    explanation: str

class KeyEntities(BaseModel):
    people: List[str] = []
    organizations: List[str] = []
    locations: List[str] = []

class ArticleResponse(BaseModel):
    id: int
    url: str
    title: str
    summary: str
    key_entities: Dict
    sections: List[str]
    quiz: List[Dict]
    related_topics: List[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class URLInput(BaseModel):
    url: HttpUrl

class ArticleListItem(BaseModel):
    id: int
    url: str
    title: str
    created_at: datetime
    
    class Config:
        from_attributes = True