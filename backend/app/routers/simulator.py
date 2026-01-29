from fastapi import APIRouter
from pydantic import BaseModel
from app.services.game_engine import GameEngine, GameState

router = APIRouter()

class ActionRequest(BaseModel):
    session_id: str
    action_type: str # reply_email, submit_task
    payload: dict

@router.post("/simulator/start")
async def start_game(session_id: str = "demo_sim"):
    engine = GameEngine(session_id)
    return await engine.start_game()

@router.post("/simulator/action")
async def perform_action(request: ActionRequest):
    engine = GameEngine(request.session_id)
    new_state = await engine.process_action(request.action_type, request.payload)
    return new_state

@router.get("/simulator/state")
def get_state(session_id: str = "demo_sim"):
    engine = GameEngine(session_id)
    return engine.get_state()
