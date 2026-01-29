import os
import sys
import asyncio
from dotenv import load_dotenv
from langchain_aws import ChatBedrock

# Add parent dir to path to import app modules if needed
sys.path.append(os.path.join(os.getcwd()))

async def test_bedrock():
    print("--- Starting Bedrock Connection Test ---")
    
    # 1. Load Environment
    load_dotenv(override=True)
    aws_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    
    print(f"AWS Key ID Found: {bool(aws_key)}")
    if aws_key:
        print(f"Key Prefix: {aws_key[:4]}...")
    print(f"Target Region: {aws_region}")
    
    # 2. Initialize Client
    try:
        print("\nInitializing ChatBedrock...")
        llm = ChatBedrock(
            model_id="amazon.nova-lite-v1:0",
            region_name=aws_region,
            model_kwargs={"temperature": 0.1},
            # Explicitly pass if env loading is flaky, but dotenv should handle it now
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        print("Client initialized.")
    except Exception as e:
        print(f"FAILED to initialize client: {e}")
        return

    # 3. Invoke Model
    try:
        print("\nInvoking Model with 'Hello'...")
        response = await llm.ainvoke("Hello, this is a test.")
        print("\nSUCCESS! Response received:")
        print("-" * 20)
        print(response.content)
        print("-" * 20)
    except Exception as e:
        print(f"\nFAILED to invoke model: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_bedrock())
