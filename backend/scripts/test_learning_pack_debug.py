import asyncio
import sys
import os

sys.path.insert(0, os.getcwd())

from dotenv import load_dotenv
load_dotenv(".env")

async def test():
    print("=== Testing Learning Pack Agent ===")
    
    # First test direct Bedrock call
    from app.services.bedrock import invoke_nova_pro
    
    print("\n1. Testing direct Bedrock call...")
    response = invoke_nova_pro(
        "You are a helpful assistant. Output only valid JSON.",
        'Generate a JSON array with 2 items: [{"title": "Test", "content": "Hello"}]'
    )
    print(f"Direct Bedrock Response: {response[:500]}")
    
    # Now test the agent
    print("\n2. Testing LearningPackAgent...")
    from app.services.learning_pack.agent import LearningPackAgent
    
    agent = LearningPackAgent()
    try:
        pack = await agent.generate_pack(
            skill_name="Python Basics",
            context={"confidence": 50}
        )
        print(f"\nAgent Result:")
        print(f"  Notes: {len(pack.notes)}")
        print(f"  Quiz: {len(pack.quiz)}")
        print(f"  Flashcards: {len(pack.flashcards)}")
        
        if pack.notes:
            print(f"\nFirst Note: {pack.notes[0].title}")
    except Exception as e:
        print(f"Agent Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
