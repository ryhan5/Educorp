from fastapi import APIRouter, HTTPException, UploadFile, File
from app.services.rag_service import initialize_context, get_context
from app.services.file_parser import parse_file_content
from app.routers.interview_models import InterviewStartRequest, ChatRequest, ChatResponse, FeedbackResponse
# from langchain_groq import ChatGroq # Removed
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.services.llm_factory import get_llm
import os
import random

router = APIRouter()

@router.post("/interview/parse-resume")
async def parse_resume(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    content = await file.read()
    text = await parse_file_content(content, file.filename)
    
    if not text:
        raise HTTPException(status_code=400, detail="Could not extract text from file")
        
    return {"text": text}


# Simple in-memory session store
# session_id -> { history: [], persona: str, resume_context: str, job_context: str }
sessions = {}

@router.post("/interview/start")
async def start_interview(request: InterviewStartRequest):
    session_id = "demo_session" # For prototype, single session
    
    # Initialize RAG if JD is provided
    if request.job_description:
        await initialize_context(request.job_description)
    
    sessions[session_id] = {
        "history": [],
        "persona": request.persona,
        "resume_context": request.resume_text or "No resume provided.",
        "job_context": request.job_description or "No specific job description provided."
    }
    
    # Generate initial greeting based on persona
    greeting_map = {
        "Technical Interviewer": "Hello. I am your Technical Interviewer. I have your resume here. Shall we start with a brief introduction?",
        "HR Manager": "Hi there! I'm the HR Manager. Thanks for joining. To kick things off, tell me a bit about yourself.",
        "Hiring Manager": "Good to meet you. I'm the Hiring Manager. I want to understand how you'd fit into our team. Ready?"
    }
    
    greeting = greeting_map.get(request.persona, "Hello, let's begin the interview.")
    
    return {"session_id": session_id, "message": greeting}

@router.post("/interview/chat", response_model=ChatResponse)
async def chat_interview(request: ChatRequest):
    session = sessions.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # 1. Retrieve Context
    context = await get_context(request.message)
    
    # 2. Prepare Prompt
    resume_context = session.get("resume_context", "")
    job_context = session.get("job_context", "")
    persona = session.get("persona", "Interviewer")

    system_prompt_base = f"""You are an AI Interview Twin designed to simulate real-world hiring processes.
Role: {persona}
Objective: Conduct a rigorous, realistic interview. Evaluate candidates holistically.

INPUT CONTEXT:
Resume: {resume_context}
Job Description: {job_context}
RAG Context (Knowledge Base): {context}

CORE BEHAVIORS:
1. Use the resume to personalize questions. Probe claims.
2. If the candidate is vague, ask follow-ups.
3. If {persona} == "Technical Interviewer": Focus on skill depth, coding (ask for pseudo-code or logic), and system design.
4. If {persona} == "HR Manager": Focus on culture fit, motivation, and soft skills.
5. If {persona} == "Hiring Manager": Focus on ownership, strategic thinking, and leadership.

Maintain a professional, conversational tone. Do not repeat yourself.
"""

    # api_key = os.getenv("GROQ_API_KEY")
    # if not api_key: ... (Removed)

    llm = get_llm(temperature=0.6)
    
    # Construct history
    history_messages = []
    # Limit history to prevent context overflow, but keep system prompt separate
    for msg in session["history"][-10:]: 
        history_messages.append(("user" if msg["role"] == "user" else "ai", msg["content"]))
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_base),
        *history_messages,
        ("user", "{input}")
    ])
    
    chain = prompt | llm
    
    try:
        response = await chain.ainvoke({"input": request.message})
        response_text = response.content
    except Exception as e:
        print(f"Groq Error: {e}")
        response_text = "I apologize, I briefly lost connection. Could you repeat that?"

    # Update History
    session["history"].append({"role": "user", "content": request.message})
    session["history"].append({"role": "ai", "content": response_text})
    
    return {"response": response_text}

@router.post("/interview/feedback", response_model=FeedbackResponse)
async def generate_feedback(session_id: str = "demo_session"):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # api_key = os.getenv("GROQ_API_KEY") ... (Removed)

    llm = get_llm(temperature=0.3)
    parser = JsonOutputParser(pydantic_object=FeedbackResponse)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an Expert Interview Evaluator.
Analyze the transcript and provide a detailed evaluation.
Output JSON matching the schema.
- 'score': 0-100
- 'readiness_score': Dictionary with keys like 'Technical', 'Behavioral', 'Communication', 'Leadership' and values 0-100.
- 'strengths': List of top 3 assets.
- 'weaknesses': List of top 3 gaps.
- 'summary': A professional paragraph summarizing the candidate's performance and hiring recommendation.
"""),
        ("user", "Transcript:\n{transcript}\n\n{format_instructions}")
    ])
    
    chain = prompt | llm | parser
    
    # Construct Transcript
    history_text = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in session.get("history", [])])

    try:
        result = await chain.ainvoke({
            "transcript": history_text,
            "format_instructions": parser.get_format_instructions()
        })
        return FeedbackResponse(**result)
    except Exception as e:
        print(f"Feedback Generation Failed: {e}")
        return FeedbackResponse(
            score=0,
            readiness_score={},
            strengths=[],
            weaknesses=["Error generating feedback"],
            summary=f"Analysis failed: {str(e)}"
        )
