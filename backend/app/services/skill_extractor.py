import os
from typing import List, Optional
from pydantic import BaseModel, Field
# from langchain_groq import ChatGroq # Removed
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Define the structure for a single skill
class SkillData(BaseModel):
    skill_name: str = Field(description="Name of the skill, e.g., 'Python', 'React'")
    confidence_score: int = Field(description="Confidence score from 0 to 100 based on the text evidence")
    depth_score: int = Field(description="Depth of knowledge from 0 to 100 based on complexity of usage")
    industry_relevance: int = Field(description="Estimated industry demand/relevance from 0 (obsolete) to 100 (high demand)")
    parent_skill: Optional[str] = Field(description="The direct parent category or skill, e.g., 'Backend Development' for 'Python'. logic: infer likely parent if not explicit.", default=None)

# Define the list structure
class SkillList(BaseModel):
    skills: List[SkillData]

async def extract_skills_from_text(text: str) -> List[dict]:
    # Use AWS Bedrock via Factory
    from app.services.llm_factory import get_llm
    
    try:
        llm = get_llm(temperature=0)
    except Exception as e:
        print(f"Error initializing Bedrock: {e}")
        return []

    parser = JsonOutputParser(pydantic_object=SkillList)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert technical recruiter and resume analyzer. Extract a structured list of technical skills from the provided text. \n"
                   "Analyze the context to determine:\n"
                   "- Confidence Level (how much evidence of mastery)\n"
                   "- Depth Score (complexity of usage)\n"
                   "- Industry Relevance (current market demand)\n"
                   "- Parent Skill (create a logical hierarchy, grouping specific tools under broader categories like 'Frontend', 'Cloud', 'Data Science', etc.)\n"
                   "Output purely JSON."),
        ("user", "{format_instructions}\n\nAnalyze the following text from Resume/GitHub/Courses:\n{text}")
    ])

    chain = prompt | llm | parser

    try:
        result = await chain.ainvoke({
            "text": text,
            "format_instructions": parser.get_format_instructions()
        })
        return result.get("skills", [])
    except Exception as e:
        import traceback
        with open("bedrock_error.log", "a") as f:
            f.write(f"Error during LLM extraction: {str(e)}\n")
            f.write(traceback.format_exc() + "\n")
        print(f"Error during LLM extraction: {e}")
        return []
