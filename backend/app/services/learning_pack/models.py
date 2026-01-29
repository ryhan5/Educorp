from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class LearningNote(BaseModel):
    title: str = Field(description="Concept title")
    content: str = Field(description="Concise, structured explanation with bullet points or examples.")
    difficulty: Optional[str] = Field(default="intermediate", description="beginner, intermediate, or advanced")

class QuizOption(BaseModel):
    text: str
    label: str # e.g., "A", "B", "C", "D"

class QuizQuestion(BaseModel):
    id: str
    question: str
    options: List[QuizOption]
    correctAnswer: str = Field(description="Label of the correct option (e.g., 'A')")
    explanation: Optional[str] = Field(default="", description="Explanation of the answer")

class Flashcard(BaseModel):
    front: str = Field(description="Concept or Question")
    back: str = Field(description="Definition or Answer")

class LearningPackResponse(BaseModel):
    skill_name: str
    notes: List[LearningNote]
    quiz: List[QuizQuestion]
    flashcards: List[Flashcard]

class QuizSubmission(BaseModel):
    pack_id: Optional[str] = None
    answers: Dict[str, str] = Field(description="Map of question_id -> selected_option_label")

class QuizFeedback(BaseModel):
    score: int
    total: int
    feedback: str = Field(description="Overall strengths and weaknesses")
    recommendation: str = Field(description="Next steps based on score")
