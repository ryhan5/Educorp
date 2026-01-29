import boto3
import json
import os
from botocore.exceptions import ClientError

# Initialize Bedrock Client
# AWS credentials should be in ~/.aws/credentials or environment variables
REGION_NAME = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

try:
    bedrock_runtime = boto3.client(
        service_name="bedrock-runtime",
        region_name=REGION_NAME
    )
except Exception as e:
    print(f"Error initializing Bedrock client: {e}")
    bedrock_runtime = None

# Model IDs (Nova Series)
NOVA_LITE = "amazon.nova-lite-v1:0"
NOVA_PRO = "amazon.nova-pro-v1:0"
NOVA_PREMIER = "amazon.nova-premier-v1:0"

def invoke_nova_lite(prompt: str, max_tokens: int = 1000) -> str:
    """
    Invokes Amazon Nova Lite for fast, lightweight tasks.
    """
    if not bedrock_runtime:
        return "Bedrock client not initialized."

    body = json.dumps({
        "inferenceConfig": {
            "max_new_tokens": max_tokens
        },
        "messages": [
            {
                "role": "user",
                "content": [
                    {"text": prompt}
                ]
            }
        ]
    })

    try:
        response = bedrock_runtime.invoke_model(
            modelId=NOVA_LITE,
            body=body
        )
        response_body = json.loads(response.get("body").read())
        # Parse Nova response structure
        output_text = response_body["output"]["message"]["content"][0]["text"]
        return output_text
    except ClientError as e:
        return f"AWS Bedrock Error: {e}"
    except Exception as e:
        return f"Error invoking Nova Lite: {e}"

def invoke_nova_pro(system_prompt: str, user_prompt: str, max_tokens: int = 2000) -> str:
    """
    Invokes Amazon Nova Pro for complex reasoning and planning.
    """
    if not bedrock_runtime:
        return "Bedrock client not initialized."

    body = json.dumps({
         "inferenceConfig": {
            "max_new_tokens": max_tokens
        },
        "system": [
            {"text": system_prompt}
        ],
        "messages": [
            {
                "role": "user",
                "content": [
                    {"text": user_prompt}
                ]
            }
        ]
    })

    try:
        response = bedrock_runtime.invoke_model(
            modelId=NOVA_PRO,
            body=body
        )
        response_body = json.loads(response.get("body").read())
        output_text = response_body["output"]["message"]["content"][0]["text"]
        return output_text
    except Exception as e:
        return f"Error invoking Nova Pro: {e}"
