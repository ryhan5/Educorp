from typing import List, Optional
from pydantic import BaseModel, HttpUrl

class LearningResource(BaseModel):
    title: str
    url: str
    type: str = "tutorial" # tutorial, video, documentation, course
    description: Optional[str] = None
    completed: bool = False

class LearningPath(BaseModel):
    skill_name: str
    reasoning: str # Why this path was suggested (e.g., "Low confidence in React")
    resources: List[LearningResource]
    estimated_hours: int = 0
