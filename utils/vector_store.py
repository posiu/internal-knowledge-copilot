import os
from typing import List, Dict
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

# Load .env file for API keys
load_dotenv()

def create_or_load_vectorstore(docs: List[Dict[str, str]], persist_directory: str = "data/chroma_db"):
    """
    Takes a list of documents [{'source':..., 'content':...}]
    Creates embeddings and stores them in Chroma (persistent vector DB).
    Returns the Chroma vectorstore object.
    """
    os.makedirs(persist_directory, exist_ok=True)

    print("🧠 Initializing OpenAI embeddings...")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    print(f"💾 Storing vectors in: {persist_directory}")
    texts = [doc["content"] for doc in docs]
    metadatas = [{"source": doc["source"]} for doc in docs]

    vectorstore = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas,
        persist_directory=persist_directory
    )

    # New Chroma automatically persists when persist_directory is set
    print(f"✅ Vector store created and saved with {len(docs)} documents.")
    return vectorstore

def load_existing_vectorstore(persist_directory: str = "data/chroma_db"):
    """
    Loads an existing Chroma vector store if it exists.
    """
    if not os.path.exists(persist_directory):
        raise ValueError("❌ No existing vector store found. Please build it first.")
    
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    print("📂 Loading existing vector store...")
    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    return vectorstore

