import json
from typing import List, Optional
from pydantic import BaseModel, Field
from app.services.bedrock import invoke_nova_pro

# Define the structure for a single skill
class SkillData(BaseModel):
    skill_name: str = Field(description="Name of the skill, e.g., 'Python', 'React'")
    confidence_score: int = Field(description="Confidence score from 0 to 100 based on the text evidence")
    depth_score: int = Field(description="Depth of knowledge from 0 to 100 based on complexity of usage")
    industry_relevance: int = Field(description="Estimated industry demand/relevance from 0 (obsolete) to 100 (high demand)")
    parent_skill: Optional[str] = Field(description="The direct parent category or skill, e.g., 'Backend Development' for 'Python'. logic: infer likely parent if not explicit.", default=None)

class SkillList(BaseModel):
    skills: List[SkillData]

def _parse_skills_json(text: str) -> List[dict]:
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != -1:
            json_str = text[start:end]
            data = json.loads(json_str)
            # Normalize list logic
            if "skills" in data:
                return data["skills"]
            return [] # Fallback
        return []
    except Exception as e:
        print(f"JSON Parse Error in Skills: {e}")
        return []

async def extract_skills_from_text(text: str) -> List[dict]:
    """
    Extracts skills using Amazon Nova Pro.
    """
    
    system_prompt = """You are an expert technical recruiter. 
Extract a structured list of technical skills from the user's text.
Analyze the context to determine:
- Confidence Level (0-100)
- Depth Score (0-100)
- Industry Relevance (0-100)
- Parent Skill (Logical hierarchy)

Output strictly JSON with this schema:
{
    "skills": [
        {
            "skill_name": "str",
            "confidence_score": int,
            "depth_score": int,
            "industry_relevance": int,
            "parent_skill": "str"
        }
    ]
}"""
    
    user_prompt = f"Analyze the following text from Resume/GitHub/Courses:\n{text}"

    response = invoke_nova_pro(system_prompt, user_prompt)
    
    if "Error" in response:
        print(f"Bedrock Error in Skill Extractor: {response}")
        return []

    skills = _parse_skills_json(response)
    return skills
