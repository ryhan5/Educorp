from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List
from app.services.learning_pack.agent import LearningPackAgent
from app.services.learning_pack.models import LearningPackResponse, QuizSubmission, QuizFeedback, QuizQuestion

router = APIRouter(prefix="/learning-pack", tags=["LearningPack"])
agent = LearningPackAgent()

# In-memory store for active quizzes (Hackathon simplicity)
# In production, use DynamoDB (SK=QUIZ#{id})
active_quizzes: Dict[str, List[QuizQuestion]] = {}

@router.post("/generate", response_model=LearningPackResponse)
async def generate_pack(
    skill_name: str = Body(..., embed=True),
    context: Dict[str, Any] = Body({}, embed=True)
):
    """
    Triggers the Agentic Workflow: Notes -> Quiz -> Flashcards
    """
    try:
        pack = await agent.generate_pack(skill_name, context)
        
        # Cache quiz for grading
        # Using skill_name as makeshift ID for this session
        active_quizzes[skill_name] = pack.quiz
        
        return pack
    except Exception as e:
        print(f"Error generating pack: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/evaluate", response_model=QuizFeedback)
async def evaluate_quiz(
    skill_name: str = Body(..., embed=True),
    submission: QuizSubmission = Body(...)
):
    """
    Evaluates quiz and returns AI feedback.
    """
    quiz = active_quizzes.get(skill_name)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz session not found/expired.")
        
    feedback = await agent.evaluate_quiz(submission, quiz)
    return feedback
