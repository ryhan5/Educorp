import asyncio
import sys
import os
import json
import httpx

# Ensure backend root is in path
sys.path.append(os.getcwd())

async def main():
    print("--- Testing Learning Pack Generator API ---")
    
    # We will invoke the service directly or via localhost if running.
    # Since server might be busy or reloading, let's try direct service invocation for unit testing logic
    # But wait, Bedrock calls need environment.
    
    from dotenv import load_dotenv
    load_dotenv(".env")
    
    from app.services.learning_pack.agent import LearningPackAgent
    
    agent = LearningPackAgent()
    
    print("Invoking Agent (this calls Amazon Bedrock)...")
    try:
        pack = await agent.generate_pack(
            skill_name="React Hooks",
            context={"confidence": 45, "depth": 20}
        )
        
        print("\n✅ Generation Success!")
        print(f"Skill: {pack.skill_name}")
        print(f"Notes: {len(pack.notes)}")
        print(f"Quiz Questions: {len(pack.quiz)}")
        print(f"Flashcards: {len(pack.flashcards)}")
        
        # Verify Content
        if pack.notes:
            print(f"Sample Note: {pack.notes[0].title}")
            
    except Exception as e:
        print(f"❌ Generation Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
