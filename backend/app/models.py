from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field

class LearningResource(BaseModel):
    title: str
    url: str
    type: str = "tutorial" # tutorial, video, documentation, course, task
    description: Optional[str] = None
    completed: bool = False
    difficulty: str = "medium" # beginner, medium, advanced

class MicroSkill(BaseModel):
    id: str
    name: str
    description: str
    resources: List[LearningResource] = []
    status: str = "pending" # pending, in-progress, mastered
    estimated_hours: int = 1

class CareerGoal(BaseModel):
    goal_name: str
    target_role: str
    readiness_score: int = Field(description="0-100 score indicating how close the learner is")
    missing_skills: List[str] = []
    reasoning: str

class LearningPath(BaseModel):
    user_id: str = "demo_user"
    goals: List[CareerGoal] = []
    daily_tasks: List[MicroSkill] = []
    
    # Legacy fields compatibility (optional, can be deprecated)
    skill_name: Optional[str] = None
    reasoning: Optional[str] = None
    resources: List[LearningResource] = []
    estimated_hours: int = 0
