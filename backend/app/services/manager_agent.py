import json
from typing import List, Optional
from pydantic import BaseModel, Field
from app.services.bedrock import invoke_nova_pro, invoke_nova_lite

# Define Output Models
class TeamPersona(BaseModel):
    name: str
    role: str
    personality: str
    intro_email_subject: str
    intro_email_body: str

class IntroContent(BaseModel):
    manager_email_subject: str
    manager_email_body: str
    first_task_title: str
    first_task_description: str
    project_context: str
    team_members: List[TeamPersona]

class EmailReply(BaseModel):
    is_professional: bool
    manager_sentiment: str = Field(description="positive, neutral, or negative")
    reply_subject: str
    reply_body: str
    trust_score_change: int
    persona_used: str = "Manager"

class CodeReview(BaseModel):
    passed: bool
    feedback: str
    trust_score_change: int

class FollowUpTask(BaseModel):
    task_title: str
    task_description: str
    manager_comment: str

class ManagerAgent:
    def __init__(self):
        # Bedrock client is stateless/module-level, no strict init needed here
        # but we can log that we are in AWS mode
        print("ManagerAgent initialized in AWS Bedrock Mode.")

    def _parse_json_response(self, response_text: str, model_class: BaseModel) -> Optional[BaseModel]:
        """
        Helper to parse Bedrock JSON output into Pydantic models.
        """
        try:
            # Find the JSON object in the text (sometimes models add chatty preamble)
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = response_text[start:end]
                data = json.loads(json_str)
                return model_class(**data)
            else:
                print(f"Failed to find JSON in response: {response_text[:100]}...")
                return None
        except Exception as e:
            print(f"JSON Parsing Error: {e}")
            return None

    async def generate_onboarding(self) -> IntroContent:
        system_prompt = """You are Alice, an Engineering Manager at EduCorp.
You are professional, slightly demanding, and focused on results.
1. Invent a realistic, complex software project (e.g. 'FinTech Ledger', 'AI Logistics', 'Cybersecurity Threat Monitor').
2. Send a welcome email that sets high standards.
3. Assign a FIRST TASK that is DETAILED. It must include:
    - Objective
    - Technical constraints
    - Expected output format
    - **Acceptance Criteria**: What defines 'done'?
4. Create 2 distinct team members (AI Colleagues):
    - Example: "Bob (Senior Dev) - Grumpy but knowledgeable"
    - Example: "Sarah (Frontend Lead) - Cheerful but busy"

Output strictly JSON matching this structure:
{
    "manager_email_subject": "str",
    "manager_email_body": "str",
    "first_task_title": "str",
    "first_task_description": "str (markdown allowed)",
    "project_context": "str",
    "team_members": [
        {
            "name": "str",
            "role": "str",
            "personality": "str",
            "intro_email_subject": "str",
            "intro_email_body": "str"
        }
    ]
}"""
        user_prompt = "Generate the onboarding package with team details in JSON."
        
        response = invoke_nova_pro(system_prompt, user_prompt)
        # Handle potential error strings from bedrock wrapper
        if "Error" in response:
            print(f"Bedrock Error: {response}")
            return IntroContent(
                manager_email_subject="Welcome (System Error)",
                manager_email_body="Unable to connect to AWS Bedrock. Please check credentials.",
                first_task_title="Config Error",
                first_task_description="System is offline.",
                project_context="Offline",
                team_members=[]
            )

        content = self._parse_json_response(response, IntroContent)
        if not content:
             return IntroContent(
                manager_email_subject="Welcome",
                manager_email_body="Welcome to the team.",
                first_task_title="System Check",
                first_task_description="Verify system logs.",
                project_context="Recovery",
                team_members=[]
            )
        return content

    async def evaluate_email_reply(self, original_email_body: str, user_reply: str, trust_score: int) -> EmailReply:
        tone = "Professional"
        if trust_score < 40: tone = "Strict and Skeptical"
        elif trust_score > 70: tone = "Trusting and Casual"

        system_prompt = f"""You are Alice, Engineering Manager. Trust Score: {trust_score}/100. Tone: {tone}.
Evaluate the intern's reply. Output strictly JSON:
{{
    "is_professional": bool,
    "manager_sentiment": "positive|neutral|negative",
    "reply_subject": "str",
    "reply_body": "str",
    "trust_score_change": int (-10 to +10),
    "persona_used": "Manager"
}}"""
        user_prompt = f"My Email: {original_email_body}\nIntern Reply: {user_reply}\nGenerate JSON response."
        
        response = invoke_nova_lite(f"{system_prompt}\n\n{user_prompt}")
        content = self._parse_json_response(response, EmailReply)
        
        if not content:
            return EmailReply(is_professional=True, manager_sentiment="neutral", reply_subject="RE: Update", reply_body="Received.", trust_score_change=0)
        return content

    async def evaluate_code(self, task_desc: str, code: str, trust_score: int) -> CodeReview:
        system_prompt = f"""You are a Senior Code Reviewer. Task: {task_desc}.
Analyze the code. Output strictly JSON:
{{
    "passed": bool,
    "feedback": "str (constructive feedback)",
    "trust_score_change": int (-15 to +15)
}}"""
        user_prompt = f"Code:\n```python\n{code}\n```\nEvaluate this code."
        
        response = invoke_nova_pro(system_prompt, user_prompt)
        content = self._parse_json_response(response, CodeReview)
        
        if not content:
             return CodeReview(passed=True, feedback="Code parsing error, assuming pass.", trust_score_change=0)
        return content

    async def generate_followup_task(self, prev_task_title: str, prev_task_feedback: str) -> FollowUpTask:
        system_prompt = """You are Alice. Assign the next task.
Output strictly JSON:
{
    "task_title": "str",
    "task_description": "str (detailed markdown with Context, Objectives, Acceptance Criteria)",
    "manager_comment": "str"
}"""
        user_prompt = f"Previous Task: {prev_task_title}\nFeedback: {prev_task_feedback}\nGenerate next task JSON."
        
        response = invoke_nova_pro(system_prompt, user_prompt)
        content = self._parse_json_response(response, FollowUpTask)
        
        if not content:
            return FollowUpTask(task_title="Next Task", task_description="Continue project work.", manager_comment="Keep it up.")
        return content

    async def generate_colleague_response(self, colleague_name: str, colleague_role: str, colleague_persona: str, message: str, tasks_context: str = "") -> str:
        prompt = f"""You are {colleague_name}, a {colleague_role} at EduCorp. Persona: {colleague_persona}.

CURRENT PROJECT TASKS (you are aware of these):
{tasks_context if tasks_context else "No tasks assigned yet."}

User message: "{message}"

Reply in character (brief, slack style). If asked about tasks or work, reference the above task list."""
        
        return invoke_nova_lite(prompt)
