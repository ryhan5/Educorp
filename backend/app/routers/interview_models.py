from pydantic import BaseModel
from typing import List, Optional

class InterviewStartRequest(BaseModel):
    persona: str = "Technical Interviewer" # Technical, HR, Manager
    job_description: Optional[str] = ""
    resume_text: Optional[str] = ""

class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    response: str
    
class FeedbackResponse(BaseModel):
    score: int
    readiness_score: dict # Breakdown by round/skill
    strengths: List[str]
    weaknesses: List[str]
    summary: str

