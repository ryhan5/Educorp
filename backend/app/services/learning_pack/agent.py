import json
import re
from typing import List, Dict, Any
from app.services.bedrock import invoke_nova_pro
from app.services.learning_pack.models import (
    LearningNote, QuizQuestion, Flashcard, LearningPackResponse, 
    QuizFeedback, QuizSubmission
)

def _parse_json_from_text(text: str):
    """
    Robust JSON parser that handles markdown code blocks.
    """
    try:
        # Remove markdown fences
        cleaned = re.sub(r'^```(?:json)?', '', text.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r'```$', '', cleaned.strip(), flags=re.MULTILINE)
        
        # Find JSON array or object
        if '[' in cleaned:
            start = cleaned.find('[')
            end = cleaned.rfind(']') + 1
        else:
            start = cleaned.find('{')
            end = cleaned.rfind('}') + 1
        
        if start == -1 or end == 0:
            print(f"No JSON found in: {text[:200]}")
            return None
        
        json_str = cleaned[start:end]
        return json.loads(json_str)
    except Exception as e:
        print(f"JSON Parse Error: {e}")
        return None


class LearningPackAgent:
    """
    Orchestrates the creation of a Smart Learning Pack:
    Context -> Notes -> Quiz -> Flashcards
    Uses direct Amazon Bedrock Nova Pro invocation.
    """

    async def generate_pack(self, skill_name: str, context: Dict[str, Any]) -> LearningPackResponse:
        print(f"--- Agent Generating Learning Pack for: {skill_name} ---")
        
        # Step 1: Generate Notes (Nova Pro)
        notes = await self._generate_notes(skill_name, context)
        
        # Step 2: Generate Quiz (Nova Pro)
        quiz = await self._generate_quiz(skill_name, notes)
        
        # Step 3: Generate Flashcards (Nova Pro)
        flashcards = await self._generate_flashcards(skill_name, notes)
        
        return LearningPackResponse(
            skill_name=skill_name,
            notes=notes or [],
            quiz=quiz or [],
            flashcards=flashcards or []
        )

    async def _generate_notes(self, skill: str, context: Dict) -> List[LearningNote]:
        level = "Beginner"
        if context.get("confidence", 0) > 40: level = "Intermediate"
        if context.get("confidence", 0) > 75: level = "Advanced"

        system_prompt = f"""You are an Expert AI Tutor.
Create CONCISE, STRUCTURED study notes for the skill '{skill}'.
Target Level: {level}.

Output a JSON ARRAY of objects with this exact structure:
[
  {{"title": "Concept Title", "content": "Explanation with bullet points and examples."}}
]

Generate 3-4 key concepts. Output ONLY valid JSON, no markdown."""

        user_prompt = f"Generate study notes for: {skill}"
        
        response = invoke_nova_pro(system_prompt, user_prompt)
        print(f"Notes Response: {response[:200]}...")
        
        data = _parse_json_from_text(response)
        if data and isinstance(data, list):
            return [LearningNote(**n) for n in data]
        return []

    async def _generate_quiz(self, skill: str, notes: List[LearningNote]) -> List[QuizQuestion]:
        notes_text = "\n".join([f"- {n.title}: {n.content}" for n in notes])
        
        system_prompt = f"""You are an Assessment Designer.
Create a 3-question mini-quiz based on these notes about '{skill}'.

Output a JSON ARRAY with this exact structure:
[
  {{
    "id": "q1",
    "question": "What is...?",
    "options": [
      {{"label": "A", "text": "Option A text"}},
      {{"label": "B", "text": "Option B text"}},
      {{"label": "C", "text": "Option C text"}},
      {{"label": "D", "text": "Option D text"}}
    ],
    "correctAnswer": "A"
  }}
]

Output ONLY valid JSON, no markdown."""

        user_prompt = f"Notes:\n{notes_text}\n\nGenerate quiz questions."
        
        response = invoke_nova_pro(system_prompt, user_prompt)
        print(f"Quiz Response: {response[:200]}...")
        
        data = _parse_json_from_text(response)
        if data and isinstance(data, list):
            return [QuizQuestion(**q) for q in data]
        return []

    async def _generate_flashcards(self, skill: str, notes: List[LearningNote]) -> List[Flashcard]:
        notes_text = "\n".join([f"- {n.title}: {n.content}" for n in notes])

        system_prompt = f"""You are a Revision Assistant.
Create 5 flashcards for rapid review of '{skill}'.

Output a JSON ARRAY with this exact structure:
[
  {{"front": "Question or Concept", "back": "Answer or Definition"}}
]

Output ONLY valid JSON, no markdown."""

        user_prompt = f"Source Material:\n{notes_text}\n\nGenerate flashcards."
        
        response = invoke_nova_pro(system_prompt, user_prompt)
        print(f"Flashcards Response: {response[:200]}...")
        
        data = _parse_json_from_text(response)
        if data and isinstance(data, list):
            return [Flashcard(**f) for f in data]
        return []

    async def evaluate_quiz(self, submission: QuizSubmission, original_quiz: List[QuizQuestion]) -> QuizFeedback:
        """
        Grades the quiz and provides agentic feedback.
        """
        correct_count = 0
        total = len(original_quiz)
        
        for q in original_quiz:
            user_ans = submission.answers.get(q.id)
            if user_ans and user_ans.upper() == q.correctAnswer.upper():
                correct_count += 1
        
        # Generate AI feedback
        system_prompt = f"""You are a Mentor.
The student scored {correct_count}/{total} on a quiz.
Provide brief, constructive feedback and 1 specific recommendation.

Output JSON with this structure:
{{"feedback": "Your encouraging message", "recommendation": "Specific next step"}}

Output ONLY valid JSON."""

        response = invoke_nova_pro(system_prompt, "Generate feedback.")
        
        data = _parse_json_from_text(response)
        
        if data and isinstance(data, dict):
            return QuizFeedback(
                score=correct_count, 
                total=total, 
                feedback=data.get("feedback", "Good effort!"),
                recommendation=data.get("recommendation", "Review the notes.")
            )
            
        return QuizFeedback(score=correct_count, total=total, feedback="Good effort!", recommendation="Review notes.")
