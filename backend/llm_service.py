from groq import Groq
import json
import os
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
    def generate_quiz(self, title: str, content: str, sections: list) -> dict:
        """Generate quiz from article content using Groq"""
        
        prompt = f"""You are a quiz generator. Based on the Wikipedia article about "{title}", generate a quiz.

Article content:
{content[:4000]}

Sections available: {', '.join(sections[:5])}

Generate EXACTLY 7 quiz questions with the following requirements:
1. Questions should be factual and based ONLY on the article content
2. Mix of difficulty levels (2 easy, 3 medium, 2 hard)
3. Each question must have exactly 4 options (A, B, C, D)
4. One correct answer
5. Brief explanation referencing the article

Also suggest 5 related Wikipedia topics for further reading.

Return ONLY valid JSON in this exact format (no markdown, no extra text):
{{
  "quiz": [
    {{
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "Option B",
      "difficulty": "easy",
      "explanation": "Brief explanation from article"
    }}
  ],
  "related_topics": ["Topic 1", "Topic 2", "Topic 3", "Topic 4", "Topic 5"]
}}"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean JSON
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            
            result = json.loads(result_text.strip())
            return result
            
        except Exception as e:
            print(f"LLM Error: {e}")
            raise Exception(f"Failed to generate quiz: {str(e)}")