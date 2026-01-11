from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import engine, get_db
from scraper import WikipediaScraper
from services.quiz_services import QuizService
import os
import json
PORT = int(os.getenv("PORT", 8000))
origins = [
    "http://localhost:3000",
    "https://wiki-quiz-app-frontend.onrender.com",  # Update this after deploying frontend
]

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Wiki Quiz API")



# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Change from ["*"] to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

quiz_service = QuizService()

@app.get("/")
def read_root():
    return {"message": "Wiki Quiz API is running!"}

@app.post("/api/generate-quiz", response_model=schemas.ArticleResponse)
async def generate_quiz(url_input: schemas.URLInput, db: Session = Depends(get_db)):
    """Generate quiz from Wikipedia URL"""
    try:
        url = str(url_input.url)
        
        # Check if URL already exists (caching)
        existing = db.query(models.Article).filter(models.Article.url == url).first()
        if existing:
            return existing
        
        # Scrape Wikipedia
        scraper = WikipediaScraper(url)
        scraped_data = scraper.scrape()
        
        # Generate quiz using AI
        quiz_questions = quiz_service.generate_quiz(
            topic=scraped_data['title'],
            content=scraped_data['content'],
            num_questions=7
        )
        
        # Format quiz with difficulty levels
        formatted_quiz = []
        difficulty_levels = ['easy', 'easy', 'medium', 'medium', 'medium', 'hard', 'hard']
        
        for idx, q in enumerate(quiz_questions):
            formatted_quiz.append({
                'question': q['question'],
                'options': q['options'],
                'answer': q['correct_answer'],
                'difficulty': difficulty_levels[idx] if idx < len(difficulty_levels) else 'medium',
                'explanation': q.get('explanation', 'No explanation provided')
            })
        
        # Generate related topics (simple implementation)
        related_topics = [
            scraped_data['title'] + " history",
            "Computer Science",
            "Mathematics",
            "Technology",
            "Innovation"
        ]
        
        # Save to database
        article = models.Article(
            url=url,
            title=scraped_data['title'],
            summary=scraped_data['summary'],
            content=scraped_data['content'],
            sections=scraped_data['sections'],
            key_entities=scraped_data['key_entities'],
            quiz=formatted_quiz,
            related_topics=related_topics
        )
        
        db.add(article)
        db.commit()
        db.refresh(article)
        
        return article
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate quiz: {str(e)}")

@app.get("/api/quizzes", response_model=List[schemas.ArticleListItem])
async def get_all_quizzes(db: Session = Depends(get_db)):
    """Get all quizzes from history"""
    quizzes = db.query(models.Article).order_by(models.Article.created_at.desc()).all()
    return quizzes

@app.get("/api/quizzes/{quiz_id}", response_model=schemas.ArticleResponse)
async def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    """Get specific quiz by ID"""
    quiz = db.query(models.Article).filter(models.Article.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

@app.delete("/api/quizzes/{quiz_id}")
async def delete_quiz(quiz_id: int, db: Session = Depends(get_db)):
    """Delete a quiz"""
    quiz = db.query(models.Article).filter(models.Article.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    db.delete(quiz)
    db.commit()
    return {"message": "Quiz deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT) 