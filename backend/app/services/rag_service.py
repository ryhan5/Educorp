import os
from typing import List
from langchain_community.vectorstores import FAISS
# from langchain_google_genai import GoogleGenerativeAIEmbeddings # Removed per user request
from langchain_core.embeddings import FakeEmbeddings
from langchain_core.documents import Document

# In-memory storage for the prototype
# In production, this would be a persistent vector DB (Pinecone/Weaviate)
vector_store = None

async def initialize_context(text: str):
    global vector_store
    
    # Chunking might be needed for very long texts, keeping it simple for now
    docs = [Document(page_content=text, metadata={"source": "user_upload"})]
    
    # Using FakeEmbeddings to remove Gemini dependency
    try:
        embeddings = FakeEmbeddings(size=768)
        vector_store = FAISS.from_documents(docs, embeddings)
        print("RAG Context Initialized (Fake Embeddings)")
    except Exception as e:
        print(f"RAG Initialization failed: {e}")
        vector_store = None


async def get_context(query: str, k: int = 2) -> str:
    global vector_store
    if not vector_store:
        return ""
    
    docs = vector_store.similarity_search(query, k=k)
    return "\n\n".join([d.page_content for d in docs])
