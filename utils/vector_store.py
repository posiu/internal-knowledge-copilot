import os
import time
from typing import List, Any

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings


def _normalize_documents(documents: List[Any]):
    """
    Accepts multiple input shapes and normalizes to (texts, metadatas) lists.

    Supported shapes:
    - ["text", "text2", ...]
    - [{"text": "...", "source": "file.ext"}, ...]
    - [{"page_content": "...", "metadata": {...}}, ...]
    - [Document(page_content="...", metadata={...}), ...]
    """
    texts, metadatas = [], []
    for doc in documents:
        if isinstance(doc, str):
            texts.append(doc)
            metadatas.append({})
        elif isinstance(doc, dict):
            if "page_content" in doc:
                texts.append(doc["page_content"])
                metadatas.append(doc.get("metadata", {}))
            elif "text" in doc:
                texts.append(doc["text"])
                metadatas.append({"source": doc.get("source", "unknown")})
            else:
                # fallback: join values if unknown dict schema
                texts.append(" ".join(str(v) for v in doc.values()))
                metadatas.append({})
        else:
            # likely a LangChain Document
            texts.append(getattr(doc, "page_content", str(doc)))
            metadatas.append(getattr(doc, "metadata", {}))
    return texts, metadatas


def create_or_load_vectorstore(
    documents,
    persist_directory: str = "data/chroma_db",
    collection_name: str = "ikc_collection",
):
    """
    Build a brand-new Chroma collection in the given persist_directory.
    IMPORTANT: we DO NOT pass a custom client here — letting LangChain-Chroma
    create a PersistentClient bound to persist_directory, which avoids cross-contamination.
    """
    os.makedirs(persist_directory, exist_ok=True)

    embeddings = OpenAIEmbeddings()
    texts, metadatas = _normalize_documents(documents)

    # Create a fresh collection with the explicit name
    vs = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas,
        persist_directory=persist_directory,
        collection_name=collection_name,
    )
    vs.persist()
    time.sleep(0.1)
    return vs


def load_existing_vectorstore(
    persist_directory: str = "data/chroma_db",
    collection_name: str = "ikc_collection",
):
    """
    Load the exact existing Chroma collection from a given persist_directory.
    Again, do NOT pass a client; let Chroma bind to the directory itself.
    """
    embeddings = OpenAIEmbeddings()
    return Chroma(
        persist_directory=persist_directory,
        collection_name=collection_name,
        embedding_function=embeddings,
    )
