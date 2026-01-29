from fastapi import APIRouter, HTTPException, UploadFile, File
from app.services.rag_service import initialize_context, get_context
from app.services.file_parser import parse_file_content
from app.routers.interview_models import InterviewStartRequest, ChatRequest, ChatResponse, FeedbackResponse
from app.services.bedrock import invoke_nova_pro, invoke_nova_lite
import json
import os

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
sessions = {}

@router.post("/interview/start")
async def start_interview(request: InterviewStartRequest):
    session_id = "demo_session" 
    
    if request.job_description:
        await initialize_context(request.job_description)
    
    sessions[session_id] = {
        "history": [],
        "persona": request.persona,
        "resume_context": request.resume_text or "No resume provided.",
        "job_context": request.job_description or "No specific job description provided."
    }
    
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
    
    context = await get_context(request.message)
    resume_context = session.get("resume_context", "")
    job_context = session.get("job_context", "")
    persona = session.get("persona", "Interviewer")

    system_prompt = f"""You are an AI Interview Twin. Role: {persona}.
Objective: Conduct a rigorous interview.
INPUT CONTEXT:
Resume: {resume_context}
Job Description: {job_context}
Context: {context}

Maintain professional tone. If candidate is vague, probe deeper."""

    history_text = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in session.get("history", [])[-10:]])
    user_prompt = f"History:\n{history_text}\n\nCandidate: {request.message}\nYour Response:"

    response = invoke_nova_pro(system_prompt, user_prompt)
    if "Error" in response:
        response = "I'm having trouble connecting to the interview server. Please check back later."

    session["history"].append({"role": "user", "content": request.message})
    session["history"].append({"role": "ai", "content": response})
    
    return {"response": response}

@router.post("/interview/feedback", response_model=FeedbackResponse)
async def generate_feedback(session_id: str = "demo_session"):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    system_prompt = """You are an Expert Interview Evaluator.
Analyze the transcript. Output strictly JSON:
{
    "score": int,
    "readiness_score": {"Technical": int, "Behavioral": int, "Communication": int},
    "strengths": ["str"],
    "weaknesses": ["str"],
    "summary": "str"
}"""
    
    history_text = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in session.get("history", [])])
    user_prompt = f"Transcript:\n{history_text}\n\nGenerate Feedback JSON."
    
    response = invoke_nova_pro(system_prompt, user_prompt)
    
    try:
        start = response.find('{')
        end = response.rfind('}') + 1
        data = json.loads(response[start:end])
        return FeedbackResponse(**data)
    except Exception as e:
        print(f"Feedback JSON Error: {e}")
        return FeedbackResponse(
            score=0, readiness_score={}, strengths=[], weaknesses=[],
            summary="Error generating feedback report."
        )
