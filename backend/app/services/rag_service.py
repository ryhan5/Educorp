"""
RAG Service: Retrieval-Augmented Generation using AWS Bedrock Embeddings
"""
import os
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_aws import BedrockEmbeddings
from langchain_core.embeddings import FakeEmbeddings
from langchain_core.documents import Document
import boto3

# In-memory storage for the prototype
# In production, this would be a persistent vector DB (Pinecone/Weaviate)
vector_store = None
_embeddings = None

REGION_NAME = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
# Bedrock embedding model - Titan is the most commonly available
EMBEDDING_MODEL_ID = os.getenv("BEDROCK_EMBEDDING_MODEL", "amazon.titan-embed-text-v1")


def _get_embeddings():
    """
    Initialize and return AWS Bedrock Embeddings.
    Falls back to FakeEmbeddings if Bedrock is unavailable.
    """
    global _embeddings
    if _embeddings:
        return _embeddings
    
    try:
        bedrock_client = boto3.client(
            service_name="bedrock-runtime",
            region_name=REGION_NAME
        )
        _embeddings = BedrockEmbeddings(
            client=bedrock_client,
            model_id=EMBEDDING_MODEL_ID
        )
        # Test the embeddings with a simple query
        _embeddings.embed_query("test")
        print(f"AWS Bedrock Embeddings initialized: {EMBEDDING_MODEL_ID}")
        return _embeddings
    except Exception as e:
        print(f"Bedrock Embeddings unavailable ({e}), falling back to FakeEmbeddings")
        _embeddings = FakeEmbeddings(size=1536)  # Titan outputs 1536-dim vectors
        return _embeddings


async def initialize_context(text: str):
    """
    Initialize the RAG vector store with the provided text.
    Uses AWS Bedrock Titan embeddings for semantic indexing.
    """
    global vector_store
    
    # Chunking might be needed for very long texts, keeping it simple for now
    docs = [Document(page_content=text, metadata={"source": "user_upload"})]
    
    try:
        embeddings = _get_embeddings()
        vector_store = FAISS.from_documents(docs, embeddings)
        print("RAG Context Initialized with AWS Bedrock Embeddings")
    except Exception as e:
        print(f"RAG Initialization failed: {e}")
        vector_store = None


async def get_context(query: str, k: int = 2) -> str:
    """
    Retrieve relevant context from the vector store using semantic similarity.
    """
    global vector_store
    if not vector_store:
        return ""
    
    try:
        docs = vector_store.similarity_search(query, k=k)
        return "\n\n".join([d.page_content for d in docs])
    except Exception as e:
        print(f"RAG retrieval error: {e}")
        return ""
