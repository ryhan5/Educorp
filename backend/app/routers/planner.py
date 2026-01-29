from fastapi import APIRouter
from typing import List
from app.services.planner_agent import generate_learning_plan, generate_mindmap_plan, generate_interactive_widget
from app.models import LearningPath
from app.database import db
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
    cursor = db.learning_paths.find({})
    plans = await cursor.to_list(length=100)
    return plans
