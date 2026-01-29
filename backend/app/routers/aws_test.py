from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.bedrock import invoke_nova_lite

router = APIRouter()

class PromptRequest(BaseModel):
    prompt: str

@router.post("/test-nova")
async def test_nova(request: PromptRequest):
    """
    Test endpoint to verify AWS Bedrock connectivity (Nova Lite).
    """
    response = invoke_nova_lite(request.prompt)
    if "Error" in response:
        raise HTTPException(status_code=500, detail=response)
    
    return {"model": "amazon.nova-lite-v1:0", "response": response}
