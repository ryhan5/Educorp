import asyncio
import sys
import os
import json

# Ensure backend root is in path
sys.path.append(os.getcwd())

from dotenv import load_dotenv
load_dotenv(".env")

from app.services.planner.orchestrator import AgenticOrchestrator

async def main():
    print("--- Testing Agentic Planner Refactor ---")
    
    try:
        orchestrator = AgenticOrchestrator(user_id="demo_user")
        plans = await orchestrator.generate_plan()
        
        print(f"\nSuccessfully generated {len(plans)} learning paths!")
        
        for i, plan in enumerate(plans):
            print(f"\n--- Plan {i+1} ---")
            # Using .dict() if pydantic v1 or .model_dump() if pydantic v2. 
            # Trying standard dict access or conversion
            data = plan.dict()
            print(json.dumps(data, indent=2, default=str))
            
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
