"""
AWS Store: DynamoDB CRUD operations for Skill Digital Twin
"""
import boto3
import os
from datetime import datetime
from typing import List, Dict, Optional
from boto3.dynamodb.conditions import Key

REGION_NAME = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
TABLE_PREFIX = os.getenv("DYNAMODB_TABLE_PREFIX", "educorp")

class AWSStore:
    def __init__(self):
        try:
            self.dynamodb = boto3.resource("dynamodb", region_name=REGION_NAME)
            self.skill_table_name = f"{TABLE_PREFIX}_SkillGraph"
            self.skill_table = self.dynamodb.Table(self.skill_table_name)
        except Exception as e:
            print(f"AWS Store init error: {e}")
            self.dynamodb = None
            self.skill_table = None

    async def save_skill(self, user_id: str, skill_data: Dict):
        """
        Saves a skill to DynamoDB with timestamp.
        """
        if not self.skill_table:
            print("DynamoDB table not available")
            return False
        
        try:
            item = {
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "skill_name": skill_data.get("skill_name", "Unknown"),
                "confidence_score": skill_data.get("confidence_score", 0),
                "depth_score": skill_data.get("depth_score", 0),
                "industry_relevance": skill_data.get("industry_relevance", 0),
                "parent_skill": skill_data.get("parent_skill", "General"),
                "subskills": skill_data.get("subskills", [])
            }
            self.skill_table.put_item(Item=item)
            return True
        except Exception as e:
            print(f"Error saving skill: {e}")
            return False

    async def get_user_skills(self, user_id: str) -> List[Dict]:
        """
        Retrieves all skills for a user from DynamoDB.
        Returns a list of skill dictionaries.
        """
        if not self.skill_table:
            print("DynamoDB table not available")
            return []
        
        try:
            response = self.skill_table.query(
                KeyConditionExpression=Key('user_id').eq(user_id)
            )
            items = response.get('Items', [])
            
            # Deduplicate by skill_name (keep latest)
            skill_map = {}
            for item in items:
                name = item.get('skill_name', 'Unknown')
                if name not in skill_map or item.get('timestamp', '') > skill_map[name].get('timestamp', ''):
                    skill_map[name] = item
            
            return list(skill_map.values())
        except Exception as e:
            print(f"Error fetching skills: {e}")
            return []

    async def get_skills_summary(self, user_id: str) -> str:
        """
        Returns a formatted string summary of user's skills for LLM context.
        """
        skills = await self.get_user_skills(user_id)
        if not skills:
            return "No skills data available for this user."
        
        summary_lines = []
        for s in skills:
            summary_lines.append(
                f"- {s.get('skill_name', 'Unknown')} "
                f"(Confidence: {s.get('confidence_score', 0)}%, "
                f"Depth: {s.get('depth_score', 0)}%, "
                f"Relevance: {s.get('industry_relevance', 0)}%)"
            )
        
        return "USER SKILL PROFILE:\n" + "\n".join(summary_lines)

# Singleton instance
aws_store = AWSStore()
