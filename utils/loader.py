import os
from typing import List, Dict
from pypdf import PdfReader
import docx

def load_text_from_pdf(file_path: str) -> str:
    """Extracts all text from a PDF file."""
    text = ""
    with open(file_path, "rb") as f:
        pdf = PdfReader(f)
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.strip()

def load_text_from_docx(file_path: str) -> str:
    """Extracts all text from a DOCX file."""
    doc = docx.Document(file_path)
    text = "\n".join([p.text for p in doc.paragraphs])
    return text.strip()

def load_text_from_txt(file_path: str) -> str:
    """Reads plain text from a TXT file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()

def load_documents(upload_dir: str) -> List[Dict[str, str]]:
    """
    Loads and extracts text from all supported files in a given directory.
    Returns a list of dicts with {'source': filename, 'content': text}.
    """
    supported_ext = [".pdf", ".docx", ".txt"]
    documents = []

    for filename in os.listdir(upload_dir):
        file_path = os.path.join(upload_dir, filename)
        _, ext = os.path.splitext(filename)

        if ext.lower() not in supported_ext:
            print(f"⚠️ Skipping unsupported file: {filename}")
            continue

        try:
            if ext.lower() == ".pdf":
                text = load_text_from_pdf(file_path)
            elif ext.lower() == ".docx":
                text = load_text_from_docx(file_path)
            elif ext.lower() == ".txt":
                text = load_text_from_txt(file_path)
            else:
                text = ""
            
            if text:
                documents.append({"source": filename, "content": text})
                print(f"✅ Loaded {filename} ({len(text)} characters)")
            else:
                print(f"⚠️ No text extracted from {filename}")

        except Exception as e:
            print(f"❌ Error reading {filename}: {e}")

    return documents

