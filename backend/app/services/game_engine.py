import uuid
from typing import List, Optional, Dict
from pydantic import BaseModel
import random
from app.services.manager_agent import ManagerAgent

# Models
class Email(BaseModel):
    id: str
    sender: str
    subject: str
    body: str
    is_read: bool = False
    replied: bool = False

class Task(BaseModel):
    id: str
    title: str
    description: str
    status: str = "todo" # todo, in_progress, done

class GameState(BaseModel):
    day: int = 1
    trust_score: int = 50
    emails: List[Email] = []
    tasks: List[Task] = []
    logs: List[str] = []
    project_context: str = ""

# In-memory store logic
# session_id -> GameState
games: Dict[str, GameState] = {}

class GameEngine:
    def __init__(self, session_id: str):
        self.session_id = session_id
        if session_id not in games:
            games[session_id] = GameState()
        self.state = games[session_id]
        self.agent = ManagerAgent()

    async def start_game(self):
        try:
            self.state = GameState() # Reset
            self.state.logs.append("Booting EduCorp OS...")
            
            # Agentic Onboarding
            with open("backend_debug.log", "a") as f:
                f.write("GameEngine: Calling generate_onboarding\n")
            
            content = await self.agent.generate_onboarding()
            
            with open("backend_debug.log", "a") as f:
                f.write(f"GameEngine: Onboarding content received: {content}\n")

            self.state.project_context = content.project_context
            self.state.logs.append(f"Assigned to Project: {content.project_context}")
            
            # Initial Email from Agent
            self._send_email(
                sender="Manager (Alice)",
                subject=content.manager_email_subject,
                body=content.manager_email_body
            )
            
            # Initial Task from Agent
            self.state.tasks.append(Task(
                id=str(uuid.uuid4()),
                title=content.first_task_title,
                description=content.first_task_description
            ))
            
            games[self.session_id] = self.state
            return self.state
        except Exception as e:
            with open("backend_debug.log", "a") as f:
                f.write(f"CRITICAL ERROR in GameEngine.start_game: {str(e)}\n")
            raise e

    async def process_action(self, action_type: str, payload: dict):
        if action_type == "reply_email":
            email_id = payload.get("email_id")
            content = payload.get("content", "")
            await self._handle_email_reply(email_id, content)
            
        elif action_type == "submit_task":
            task_id = payload.get("task_id")
            code = payload.get("code", "")
            await self._handle_task_submission(task_id, code)

        return self.state

    def _send_email(self, sender, subject, body):
        email = Email(
            id=str(uuid.uuid4()),
            sender=sender,
            subject=subject,
            body=body
        )
        self.state.emails.insert(0, email) # Newest first

    async def _handle_email_reply(self, email_id, content):
        # Find email
        email = next((e for e in self.state.emails if e.id == email_id), None)
        if not email: return
        
        email.replied = True
        self.state.logs.append(f"Replied to {email.sender}")

        # Agent Evaluation
        reply_evaluation = await self.agent.evaluate_email_reply(email.body, content, self.state.trust_score)
        
        # Update Game State based on Agent
        self.state.trust_score += reply_evaluation.trust_score_change
        
        # Cap trust score
        self.state.trust_score = max(0, min(100, self.state.trust_score))
        
        # Send Agent's Counter-Reply
        self._send_email(
            sender="Manager (Alice)",
            subject=reply_evaluation.reply_subject,
            body=reply_evaluation.reply_body
        )

    async def _handle_task_submission(self, task_id, code):
        task = next((t for t in self.state.tasks if t.id == task_id), None)
        if not task: return

        # Agent Evaluation
        review = await self.agent.evaluate_code(task.description, code, self.state.trust_score)
        
        self.state.trust_score += review.trust_score_change
        self.state.trust_score = max(0, min(100, self.state.trust_score))
        
        self.state.logs.append(f"Code Review: {review.feedback}")

        if review.passed:
             task.status = "done"
             # Maybe generate next task? Leaving simple for now.
             self._send_email(
                 sender="System",
                 subject="Task Completed",
                 body=f"Task '{task.title}' marked as done. Good job. \n\nReviewer Feedback: {review.feedback}"
             )
        else:
             self._send_email(
                 sender="System",
                 subject="Build Failed",
                 body=f"Your submission for '{task.title}' was rejected.\n\nFeedback: {review.feedback}\n\nTrust Impact: {review.trust_score_change}"
             )

    def get_state(self):
        return self.state
