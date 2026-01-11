import os
from typing import List, Dict
from groq import Groq
from dotenv import load_dotenv
import json

load_dotenv()

class QuizService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=api_key)
    
    def generate_quiz(self, topic: str, content: str, num_questions: int = 5) -> List[Dict]:
        """Generate quiz questions using Groq AI"""
        
        prompt = f"""Based on the following Wikipedia article about "{topic}", generate {num_questions} multiple-choice quiz questions.

Article Content:
{content[:4000]}

IMPORTANT: Return ONLY a valid JSON array. Do not include any markdown formatting, code blocks, or explanatory text.

Format:
[
  {{
    "question": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "Option A",
    "explanation": "Brief explanation of the correct answer"
  }}
]

Requirements:
1. Questions should test understanding, not just memorization
2. Each question must have exactly 4 options
3. Mix difficulty levels (easy, medium, hard)
4. correct_answer must exactly match one of the options
5. Keep explanations concise (1-2 sentences)
6. Return ONLY the JSON array, nothing else - no text before or after

Generate the questions now:"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Fast and accurate Groq model
                messages=[
                    {
                        "role": "system",
                        "content": "You are a quiz generator. Always respond with valid JSON only, no markdown or extra text."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000,
                top_p=1,
                stream=False
            )
            
            response_text = response.choices[0].message.content.strip()
            
            print(f"Raw AI Response (first 500 chars): {response_text[:500]}")
            
            # Clean the response - remove markdown code blocks if present
            if "```json" in response_text:
                # Extract content between ```json and ```
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                if end == -1:
                    end = len(response_text)
                response_text = response_text[start:end].strip()
            elif "```" in response_text:
                # Extract content between ``` and ```
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                if end == -1:
                    end = len(response_text)
                response_text = response_text[start:end].strip()
            
            # Remove any text before the first [
            if '[' in response_text:
                response_text = response_text[response_text.find('['):]
            
            # Remove any text after the last ]
            if ']' in response_text:
                response_text = response_text[:response_text.rfind(']') + 1]
            
            print(f"Cleaned Response (first 500 chars): {response_text[:500]}")
            
            # Parse JSON
            questions = json.loads(response_text)
            
            # Validate questions
            if not isinstance(questions, list) or len(questions) == 0:
                raise ValueError("Invalid questions format - not a list or empty")
            
            # Ensure each question has required fields
            for idx, q in enumerate(questions):
                if not all(k in q for k in ["question", "options", "correct_answer"]):
                    print(f"Question {idx} keys: {q.keys()}")
                    raise ValueError(f"Question {idx} missing required fields")
                if not isinstance(q["options"], list) or len(q["options"]) != 4:
                    raise ValueError(f"Question {idx} must have exactly 4 options, got {len(q.get('options', []))}")
                # Ensure correct_answer is in options
                if q["correct_answer"] not in q["options"]:
                    raise ValueError(f"Question {idx}: correct_answer '{q['correct_answer']}' not in options")
            
            print(f"Successfully generated {len(questions)} questions")
            return questions[:num_questions]
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Full response text: {response_text}")
            raise ValueError(f"Failed to parse AI response as JSON: {str(e)}")
        except Exception as e:
            print(f"Error generating quiz: {e}")
            raise ValueError(f"Failed to generate quiz: {str(e)}")
    
    @staticmethod
    def calculate_score(questions: List[Dict], user_answers: List[Dict]) -> Dict:
        """Calculate quiz score"""
        correct_count = 0
        results = []
        
        for i, answer in enumerate(user_answers):
            question = questions[answer["question_index"]]
            is_correct = answer["selected_answer"] == question["correct_answer"]
            
            if is_correct:
                correct_count += 1
            
            results.append({
                "question_index": i,
                "question": question["question"],
                "user_answer": answer["selected_answer"],
                "correct_answer": question["correct_answer"],
                "is_correct": is_correct,
                "explanation": question.get("explanation", "")
            })
        
        total = len(questions)
        score = (correct_count / total) * 100 if total > 0 else 0
        
        return {
            "score": round(score, 2),
            "correct_answers": correct_count,
            "total_questions": total,
            "results": results
        }