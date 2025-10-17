import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


def load_documents(upload_folder: str) -> List[dict]:
    """
    Load and split PDF, DOCX, and TXT files from the given folder.
    Each document gets metadata including its source filename.
    Returns a list of dicts ready for embedding.
    """
    if not os.path.exists(upload_folder):
        raise FileNotFoundError(f"Upload folder '{upload_folder}' does not exist.")

    all_docs = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

    for filename in os.listdir(upload_folder):
        file_path = os.path.join(upload_folder, filename)
        if not os.path.isfile(file_path):
            continue

        ext = filename.lower().split(".")[-1]
        try:
            if ext == "pdf":
                loader = PyPDFLoader(file_path)
            elif ext in ["docx", "doc"]:
                loader = Docx2txtLoader(file_path)
            elif ext == "txt":
                loader = TextLoader(file_path, encoding="utf-8")
            else:
                print(f"⚠️ Skipping unsupported file: {filename}")
                continue

            documents = loader.load()
            if not documents:
                print(f"⚠️ No text extracted from {filename}")
                continue

            split_docs = splitter.split_documents(documents)
            for doc in split_docs:
                if not doc.page_content.strip():
                    continue
                doc.metadata["source"] = filename
                all_docs.append({
                    "page_content": doc.page_content,
                    "metadata": doc.metadata,
                })

        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")

    if not all_docs:
        raise ValueError(
            "No readable text extracted from any uploaded files. "
            "Check that your PDFs/DOCX/TXT contain selectable text (not scanned images)."
        )

    return all_docs
