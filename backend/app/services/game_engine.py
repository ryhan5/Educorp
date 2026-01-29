import uuid
from typing import List, Optional, Dict
from pydantic import BaseModel
import random
from app.services.manager_agent import ManagerAgent
from app.services.aws_store import aws_store

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
    team_members: List[dict] = [] # Store team personas

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
            
            # Fetch user skills from Skill Twin (DynamoDB)
            skills_context = await aws_store.get_skills_summary(user_id="demo_user")
            self.state.logs.append("Loaded Skill Profile from Digital Twin...")
            
            # Agentic Onboarding with skill context
            with open("backend_debug.log", "a") as f:
                f.write(f"GameEngine: Calling generate_onboarding with skills: {skills_context[:100]}...\n")
            
            content = await self.agent.generate_onboarding(skills_context=skills_context)
            
            with open("backend_debug.log", "a") as f:
                f.write(f"GameEngine: Onboarding content received: {content}\n")

            self.state.project_context = content.project_context
            self.state.logs.append(f"Assigned to Project: {content.project_context}")
            
            # Initial Email from Manager
            self._send_email(
                sender="Manager (Alice)",
                subject=content.manager_email_subject,
                body=content.manager_email_body
            )

            # Team Intros
            self.state.team_members = [t.dict() for t in content.team_members]
            for member in content.team_members:
                self._send_email(
                    sender=f"{member.name} ({member.role})",
                    subject=member.intro_email_subject,
                    body=member.intro_email_body
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

        elif action_type == "chat_colleague":
            member_name = payload.get("member_name")
            message = payload.get("message")
            await self._handle_colleague_chat(member_name, message)

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
             
             # Generate Follow-up Task
             followup = await self.agent.generate_followup_task(task.title, review.feedback)
             
             # Create new task
             new_task_id = str(uuid.uuid4())
             self.state.tasks.append(Task(
                 id=new_task_id,
                 title=followup.task_title,
                 description=followup.task_description
             ))

             self._send_email(
                 sender="Manager (Alice)",
                 subject="Task Approved & Next Steps",
                 body=f"Good work on '{task.title}'.\n\nReview Feedback: {review.feedback}\n\n{followup.manager_comment}\n\nI've assigned your next task: {followup.task_title}"
             )
        else:
             self._send_email(
                 sender="Manager (Alice)",
                 subject="Code Rejected - Revisions Needed",
                 body=f"Your submission for '{task.title}' was rejected.\n\nFeedback: {review.feedback}\n\nFix the issues and resubmit."
             )

    async def _handle_colleague_chat(self, member_name, message):
        # Find member
        member = next((m for m in self.state.team_members if m['name'] == member_name), None)
        if not member: return

        # Store user message
        if 'chats' not in member: member['chats'] = []
        member['chats'].append({"sender": "You", "message": message})
        
        # Build task context for AI awareness
        tasks_context = "\n".join([
            f"- [{t.status.upper()}] {t.title}: {t.description}"
            for t in self.state.tasks
        ]) if self.state.tasks else "No tasks assigned yet."
        
        # Get response with task awareness
        response = await self.agent.generate_colleague_response(
            member['name'], member['role'], member['personality'], message, tasks_context
        )
        
        # Store response
        member['chats'].append({"sender": member['name'], "message": response})
        self.state.logs.append(f"Chatted with {member_name}")

    def get_state(self):
         return self.state
