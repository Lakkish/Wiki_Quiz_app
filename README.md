# Wiki Quiz Generator

A full-stack web application that generates interactive quizzes from Wikipedia articles using AI (Groq LLM).

## Features

- 📚 **Generate Quiz from Wikipedia**: Enter any Wikipedia URL and get AI-generated quiz questions
- 🧠 **Smart AI Questions**: 7 questions with varying difficulty levels (easy, medium, hard)
- ✅ **Instant Answers**: See correct answers and explanations
- 📊 **Quiz History**: View all previously generated quizzes
- 💾 **Database Storage**: All quizzes are saved for future reference
- 🎨 **Beautiful UI**: Clean, modern interface with responsive design

## Tech Stack

### Backend

- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **Web Scraping**: BeautifulSoup4
- **AI/LLM**: Groq API (Llama 3.3 70B)
- **ORM**: SQLAlchemy

### Frontend

- **Framework**: React.js
- **HTTP Client**: Axios
- **Styling**: Custom CSS

## Prerequisites

- Python 3.8+
- Node.js 14+
- PostgreSQL 12+
- Groq API Key (free from https://console.groq.com/)

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd wiki_quiz_app
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create `backend/.env` file:

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/wikiquiz
GROQ_API_KEY=your_groq_api_key_here
```

**Get Groq API Key:**

1. Go to https://console.groq.com/
2. Sign up for free account
3. Create API key
4. Copy and paste into `.env`

### 4. Setup PostgreSQL Database

```bash
# Using psql
psql -U postgres

# Create database
CREATE DATABASE wikiquiz;
\q
```

### 5. Run Backend Server

```bash
cd backend
python main.py
```

Backend will run on: http://localhost:8000

### 6. Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will run on: http://localhost:3000

## API Endpoints

### POST `/api/generate-quiz`

Generate a quiz from Wikipedia URL

**Request:**

```json
{
  "url": "https://en.wikipedia.org/wiki/Python_(programming_language)"
}
```

**Response:**

```json
{
  "id": 1,
  "url": "https://en.wikipedia.org/wiki/Python_(programming_language)",
  "title": "Python (programming language)",
  "summary": "Python is a high-level programming language...",
  "sections": ["History", "Design philosophy", "Syntax"],
  "key_entities": {
    "people": ["Guido van Rossum"],
    "organizations": ["Python Software Foundation"],
    "locations": ["Netherlands"]
  },
  "quiz": [
    {
      "question": "Who created Python?",
      "options": [
        "Guido van Rossum",
        "James Gosling",
        "Bjarne Stroustrup",
        "Dennis Ritchie"
      ],
      "answer": "Guido van Rossum",
      "difficulty": "easy",
      "explanation": "Guido van Rossum created Python in 1991"
    }
  ],
  "related_topics": ["Programming", "Computer Science"],
  "created_at": "2025-01-11T10:30:00Z"
}
```

### GET `/api/quizzes`

Get all quiz history

**Response:**

```json
[
  {
    "id": 1,
    "url": "https://en.wikipedia.org/wiki/Python_(programming_language)",
    "title": "Python (programming language)",
    "created_at": "2025-01-11T10:30:00Z"
  }
]
```

### GET `/api/quizzes/{quiz_id}`

Get specific quiz by ID

**Response:** Same as POST `/api/generate-quiz`

## Usage

### Generating a Quiz

1. Navigate to http://localhost:3000
2. Enter a Wikipedia URL (e.g., `https://en.wikipedia.org/wiki/Artificial_intelligence`)
3. Click "Generate Quiz"
4. Wait for AI to generate questions (10-20 seconds)
5. View quiz with questions, options, and explanations

### Viewing Quiz History

1. Click "Quiz History" tab
2. See all previously generated quizzes
3. Click "View Details" to see full quiz in a modal

## Project Structure

```
wiki_quiz_app/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── scraper.py           # Wikipedia scraper
│   ├── quiz_service.py      # AI quiz generation
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Environment variables
├── frontend/
│   ├── src/
│   │   ├── App.js           # Main React component
│   │   ├── App.css          # Styles
│   │   └── api.js           # API calls
│   ├── public/
│   └── package.json         # Node dependencies
├── sample_data/             # Sample outputs
│   ├── urls.txt
│   └── sample_output_*.json
├── screenshots/             # Application screenshots
└── README.md
```

## Testing

### Test Wikipedia URLs

The application works with any Wikipedia article. Here are some tested examples:

- https://en.wikipedia.org/wiki/Python_(programming_language)
- https://en.wikipedia.org/wiki/Artificial_intelligence
- https://en.wikipedia.org/wiki/Albert_Einstein
- https://en.wikipedia.org/wiki/World_War_II
- https://en.wikipedia.org/wiki/Climate_change

### API Testing

Visit http://localhost:8000/docs for interactive API documentation (Swagger UI).

## Troubleshooting

### PostgreSQL Connection Issues

If you see database connection errors:

1. Verify PostgreSQL is running
2. Check database credentials in `.env`
3. Ensure `wikiquiz` database exists
4. URL encode special characters in password (e.g., `#` → `%23`, `@` → `%40`)

### Groq API Quota Exceeded

If you hit rate limits:

- Wait 60 seconds before trying again
- Groq free tier allows 30 requests/minute
- Consider upgrading to paid tier for higher limits

### CORS Errors

If you see CORS errors:

- Ensure backend is running on port 8000
- Ensure frontend is running on port 3000
- Check CORS middleware in `main.py`

## LLM Prompt Design

The quiz generation uses carefully crafted prompts to ensure quality:

### Quiz Generation Prompt

```
Based on the following Wikipedia article about "{topic}", generate {num_questions}
multiple-choice quiz questions.

Requirements:
1. Questions should test understanding, not just memorization
2. Each question must have exactly 4 options
3. Mix difficulty levels (easy, medium, hard)
4. correct_answer must exactly match one of the options
5. Keep explanations concise (1-2 sentences)
6. Return ONLY valid JSON array
```

### Prompt Engineering Techniques Used

- **Clear instructions**: Specific format requirements
- **Grounding**: Questions based on article content only
- **Structured output**: JSON format for easy parsing
- **Validation rules**: Exact match requirements for answers
- **Diversity**: Mix of difficulty levels

## Performance Optimization

- **Caching**: Duplicate URLs are not re-scraped
- **Content Truncation**: Only first 4000 characters sent to LLM
- **Efficient Scraping**: Removes unnecessary HTML elements
- **Database Indexing**: URL and ID fields indexed

## Future Enhancements

- [ ] Interactive quiz mode (hide answers until submission)
- [ ] User scoring and leaderboards
- [ ] Export quiz as PDF
- [ ] Multiple language support
- [ ] Custom question count selection
- [ ] Question difficulty filter
- [ ] Share quiz via link

## License

MIT License

## Author

Your Name

## Acknowledgments

- Wikipedia for content
- Groq for AI inference
- FastAPI for backend framework
- React for frontend framework
