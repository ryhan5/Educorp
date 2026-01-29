import os
import json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

# Define Output Models
class IntroContent(BaseModel):
    manager_email_subject: str
    manager_email_body: str
    first_task_title: str
    first_task_description: str
    project_context: str

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

class ManagerAgent:
    def __init__(self):
        try:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                print("WARNING: GROQ_API_KEY missing. Agent will be lobotomized.")
                self.llm = None
            else:
                self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7, groq_api_key=api_key)
            
            with open("backend_debug.log", "a") as f:
                f.write("ManagerAgent initialized successfully.\n")
                
        except Exception as e:
            with open("backend_debug.log", "a") as f:
                f.write(f"CRITICAL ERROR in ManagerAgent __init__: {str(e)}\n")
            print(f"CRITICAL ERROR in ManagerAgent: {e}")
            self.llm = None

    async def generate_onboarding(self) -> IntroContent:
        with open("backend_debug.log", "a") as f:
            f.write("Entering generate_onboarding\n")

        if not self.llm:
            return IntroContent(
                manager_email_subject="Welcome (Offline Mode)",
                manager_email_body="Groq API key missing. Using fallback.",
                first_task_title="Setup Config",
                first_task_description="Add your API Key to .env file.",
                project_context="Maintenance"
            )

        try:
            parser = JsonOutputParser(pydantic_object=IntroContent)
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are Alice, an Engineering Manager at EduCorp.
You are professional, slightly demanding, and focused on results.
1. Invent a realistic software project (e.g. 'Legacy API Migration', 'Cloud Data Lake', 'Internal Dashboard').
2. Send a welcome email that sets high standards.
3. Assign a FIRST TASK that is small but specific (e.g. 'Write a script to clean this CSV', 'Fix a specific Regex bug').
4. Do NOT be overly cheerful. Be corporate."""),
                ("user", "Generate the onboarding package.\n\n{format_instructions}")
            ])

            chain = prompt | self.llm | parser
            result = await chain.ainvoke({"format_instructions": parser.get_format_instructions()})
            return IntroContent(**result)
        except Exception as e:
             print(f"Error generating onboarding: {e}")
             return IntroContent(
                manager_email_subject="Welcome",
                manager_email_body="Welcome to the team.",
                first_task_title="System Check",
                first_task_description="Verify system logs.",
                project_context="Recovery"
            )

    async def evaluate_email_reply(self, original_email_body: str, user_reply: str, trust_score: int) -> EmailReply:
        if not self.llm:
            return EmailReply(is_professional=True, manager_sentiment="neutral", reply_subject="RE: Reply", reply_body="Got it.", trust_score_change=0, persona_used="Manager")
        
        # Determine Tone based on Trust
        tone = "Professional and Trusting"
        if trust_score < 40:
            tone = "Micromanaging, Skeptical, and Strict. Demand better updates."
        elif trust_score < 70:
            tone = "Professional but monitoring closely."
        else:
            tone = "Casual and trusting. Brief responses."

        parser = JsonOutputParser(pydantic_object=EmailReply)
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are Alice, the Engineering Manager.
Current Trust Score: {trust_score}/100.
Your Tone: {tone}

Evaluate the intern's email reply.
- If they are vague, rude, or late -> Deduct Trust severely. Be harsh.
- If they are clear, professional, and ownership-driven -> Add Trust. Be approving.

Output 'is_professional', 'manager_sentiment', 'trust_score_change' (-10 to +10), and your 'reply_body'."""),
            ("user", "My Last Email: {original_email}\nIntern's Reply: {user_reply}\n\nGenerate your counter-reply.\n\n{format_instructions}")
        ])

        chain = prompt | self.llm | parser
        try:
            result = await chain.ainvoke({
                "original_email": original_email_body, 
                "user_reply": user_reply,
                "format_instructions": parser.get_format_instructions()
            })
            return EmailReply(**result)
        except Exception as e:
            print(f"Error evaluating reply: {e}")
            return EmailReply(is_professional=True, manager_sentiment="neutral", reply_subject="RE: Update", reply_body="Received.", trust_score_change=0, persona_used="Manager")

    async def evaluate_code(self, task_desc: str, code: str, trust_score: int) -> CodeReview:
        if not self.llm:
             return CodeReview(passed=True, feedback="Offline mode: Code accepted.", trust_score_change=5)

        # stricter review if trust is low
        strictness = "Standard"
        if trust_score < 40:
            strictness = "EXTREME. Fail them for minor style issues or lack of comments."
        
        parser = JsonOutputParser(pydantic_object=CodeReview)
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are a Senior Engineer Code Reviewer.
Review Strictness: {strictness}

Task: {task_desc}

Analyze the Python code below.
1. Funcationality: Does it solve the problem?
2. Quality: Variable names, comments, edge cases.
3. Professionalism: No placeholder 'pass' unless valid.

If it fails: Provide specific, constructive, but firm feedback. Trust -5 to -15.
If it passes: Provide brief kudos. Trust +5 to +15.
"""),
            ("user", "Intern's Code:\n```python\n{code}\n```\n\n{format_instructions}")
        ])

        chain = prompt | self.llm | parser
        try:
            result = await chain.ainvoke({
                "task_desc": task_desc,
                "code": code,
                "format_instructions": parser.get_format_instructions()
            })
            return CodeReview(**result)
        except Exception as e:
            print(f"Error evaluating code: {e}")
            return CodeReview(passed=False, feedback="Error evaluating code.", trust_score_change=0)
