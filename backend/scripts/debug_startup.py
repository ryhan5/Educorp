import sys
import os

print("Debugging imports...")
try:
    from langchain_aws import ChatBedrock
    print("✅ langchain_aws imported")
except ImportError as e:
    print(f"❌ langchain_aws failed: {e}")

try:
    from langchain_core.prompts import ChatPromptTemplate
    print("✅ langchain_core.prompts imported")
except ImportError as e:
    print(f"❌ langchain_core.prompts failed: {e}")

try:
    from app.services.learning_pack.agent import LearningPackAgent
    print("✅ LearningPackAgent imported")
except ImportError as e:
    print(f"❌ LearningPackAgent failed: {e}")
except Exception as e:
    print(f"❌ LearningPackAgent other error: {e}")
