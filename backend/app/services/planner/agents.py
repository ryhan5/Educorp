from typing import List, Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.services.llm_factory import get_llm
from app.models import CareerGoal, MicroSkill, LearningResource

# --- Helper ---
async def invoke_bedrock_agent(prompt_template, output_model, input_vars, model_type="nova-pro"):
    """
    Generic wrapper to invoke a Bedrock agent with structured output.
    """
    # model_id selection inside get_llm is fixed to Nova Lite for now in factory. 
    # Logic note: If we needed Pro vs Lite switch, we'd adjust factory.
    # For Hackathon, 'amazon.nova-lite-v1:0' is default in factory.
    llm = get_llm(temperature=0.3) 
    
    parser = JsonOutputParser(pydantic_object=output_model)
    
    chain = prompt_template | llm | parser
    
    try:
        input_vars["format_instructions"] = parser.get_format_instructions()
        return await chain.ainvoke(input_vars)
    except Exception as e:
        print(f"Agent Invocation Failed: {e}")
        return None

# --- Agent 1: Goal Planner ---
class GoalPlannerAgent:
    """
    Analyzes the learner's Digital Twin context and generates high-level career goals.
    """
    async def generate_goals(self, learner_context: Dict[str, Any]) -> List[CareerGoal]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an Agentic Career Mentor.
            Analyze the learner's skill profile (Digital Twin) and define 1-2 strategic career goals.
            
            Logic:
            1. Identify WEAKNESSES (Confidence < 60).
            2. Identify STRENGTHS (Confidence > 80).
            3. Formulate a path: "Master [Weakness] to become a [Role]".
            4. Calculate 'Readiness Score' based on ratio of strong to weak skills.
            
            Output strictly JSON list of CareerGoals.
            """),
            ("user", "Learner Context: {context}\n\n{format_instructions}")
        ])

        results = await invoke_bedrock_agent(
            prompt, 
            output_model=List[CareerGoal], # Expecting list, handled by parser if we wrap in wrapper model or just list
            input_vars={"context": str(learner_context)}
        )
        
        # Determine if results is a list or dict wrapper
        if isinstance(results, list):
             return [CareerGoal(**g) for g in results]
        elif isinstance(results, dict) and "goals" in results:
             return [CareerGoal(**g) for g in results["goals"]]
        return []

# --- Agent 2: Micro-Skill Decomposer ---
class MicroSkillDecomposer:
    """
    Breaks down a high-level CareerGoal into atomic, actionable micro-skills.
    """
    async def decompose_goal(self, goal: CareerGoal) -> List[MicroSkill]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an Expert Curriculum Designer.
            Break down the provided Career Goal into 3-5 atomic MICRO-SKILLS.
            
            Rules:
            1. Skills must be ACTIONABLE (e.g., "Build a REST API" NOT "Learn Backend").
            2. Order them by dependency (Foundational -> Advanced).
            3. Estimate hours realistically.
            
            Output strictly JSON list of MicroSkills.
            """),
            ("user", "Goal: {goal_name}\nTarget Role: {target_role}\nMissing Skills: {missing}\n\n{format_instructions}")
        ])

        results = await invoke_bedrock_agent(
            prompt,
            output_model=List[MicroSkill],
            input_vars={
                "goal_name": goal.goal_name,
                "target_role": goal.target_role,
                "missing": str(goal.missing_skills)
            }
        )
         
        if isinstance(results, list):
             return [MicroSkill(**ms) for ms in results]
        elif isinstance(results, dict) and "skills" in results:
             return [MicroSkill(**ms) for ms in results["skills"]]
        return []

# --- Agent 3: Resource Selector (RAG) ---
class ResourceSelector:
    """
    Selects the best learning resources for a micro-skill.
    (Mock RAG for Hackathon speed, but architected for vector DB)
    """
    async def find_resources(self, micro_skill: MicroSkill) -> List[LearningResource]:
        # In a real RAG, this would query a VectorStore (OpenSearch/Pinecone)
        # Here we use Bedrock to "Simulate" a search or generating recommendations
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Learning Resource Curator.
            Recommend 2-3 High-Quality resources for the requested Micro-Skill.
            
            Sources to simulate:
            - Official Documentation
            - YouTube Tutorials
            - Interactive Coding Tasks
            
            Output strictly JSON list of LearningResources.
            """),
            ("user", "Micro-Skill: {name}\nDescription: {desc}\n\n{format_instructions}")
        ])

        results = await invoke_bedrock_agent(
            prompt,
            output_model=List[LearningResource],
            input_vars={"name": micro_skill.name, "desc": micro_skill.description}
        )
        
        if isinstance(results, list):
             return [LearningResource(**r) for r in results]
        elif isinstance(results, dict) and "resources" in results:
             return [LearningResource(**r) for r in results["resources"]]
        return []
