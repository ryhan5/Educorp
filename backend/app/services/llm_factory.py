import os
from langchain_aws import ChatBedrock
import boto3

def get_llm(temperature=0.7):
    """
    Returns a ChatBedrock instance configured for the hackathon.
    Retries or error handling for credentials should be managed by the caller or standard AWS SDK behavior.
    """
    # Hackathon constraints
    region_name = "us-east-1"
    model_id = "amazon.nova-lite-v1:0"
    
    # Ensure AWS Credentials are in environment or config
    from dotenv import load_dotenv
    import os
    
    # Debug info
    print(f"DEBUG: Current CWD: {os.getcwd()}")
    env_path = os.path.join(os.getcwd(), ".env")
    print(f"DEBUG: Looking for .env at: {env_path}, Exists: {os.path.exists(env_path)}")
    
    load_dotenv(env_path, override=True) # Force load .env
    
    # Explicitly get keys from env to debug/ensure availability
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_DEFAULT_REGION", region_name)

    print(f"DEBUG: AWS_ACCESS_KEY_ID present: {bool(aws_access_key)}")
    if aws_access_key:
        print(f"DEBUG: AWS Key starts with: {aws_access_key[:4]}...")

    if not aws_access_key or not aws_secret_key:
        print("CRITICAL: AWS Credentials not found in environment!")
    
    return ChatBedrock(
        model_id=model_id,
        region_name=aws_region,
        model_kwargs={"temperature": temperature},
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
    )
