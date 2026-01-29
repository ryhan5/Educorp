from typing import Dict, List, Any
from app.services.aws_store import aws_store

class SkillContextManager:
    """
    Interfaces with the Skill Digital Twin (DynamoDB) to retrieve
    the learner's current state, confident skills, and weak areas.
    """
    
    def __init__(self, user_id: str = "demo_user"):
        self.user_id = user_id

    async def get_learner_context(self) -> Dict[str, Any]:
        """
        Aggregates skill graph data into a context object for the Agent.
        """
        # Fetch from DynamoDB
        raw_graph = await aws_store.get_user_graph(self.user_id)
        
        skills = []
        weak_skills = []
        strong_skills = []
        
        for item in raw_graph:
            if item.get("type") == "skill":
                skill = {
                    "name": item.get("skill_name"),
                    "confidence": int(item.get("confidence_score", 0)),
                    "depth": int(item.get("depth_score", 0)),
                    "relevance": int(item.get("industry_relevance", 0))
                }
                skills.append(skill)
                
                if skill["confidence"] < 60:
                    weak_skills.append(skill)
                elif skill["confidence"] > 80:
                    strong_skills.append(skill)
        
        # Default context if empty (Cold Start)
        if not skills:
            skills = [{"name": "General Tech", "confidence": 0, "depth": 0}]
            weak_skills = skills

        return {
            "user_id": self.user_id,
            "total_skills": len(skills),
            "skills": skills,
            "weak_skills": weak_skills,
            "strong_skills": strong_skills,
            "top_strength": strong_skills[0]["name"] if strong_skills else "None",
            "primary_weakness": weak_skills[0]["name"] if weak_skills else "None"
        }
