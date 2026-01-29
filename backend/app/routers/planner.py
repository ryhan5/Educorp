from fastapi import APIRouter
from typing import List
from app.services.planner_agent import generate_learning_plan, generate_mindmap_plan, generate_interactive_widget
from app.models import LearningPath
# from app.database import db # Removed for Bedrock migration
from app.services.aws_store import aws_store
from pydantic import BaseModel

router = APIRouter()

class MindMapRequest(BaseModel):
    topic: str

@router.post("/generate-mindmap")
async def create_mindmap(request: MindMapRequest):
    data = await generate_mindmap_plan(request.topic)
    return data

@router.post("/generate-widget")
async def create_widget(request: MindMapRequest):
    data = await generate_interactive_widget(request.topic)
    return data

@router.post("/generate-plan", response_model=List[LearningPath])
async def create_plan():
    # Trigger the agent
    plans = await generate_learning_plan()
    return plans

@router.get("/learning-paths", response_model=List[LearningPath])
async def get_plans():
    # Fetch from DynamoDB
    raw_skills = await aws_store.get_user_graph(user_id="demo_user")
    
    # Convert DynamoDB items to LearningPath (Just a placeholder logic as learning paths are different)
    # For now, we return empty or implement actual logic if `learning_paths` were stored. 
    # Since we are storing SKILLS, we might want to generate plans based on those skills.
    
    # Returning empty for now to satisfy interface, pending new requirement
    return []
