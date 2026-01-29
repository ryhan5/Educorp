from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
# from app.database import db # Removed for Bedrock migration
from app.services.aws_store import aws_store
from app.services.skill_extractor import extract_skills_from_text
from app.services.file_parser import parse_file_content
from app.services.github_extractor import fetch_github_summary
import math

router = APIRouter()

@router.post("/analyze-profile")
async def analyze_profile(
    text: Optional[str] = Form(None),
    github_url: Optional[str] = Form(None),
    course_history: Optional[str] = Form(None),
    assessments: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    content = ""
    
    if text:
        content += f"Resume/Bio Text: {text}\n"
    
    if file:
        file_content = await file.read()
        parsed_text = await parse_file_content(file_content, file.filename)
        content += f"Uploaded Resume ({file.filename}):\n{parsed_text}\n"

    if github_url:
         # Fetch real data
         gh_summary = await fetch_github_summary(github_url)
         content += f"\n{gh_summary}\n"
    
    if course_history:
        content += f"Course History: {course_history}\n"

    if assessments:
        content += f"Assessment Results: {assessments}\n"

    if not content.strip():
        raise HTTPException(status_code=400, detail="No content provided for analysis. Please provide text, URL, or upload a file.")

    # Extract skills using LLM
    extracted_skills = await extract_skills_from_text(content)
    
    if not extracted_skills:
        raise HTTPException(status_code=400, detail="Could not extract skills from the provided content.")

    # await db.skill_nodes.delete_many({}) # Removed DB Logic 
    # Continuous Update: DO NOT clear the graph. We want to Upsert/Merge.
    # await aws_store.delete_user_graph(user_id="demo_user") # REMOVED for Digital Twin persistence
    
    nodes = []
    edges = []
    
    # Track existing nodes to avoid duplicates and help parent linking
    existing_node_ids = set()

    # Create Root Node
    root_id = "root"
    nodes.append({
        "id": root_id,
        "data": {"label": "My Skills", "type": "root"},
        "position": {"x": 0, "y": 0},
        "type": "input", # standard ReactFlow input type
        "style": {
            "background": "#0a0a0a",
            "color": "white",
            "width": 100,
            "height": 50,
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center",
            "borderRadius": "8px",
            "fontWeight": "bold"
        }
    })
    existing_node_ids.add(root_id)

    # First pass: Create nodes for all skills and identify parents
    parent_map = {} # parent_name -> [child_skill_objects]
    
    categories = {} # name -> id

    # Organize skills by parent
    for skill in extracted_skills:
        p = skill.get("parent_skill") or "General"
        if p not in parent_map:
            parent_map[p] = []
        parent_map[p].append(skill)

    # Layout params
    category_radius = 250
    skill_radius = 150 

    cat_count = len(parent_map)
    
    for i, (category, skills) in enumerate(parent_map.items()):
        # Create Category Node
        cat_id = f"cat-{i}"
        cat_angle = (2 * math.pi / cat_count) * i
        cat_x = category_radius * math.cos(cat_angle)
        cat_y = category_radius * math.sin(cat_angle)

        nodes.append({
            "id": cat_id,
            "data": {"label": category, "type": "category"},
            "position": {"x": cat_x, "y": cat_y},
            "style": {
                "background": "#f5f5f5",
                "border": "1px solid #e5e5e5",
                "color": "#333",
                "width": 120,
                "padding": "10px",
                "borderRadius": "8px",
                "textAlign": "center",
                "fontWeight": "600"
            }
        })
        
        # Link Category to Root
        edges.append({
            "id": f"e-root-{cat_id}",
            "source": root_id,
            "target": cat_id,
            "style": {"stroke": "#0a0a0a", "strokeWidth": 2}
        })

        # Create Skill Nodes around the Category
        for j, skill in enumerate(skills):
            skill_id = f"skill-{i}-{j}"
            
            # Fan out skills around category
            skill_angle = cat_angle + (j - len(skills)/2 + 0.5) * 0.5 
            
            skill_dist = 180 # distance from category
            skill_x = cat_x + skill_dist * math.cos(skill_angle)
            skill_y = cat_y + skill_dist * math.sin(skill_angle)

            nodes.append({
                "id": skill_id,
                "data": {
                    "label": skill["skill_name"],
                    "confidence": skill["confidence_score"],
                    "depth": skill["depth_score"],
                    "relevance": skill.get("industry_relevance", 50),
                    "type": "skill"
                },
                "position": {"x": skill_x, "y": skill_y},
                "style": {
                    "background": "white",
                    "border": "1px solid #d4d4d4",
                    "color": "black",
                    "width": 150,
                    "padding": "10px",
                    "borderRadius": "8px",
                    "fontSize": "12px"
                }
            })

            # Link Skill to Category
            edges.append({
                "id": f"e-{cat_id}-{skill_id}",
                "source": cat_id,
                "target": skill_id,
                "style": {"stroke": "#e5e5e5"}
            })

            # Save to DB (DynamoDB)
            await aws_store.save_skill(
                user_id="demo_user", # Hardcoded for hackathon demo
                skill_data={
                    "skill_name": skill["skill_name"],
                    "confidence_score": skill["confidence_score"],
                    "depth_score": skill["depth_score"],
                    "industry_relevance": skill.get("industry_relevance", 0),
                    "parent_skill": category,
                    "subskills": [] # Add logic for subskills if available
                }
            )

            # await db.skill_nodes.insert_one({ ... }) # Removed

    return {
        "message": "Analysis complete",
        "data": {
            "nodes": nodes,
            "edges": edges
        }
    }
