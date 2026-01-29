import json
from typing import List, Optional
from app.database import db
from app.models import LearningPath, LearningResource
from pydantic import BaseModel
from app.services.bedrock import invoke_nova_pro, invoke_nova_lite

# Models
class MindMapNode(BaseModel):
    id: str
    label: str
    type: str # 'root', 'concept', 'resource'
    url: Optional[str] = None

class MindMapEdge(BaseModel):
    id: str
    source: str
    target: str

class MindMapData(BaseModel):
    nodes: List[MindMapNode]
    edges: List[MindMapEdge]

class WidgetResponse(BaseModel):
    name: str
    html_content: str
    description: str

def _parse_planner_json(text: str, model_class):
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != -1:
            json_str = text[start:end]
            data = json.loads(json_str)
            return model_class(**data)
        return None
    except Exception as e:
        print(f"JSON Parse Error: {e}")
        return None

async def generate_mindmap_plan(topic: str) -> MindMapData:
    system_prompt = """You are an AI Curriculum Agent. Create a detailed learning mindmap.
Structure: Root -> Concepts -> Resources.
Output strictly JSON:
{
    "nodes": [{"id": "str", "label": "str", "type": "root|concept|resource", "url": "opt_str"}],
    "edges": [{"id": "str", "source": "str", "target": "str"}]
}"""
    user_prompt = f"Topic: {topic}"
    
    response = invoke_nova_pro(system_prompt, user_prompt)
    if "Error" in response:
        print(f"Bedrock Error: {response}")
        # Return fallback
        return MindMapData(
            nodes=[MindMapNode(id="1", label=f"Error: {topic}", type="root")],
            edges=[]
        )

    data = _parse_planner_json(response, MindMapData)
    if not data:
        return MindMapData(
            nodes=[MindMapNode(id="1", label=f"Plan: {topic}", type="root")],
            edges=[]
        )
    return data

async def generate_interactive_widget(topic: str) -> WidgetResponse:
    print(f"DEBUG: Generating widget for {topic}")
    
    system_prompt = """You are a Visualization Expert. Create a DEEP, ENGAGING INTERACTIVE WIDGET.
Strategies:
1. Algorithms: Animated Bar Charts.
2. Data Structures: SVG Nodes.
3. Systems: Flow Diagrams.

REQUIREMENTS:
- name: Title
- html_content: COMPLETE HTML/JS with TailwindCSS. NO EXTERNAL JS FILES.
- description: Summary.
Output strictly JSON."""
    
    user_prompt = f"Topic: {topic}"
    
    response = invoke_nova_lite(f"{system_prompt}\n\n{user_prompt}")
    
    data = _parse_planner_json(response, WidgetResponse)
    
    if not data:
        return WidgetResponse(
            name="Generation Failed",
            html_content="<div class='p-4 text-red-500'>Failed to generate widget.</div>",
            description="Error."
        )
    return data

async def generate_learning_plan() -> List[LearningPath]:
    # 1. Fetch skills from DB
    skills_cursor = db.skill_nodes.find({})
    skills = await skills_cursor.to_list(length=100)
    
    if not skills:
        return []

    weak_skills = [s for s in skills if s.get("confidence_score", 0) < 70]
    if not weak_skills:
        weak_skills = [{"skill_name": "Advanced Architecture", "confidence_score": 50}]

    plans = []

    for skill in weak_skills:
        skill_name = skill["skill_name"]
        confidence = skill["confidence_score"]
        
        system_prompt = """You are an Agentic Learning Planner.
CORE RESPONSIBILITIES:
1. DEFINE CAREER GOALS.
2. BREAK DOWN SKILLS.
3. ASSIGN TASKS.

Output strictly JSON:
{
    "skill_name": "str",
    "reasoning": "str",
    "resources": [{"title": "str", "url": "str", "type": "video|article|task"}],
    "estimated_hours": int
}"""
        user_prompt = f"Skill: {skill_name}\nConfidence: {confidence}"
        
        response = invoke_nova_pro(system_prompt, user_prompt)
        
        # Manually parse since LearningPath logic might check DB insertion
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1:
                data = json.loads(response[start:end])
                plan = LearningPath(**data)
                plans.append(plan)
                await db.learning_paths.insert_one(plan.dict())
        except Exception as e:
            print(f"Plan Generation Error for {skill_name}: {e}")
            
    return plans
