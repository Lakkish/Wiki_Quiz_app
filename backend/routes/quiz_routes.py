from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
import schemas
from database import get_db
from services.wikipedia_services import WikipediaService
from services.quiz_services import QuizService

router = APIRouter(prefix="/api/quiz", tags=["quiz"])

wiki_service = WikipediaService()
quiz_service = QuizService()

@router.post("/generate", response_model=schemas.QuizResponse)
async def generate_quiz(quiz_data: schemas.QuizCreate, db: Session = Depends(get_db)):
    """Generate a new quiz from Wikipedia topic"""
    
    # Fetch Wikipedia content
    article = wiki_service.fetch_article_content(quiz_data.topic)
    if not article:
        raise HTTPException(status_code=404, detail=f"Wikipedia article not found for topic: {quiz_data.topic}")
    
    # Generate quiz questions
    try:
        questions = quiz_service.generate_quiz(
            topic=article["title"],
            content=article["content"],
            num_questions=5
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")
    
    # Save to database
    db_quiz = models.Quiz(
        topic=article["title"],
        wikipedia_url=article["url"],
        questions=questions
    )
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    
    return db_quiz

@router.get("/{quiz_id}", response_model=schemas.QuizResponse)
async def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    """Get a quiz by ID"""
    quiz = db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

@router.post("/submit", response_model=schemas.QuizResult)
async def submit_quiz(submission: schemas.QuizSubmit, db: Session = Depends(get_db)):
    """Submit quiz answers and get results"""
    
    # Get quiz
    quiz = db.query(models.Quiz).filter(models.Quiz.id == submission.quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Calculate score
    user_answers = [{"question_index": ans.question_index, "selected_answer": ans.selected_answer} 
                    for ans in submission.answers]
    
    result = quiz_service.calculate_score(quiz.questions, user_answers)
    
    # Save attempt
    attempt = models.QuizAttempt(
        quiz_id=submission.quiz_id,
        user_name=submission.user_name,
        score=result["score"],
        total_questions=result["total_questions"],
        answers=result["results"]
    )
    db.add(attempt)
    db.commit()
    
    return {
        "quiz_id": submission.quiz_id,
        "score": result["score"],
        "total_questions": result["total_questions"],
        "correct_answers": result["correct_answers"],
        "answers": result["results"]
    }

@router.get("/leaderboard/top", response_model=List[schemas.LeaderboardEntry])
async def get_leaderboard(limit: int = 10, db: Session = Depends(get_db)):
    """Get top quiz scores"""
    
    attempts = db.query(models.QuizAttempt, models.Quiz)\
        .join(models.Quiz)\
        .filter(models.QuizAttempt.user_name.isnot(None))\
        .order_by(models.QuizAttempt.score.desc())\
        .limit(limit)\
        .all()
    
    leaderboard = [
        {
            "user_name": attempt.user_name,
            "score": attempt.score,
            "topic": quiz.topic,
            "completed_at": attempt.completed_at
        }
        for attempt, quiz in attempts
    ]
    
    return leaderboard

@router.get("/history/recent", response_model=List[schemas.QuizResponse])
async def get_recent_quizzes(limit: int = 10, db: Session = Depends(get_db)):
    """Get recently created quizzes"""
    
    quizzes = db.query(models.Quiz)\
        .order_by(models.Quiz.created_at.desc())\
        .limit(limit)\
        .all()
    
    return quizzes