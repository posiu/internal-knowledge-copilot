import streamlit as st
import os
import shutil  # add this near the top of the file (with other imports)
import time
import uuid
import chromadb
from dotenv import load_dotenv

from utils.loader import load_documents
from utils.vector_store import create_or_load_vectorstore, load_existing_vectorstore
from utils.qa_chain import build_qa_chain

# Load environment variables (like OPENAI_API_KEY)
load_dotenv()

# Streamlit page setup
st.set_page_config(page_title="Internal Knowledge Copilot", page_icon="🧩", layout="wide")

st.title("🧩 Internal Knowledge Copilot")
st.markdown("Ask questions about your internal documents with AI-powered retrieval and citations.")

# Paths
UPLOAD_DIR = "data/uploads"
CHROMA_DIR = "data/chroma_db"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)

# --- SIDEBAR ---
st.sidebar.header("📂 Upload Documents")
uploaded_files = st.sidebar.file_uploader(
    "Upload PDF, DOCX, or TXT files",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    st.sidebar.success(f"Uploaded {len(uploaded_files)} file(s).")

# Button to rebuild knowledge base
if st.sidebar.button("🧠 Rebuild Knowledge Base"):
    with st.spinner("Processing documents and creating embeddings..."):
        # 🧹 Instead of deleting, create a new unique Chroma directory
        new_chroma_dir = f"data/chroma_db_{uuid.uuid4().hex[:8]}"
        os.makedirs(new_chroma_dir, exist_ok=True)

        docs = load_documents(UPLOAD_DIR)
        if docs:
            create_or_load_vectorstore(docs, persist_directory=new_chroma_dir)
            st.sidebar.success("✅ Knowledge base rebuilt successfully!")

            # Save new path in session state
            st.session_state["CHROMA_DIR"] = new_chroma_dir
        else:
            st.sidebar.warning("⚠️ No valid documents found.")

# --- MAIN CONTENT ---
st.subheader("💬 Ask a Question")

question = st.text_input("Enter your question:")

if st.button("Get Answer"):
    # Use the latest Chroma directory from session (if available)
    vector_dir = st.session_state.get("CHROMA_DIR", None)

    if not vector_dir or not os.path.exists(vector_dir):
        st.warning("⚠️ Please upload and build the knowledge base first.")
    elif not question.strip():
        st.warning("⚠️ Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            vectorstore = load_existing_vectorstore(vector_dir)
            qa_chain = build_qa_chain(vectorstore)
            response = qa_chain.invoke({"query": question})

            st.markdown("### 🧩 Answer")
            st.write(response["result"])

            st.markdown("### 📚 Sources")
            for doc in response["source_documents"]:
                st.markdown(f"- **{doc.metadata['source']}**")



