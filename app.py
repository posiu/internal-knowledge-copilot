import os
import uuid
import time
import shutil
import streamlit as st
from dotenv import load_dotenv

from utils.loader import load_documents
from utils.vector_store import create_or_load_vectorstore, load_existing_vectorstore
from utils.qa_chain import build_qa_chain

# --- ENV ---
load_dotenv()

# --- PAGE CONFIG ---
st.set_page_config(page_title="Internal Knowledge Copilot", page_icon="🤖", layout="centered")

# --- SESSION DEFAULTS ---
for k, v in {
    "kb_ready": False,
    "question": "",
    "answer": "",
    "chroma_db_path": "",
    "collection_name": "",
    "current_files": [],
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --- HELPERS ---
def reset_app_state():
    """Clear QA and KB selection."""
    for k in ["question", "answer", "chroma_db_path", "collection_name", "kb_ready"]:
        if k in st.session_state:
            del st.session_state[k]
    st.session_state.kb_ready = False
    st.session_state.question = ""
    st.session_state.answer = ""

def on_upload_change():
    """When files change, force user to rebuild and clear QA."""
    st.session_state.kb_ready = False
    st.session_state.question = ""
    st.session_state.answer = ""
    st.session_state.current_files = []
    pointer = os.path.join("data", "chroma_db_pointer.txt")
    if os.path.exists(pointer):
        try:
            os.remove(pointer)
        except Exception:
            pass

# --- STYLES ---
st.markdown("""
    <style>
        .main { max-width: 850px; margin: 0 auto; padding-top: 2rem; }

        /* Top bar */
        .top-bar {
            position: fixed; top: 0; left: 0; right: 0; height: 60px;
            background-color: #ffffff; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            display: flex; align-items: center; justify-content: center; z-index: 100;
        }
        .top-bar-inner {
            display: flex; align-items: center; justify-content: space-between;
            max-width: 850px; width: 100%; padding: 0 1rem;
        }
        .top-bar h2 { font-size: 1.3rem; color: #2c3e50; margin: 0; display: flex; align-items: center; gap: .4rem; }

        /* Typography */
        h1 { text-align: center; font-size: 2.4rem !important; color: #2c3e50; margin-top: 5rem; margin-bottom: .5rem; }
        h3 { text-align: center; color: #555; font-weight: normal; margin-bottom: 2rem; }

        /* Buttons */
        .stButton>button {
            border-radius: 10px; background-color: #FF4B4B; color: white;
            font-weight: 600; height: 3rem; width: 100%; border: none;
        }
        .stButton>button:hover { background-color: #ff6b6b; }

        /* Footer */
        footer { text-align: center; padding-top: 3rem; font-size: 0.9rem; color: #888; }
        a { color: #FF4B4B; text-decoration: none; }
        a:hover { text-decoration: underline; }

        /* Space below fixed bar */
        .block-container { padding-top: 90px !important; }
    </style>
""", unsafe_allow_html=True)

# --- TOP BAR ---
st.markdown("""
<div class="top-bar">
    <div class="top-bar-inner">
        <h2>🤖 Internal Knowledge Copilot</h2>
    </div>
</div>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("Ask Your Documents Anything 💬")
st.markdown("<h3>AI-powered answers with context and citations.</h3>", unsafe_allow_html=True)

with st.expander("📘 HOW TO USE", expanded=False):
    st.markdown("""
        1️⃣ **Upload** your documents (PDF, DOCX, TXT).  
        2️⃣ **Rebuild** your knowledge base (previous data is cleared unless you choose to accumulate).  
        3️⃣ **Ask** your question (optionally limit search to specific files).  
        4️⃣ **Review** the AI answer and its cited sources.  
    """)

st.divider()

# --- UPLOAD ---
st.subheader("📂 Upload Your Documents")

accumulate = st.checkbox("Keep previously uploaded files (accumulate)", value=False)

uploaded_files = st.file_uploader(
    "Upload internal documents",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True,
    key="uploader",
    on_change=on_upload_change
)

# Save uploads
if uploaded_files:
    os.makedirs("data/uploads", exist_ok=True)
    if not accumulate:
        # Clear previous uploads so only current selection is indexed
        for item in os.listdir("data/uploads"):
            path = os.path.join("data/uploads", item)
            if os.path.isfile(path):
                os.remove(path)
    # Save new
    saved_names = []
    for uploaded_file in uploaded_files:
        file_path = os.path.join("data/uploads", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        saved_names.append(uploaded_file.name)
    st.session_state.current_files = sorted(saved_names)

    st.success("✅ Files saved. Please rebuild the knowledge base.")

    # Centered Rebuild button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 Rebuild Knowledge Base"):
            with st.spinner("Clearing old data and embedding new documents..."):
                # Reset UI/session & remove any old pointer
                on_upload_change()

                # 1) Remove old DB folders safely (dirs only)
                chroma_root = "data"
                if os.path.exists(chroma_root):
                    for item in os.listdir(chroma_root):
                        path = os.path.join(chroma_root, item)
                        if item.startswith("chroma_db") and os.path.isdir(path):
                            shutil.rmtree(path)

                # 2) Create brand-new DB directory + unique collection name
                new_db_path = os.path.join("data", f"chroma_db_{uuid.uuid4().hex[:8]}")
                os.makedirs(new_db_path, exist_ok=True)
                collection_name = f"ikc_{int(time.time())}"

                # 3) Load documents from current uploads only
                documents = load_documents("data/uploads")

                # 4) Build vector store in THIS path + collection
                _ = create_or_load_vectorstore(
                    documents,
                    persist_directory=new_db_path,
                    collection_name=collection_name,
                )

                # 5) Persist selection for QA
                pointer_file = os.path.join("data", "chroma_db_pointer.txt")
                with open(pointer_file, "w") as f:
                    f.write(f"{new_db_path}|{collection_name}")
                st.session_state.chroma_db_path = new_db_path
                st.session_state.collection_name = collection_name

                # 6) Mark KB ready and clear QA boxes
                st.session_state.kb_ready = True
                st.session_state.question = ""
                st.session_state.answer = ""

                st.success("✅ Knowledge base rebuilt successfully! You can ask questions below.")

st.divider()

# --- QA ---
st.subheader("💬 Ask a Question")

# Only let users ask after KB is ready
question = st.text_input(
    "Enter your question here",
    value=st.session_state.question,
    key="question",
    disabled=not st.session_state.kb_ready,
)

# NEW: let user pick which files to search
limit_files = []
if st.session_state.kb_ready:
    if st.session_state.current_files:
        limit_files = st.multiselect(
            "Limit search to files (recommended):",
            options=st.session_state.current_files,
            default=st.session_state.current_files,  # all by default; user can narrow
            help="Choose which uploaded files the AI is allowed to search."
        )

if st.session_state.kb_ready and question.strip():
    # Resolve db path + collection name
    db_path = st.session_state.get("chroma_db_path")
    collection_name = st.session_state.get("collection_name")

    # Fallback to pointer file (after restart)
    if not (db_path and collection_name):
        pointer_file = os.path.join("data", "chroma_db_pointer.txt")
        if os.path.exists(pointer_file):
            with open(pointer_file) as f:
                content = f.read().strip()
                if "|" in content:
                    db_path, collection_name = content.split("|", 1)
                    st.session_state.chroma_db_path = db_path
                    st.session_state.collection_name = collection_name

    if db_path and collection_name and os.path.isdir(db_path):
        vectorstore = load_existing_vectorstore(
            persist_directory=db_path,
            collection_name=collection_name,
        )

        # Build a strict metadata filter for the retriever (by source filenames)
        search_filter = None
        if limit_files:
            search_filter = {"source": {"$in": limit_files}}

        limit_files = st.session_state.get("limit_files") or []
        qa_chain = build_qa_chain(vectorstore, limit_files=limit_files)


        with st.spinner("Thinking..."):
            st.session_state.answer = ""
            result = qa_chain.invoke({"query": question})
            # If RetrievalQA returns sources, we can sanity-check which files contributed
            st.session_state.answer = result["result"].strip()
            used_sources = sorted({d.metadata.get("source", "unknown") for d in result.get("source_documents", [])})
        st.markdown("### 🧠 Answer")
        st.write(st.session_state.answer)
        if limit_files:
            st.caption(f"Searched files: {', '.join(limit_files)}")
        if used_sources:
            st.caption(f"Sources used: {', '.join(used_sources)}")
        st.caption(f"KB: `{db_path}` • Collection: `{collection_name}`")
    else:
        st.warning("⚠️ Please upload and rebuild your knowledge base first.")
elif not st.session_state.kb_ready:
    st.info("ℹ️ Upload files and click **Rebuild Knowledge Base** to enable questions.")

# --- FOOTER ---
st.markdown("""
<footer>
    Created with ❤️ by <a href="https://github.com/posiu" target="_blank">posiu</a> (and AI 🤖)
</footer>
""", unsafe_allow_html=True)
