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

import re

def _parse_planner_json(text: str, model_class):
    """
    Robust JSON parser that handles:
    1. Markdown code blocks (```json ... ```)
    2. Newlines inside JSON string values (common in html_content)
    3. Raw JSON text
    """
    try:
        # Step 1: Remove markdown code fences if present
        # Handle ```json or just ```
        cleaned = re.sub(r'^```(?:json)?', '', text.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r'```$', '', cleaned.strip(), flags=re.MULTILINE)
        
        # Step 2: Find the JSON object boundaries
        start = cleaned.find('{')
        end = cleaned.rfind('}')
        
        if start == -1 or end == -1:
            print(f"No JSON object found in text: {text[:200]}")
            return None
        
        json_str = cleaned[start:end+1]
        
        # Step 3: Parse JSON
        data = json.loads(json_str)
        return model_class(**data)
        
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print(f"Problematic JSON: {json_str[:300]}...")
        return None
    except Exception as e:
        print(f"Parse Error: {e} | Text preview: {text[:100]}...")
        return None

async def generate_mindmap_plan(topic: str) -> MindMapData:
    system_prompt = """You are an AI Curriculum Agent. Create a detailed learning mindmap.
Structure: Root -> Concepts -> Resources.
Output ONLY raw JSON. Do not use markdown fencing (```json). Do not add preamble.
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
- html_content: COMPLETE HTML/JS. 
    1. MUST use a container <div id='visualization' style='height: 400px; width: 100%;'></div>.
    2. MUST include scripts to render immediately on load.
    3. Use inline TailwindCSS.
- description: Summary.
Output strictly JSON."""
    
    user_prompt = f"Topic: {topic}\n\nGenerate the widget JSON."
    
    # Use Nova Pro for better coding capability and reliability
    response = invoke_nova_pro(system_prompt, user_prompt)
    
    # Try parsing (Regex logic inside handles markdown blocks)
    data = _parse_planner_json(response, WidgetResponse)
    
    if not data:
        print(f"Widget Generation Failed. Raw Response: {response}")

        return WidgetResponse(
            name="Generation Failed",
            html_content=f"<div class='p-4 text-red-500'>Failed to generate widget.</div>",
            description="Error."
        )
    return data

async def generate_learning_plan() -> List[LearningPath]:
    """
    New Agentic Workflow using the Orchestrator.
    """
    from app.services.planner.orchestrator import AgenticOrchestrator
    
    orchestrator = AgenticOrchestrator(user_id="demo_user")
    plans = await orchestrator.generate_plan()
    
    return plans
