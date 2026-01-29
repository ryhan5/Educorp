import os
from typing import List, Optional
from app.database import db
from app.models import LearningPath, LearningResource
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser


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

async def generate_mindmap_plan(topic: str) -> MindMapData:
    mock_data = MindMapData(
        nodes=[
            MindMapNode(id="1", label=topic, type="root"),
            MindMapNode(id="2", label="Basics (Mock)", type="concept"),
            MindMapNode(id="3", label="Advanced (Mock)", type="concept"),
            MindMapNode(id="4", label="Official Docs", type="resource", url="https://example.com"),
        ],
        edges=[
            MindMapEdge(id="e1-2", source="1", target="2"),
            MindMapEdge(id="e1-3", source="1", target="3"),
            MindMapEdge(id="e2-4", source="2", target="4"),
        ]
    )

    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("DEBUG: GROQ_API_KEY is missing.")
        return MindMapData(
            nodes=[
                MindMapNode(id="root", label="Error: GROQ_API_KEY Missing", type="root"),
                MindMapNode(id="info", label="Get key from console.groq.com", type="resource"),
            ],
            edges=[MindMapEdge(id="e1", source="root", target="info")]
        )

    # Agentic Search Step
    tavily_key = os.getenv("TAVILY_API_KEY")
    search_context = ""
    if tavily_key:
        try:
            search_tool = TavilySearchResults(max_results=3)
            # Synchronous invoke within async function (LangChain legacy behavior safe here)
            results = search_tool.invoke(f"guide to learning {topic} roadmap key concepts")
            search_context = str(results)
        except Exception:
            pass

    # Use Groq (Llama-3.3-70b)
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7, groq_api_key=api_key)
    parser = JsonOutputParser(pydantic_object=MindMapData)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an AI Curriculum Agent. Create a detailed learning mindmap.\n"
                   "1. Analyze the Topic.\n"
                   "2. Break it down into Core Concepts.\n"
                   "3. For each concept, recommend REAL, specific tutorials/docs (found in Context or from your knowledge).\n"
                   "Structure: Root -> Concepts -> Resources.\n"
                   "Return JSON with 'nodes' and 'edges'."),
        ("user", "Context: {context}\n\nTopic: {topic}\n\n{format_instructions}")
    ])

    chain = prompt | llm | parser

    try:
        print(f"DEBUG: invoking Groq for topic: {topic}")
        result = await chain.ainvoke({
            "topic": topic,
            "context": search_context,
            "format_instructions": parser.get_format_instructions()
        })
        print("DEBUG: Groq response received.")
        return MindMapData(**result)
    except Exception as e:
        print(f"CRITICAL ERROR in Mindmap Generation: {e}")
        return mock_data

class WidgetResponse(BaseModel):
    name: str
    html_content: str
    description: str

async def generate_interactive_widget(topic: str) -> WidgetResponse:
    print(f"DEBUG: Generating widget for {topic}")
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        return WidgetResponse(
            name="Error",
            html_content="<div style='color:white; padding: 20px;'>Error: GROQ_API_KEY Missing</div>",
            description="Cannot generate widget without API key."
        )

    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7, groq_api_key=api_key)
    parser = JsonOutputParser(pydantic_object=WidgetResponse)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Visualization Expert and Award-Winning Frontend Engineer.
Your goal is to explain a concept by creating a DEEP, ENGAGING INTERACTIVE WIDGET.
Don't just show 'text', show 'mechanics'.

### VISUALIZATION STRATEGIES (Use the best one):
1. **Algorithms (Sorting, Pathfinding)**: Use **Animated Bar Charts** or **Grid Maps**. 
   - *CRITICAL*: Show the "current state" in RED, "processed" in GREEN. 
   - animate the transitions (swapping bars) smoothly using CSS `transition: all 0.3s`.
2. **Data Structures (Trees, Graphs, Lists)**: Use **SVG Nodes & Edges**.
   - Render circles for nodes, lines for edges.
   - Highlight the "traversal path" dynamically.
3. **Systems/Concepts (Docker, API, ML)**: Use **Flow Diagrams**.
   - Animated particles moving between boxes (e.g., "Request" moving from "Client" to "Server").

### REQUIREMENTS (JSON Output):
- name: Title.
- html_content: COMPLETE, SELF-CONTAINED HTML/JS.
    - **Libraries**: TailwindCSS (CDN) is REQUIRED for layout.
    - **No External Logic**: All JS must be inside the `<script>`.
    - **UI Layout**:
        1. **Top**: Visualization Canvas (White bg, rounded corners, shadow).
        2. **Middle**: Controls (Play, Pause, Step Next, Reset).
        3. **Bottom**: **Explanation Console** (Typewriter text explaining exactly what is happening in this specific step).
    - **Code Quality**: Use `async/await` for sleep functions to visualize steps (e.g. `await new Promise(r => setTimeout(r, 500))`).
- description: Brief summary.
"""),
        ("user", "Create a World-Class Interactive Widget for: {topic}\n\n{format_instructions}")
    ])

    chain = prompt | llm | parser

    try:
        result = await chain.ainvoke({
            "topic": topic,
            "format_instructions": parser.get_format_instructions()
        })
        return WidgetResponse(**result)
    except Exception as e:
        print(f"Widget Generation Failed: {e}")
        return WidgetResponse(
            name="Generation Failed",
            html_content=f"<div style='color:red'>Failed to generate widget: {str(e)}</div>",
            description="Error occurred during generation."
        )

async def generate_learning_plan() -> List[LearningPath]:
    # 1. Fetch skills from DB
    skills_cursor = db.skill_nodes.find({})
    skills = await skills_cursor.to_list(length=100)
    
    if not skills:
        skills = [{"skill_name": "Python (Demo)", "confidence_score": 30}]

    # 2. Identify Weak Skills (Confidence < 70)
    weak_skills = [s for s in skills if s.get("confidence_score", 0) < 70]
    
    if not weak_skills:
        weak_skills = [{"skill_name": "Advanced System Design", "confidence_score": 50}]

    plans = []
    
    # Initialize Tools
    tavily_key = os.getenv("TAVILY_API_KEY")
    search_tool = None
    if tavily_key:
        search_tool = TavilySearchResults(max_results=3)

    # Use Groq for Planner logic as well
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("WARNING: GROQ_API_KEY not found. Using mock planner.")
        # Mock Plan Generation
        for skill in weak_skills:
             plans.append(LearningPath(
                 skill_name=skill["skill_name"],
                 reasoning="Confidence is low (Mock Logic due to missing Key)",
                 resources=[
                     LearningResource(title=f"Learn {skill['skill_name']} (Mock)", url="https://example.com/docs"),
                     LearningResource(title=f"Advanced {skill['skill_name']} Course (Mock)", url="https://example.com/course", type="video")
                 ],
                 estimated_hours=10
             ))
        return plans

    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7, groq_api_key=groq_api_key)
    
    parser = JsonOutputParser(pydantic_object=LearningPath)

    # New Agentic Persona
    system_prompt = """You are an Agentic Learning Planner.
Your role is to function as a personalized career manager, not a static recommendation engine.
Unlike fixed roadmaps, you must continuously reason, plan, monitor, and adapt a learner’s journey based on real performance data.

CORE RESPONSIBILITIES:
1. DEFINE CAREER GOALS: Establish clear objectives based on skill gaps.
2. BREAK DOWN SKILLS: Deconstruct goals into atomic micro-skills and specific tasks.
3. ASSIGN LEARNING & TASKS: Select the most effective resources and REAL-WORLD tasks. Avoid passive learning.

AGENT BEHAVIOR:
- Adaptive: Adjusts pace based on confidence score.
- Goal-Oriented: Every step maps to career objectives.
- Performance-Driven: Recommendations are based on potential for measurable improvement.

Output must strictly follow the JSON schema provided.
- 'reasoning': Explain WHY this path and these specific resources were chosen based on the confidence level.
- 'resources': A list of mixed tutorials, documentation, and specific PRACTICAL TASKS (labeled as 'task' in title if possible).
"""

    for skill in weak_skills:
        skill_name = skill["skill_name"]
        confidence = skill["confidence_score"]
        
        # 3. Agentic Search
        search_results = []
        if search_tool:
            try:
                search_results = search_tool.invoke(f"best advanced interactive tutorial for {skill_name} 2024 with projects")
            except Exception as e:
                print(f"Search failed for {skill_name}: {e}")
        
        context_str = str(search_results) if search_results else "No external search results. Use best known resources."

        # 4. Generate Plan via LLM
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "Context: {context}\n\nSkill: {skill_name}\nCurrent Confidence: {confidence}/100\n\n{format_instructions}")
        ])
        
        chain = prompt | llm | parser
        
        try:
            plan_data = await chain.ainvoke({
                "skill_name": skill_name,
                "confidence": confidence,
                "context": context_str,
                "format_instructions": parser.get_format_instructions()
            })
            
            # Convert and Validate
            plan = LearningPath(**plan_data)
            plans.append(plan)
            
            # Save to DB
            await db.learning_paths.insert_one(plan.dict())
            
        except Exception as e:
            print(f"Failed to generate plan for {skill_name}: {e}")
            # Fallback to simple plan if LLM fails
            plans.append(LearningPath(
                skill_name=skill_name,
                reasoning=f"Agent generation failed: {str(e)}. Using fallback.",
                resources=[LearningResource(title=f"Documentation for {skill_name}", url=f"https://www.google.com/search?q={skill_name}")]
            ))

    return plans
