from typing import List, Optional
from app.models import LearningPath, CareerGoal, MicroSkill
from app.services.planner.skill_context import SkillContextManager
from app.services.planner.agents import GoalPlannerAgent, MicroSkillDecomposer, ResourceSelector
from app.services.aws_store import aws_store
import asyncio

class AgenticOrchestrator:
    """
    Orchestrates the multi-agent workflow:
    Context -> Goal Agent -> Decomposition Agent -> Resource Agent -> Learning Plan
    """
    
    def __init__(self, user_id: str = "demo_user"):
        self.user_id = user_id
        self.context_manager = SkillContextManager(user_id)
        self.goal_agent = GoalPlannerAgent()
        self.decomposer_agent = MicroSkillDecomposer()
        self.resource_agent = ResourceSelector()

    async def generate_plan(self) -> List[LearningPath]:
        print(f"--- Starting Agentic Planning for {self.user_id} ---")
        
        # 1. Gather Context (Digital Twin)
        context = await self.context_manager.get_learner_context()
        print(f"Context retrieved: {context['primary_weakness']}")
        
        # 2. Define Goals (Goal Agent)
        goals = await self.goal_agent.generate_goals(context)
        print(f"Goals generated: {len(goals)}")
        
        learning_paths = []
        
        for goal in goals:
            print(f"Processing Goal: {goal.goal_name}")
            
            # 3. Decompose into Micro-Skills (Decomposer Agent)
            micro_skills = await self.decomposer_agent.decompose_goal(goal)
            print(f"Decomposed into {len(micro_skills)} micro-skills")
            
            # 4. Attach Resources (Resource Agent)
            # Parallelize resource fetching for speed
            tasks = [self.resource_agent.find_resources(ms) for ms in micro_skills]
            resources_list = await asyncio.gather(*tasks)
            
            # Assign resources back to micro-skills
            for ms, resources in zip(micro_skills, resources_list):
                ms.resources = resources
            
            # 5. Assemble Path
            path = LearningPath(
                user_id=self.user_id,
                goals=[goal],
                daily_tasks=micro_skills,
                # Legacy fields for frontend compatibility
                skill_name=goal.goal_name, 
                reasoning=goal.reasoning,
                resources=[r for ms in micro_skills for r in ms.resources][:5], # Flatten top 5 for preview
                estimated_hours=sum(ms.estimated_hours for ms in micro_skills)
            )
            
            # 6. Save to DynamoDB
            await aws_store.save_learning_path(path)
            
            learning_paths.append(path)

        return learning_paths
