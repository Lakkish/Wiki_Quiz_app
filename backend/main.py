from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Wiki Quiz API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Wiki Quiz API is running!"}

@app.post("/api/generate-quiz", response_model=schemas.ArticleResponse)
async def generate_quiz(url_input: schemas.URLInput, db: Session = Depends(get_db)):
    # We'll implement this in Phase 2 & 3
    pass

@app.get("/api/quizzes", response_model=List[schemas.ArticleListItem])
async def get_all_quizzes(db: Session = Depends(get_db)):
    # We'll implement this in Phase 4
    pass

@app.get("/api/quizzes/{quiz_id}", response_model=schemas.ArticleResponse)
async def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    # We'll implement this in Phase 4
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)