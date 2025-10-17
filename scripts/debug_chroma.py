import os
from langchain_community.vectorstores import Chroma

base_dir = "data"

# Handle the pointer file if it exists
pointer_path = os.path.join(base_dir, "chroma_db_pointer.txt")

if os.path.exists(pointer_path):
    with open(pointer_path) as f:
        line = f.read().strip()
        if "|" in line:
            db_path, collection_name = line.split("|", 1)
        else:
            db_path, collection_name = line, "main"
else:
    # fallback: find last chroma_db_* directory
    dirs = [d for d in os.listdir(base_dir) if d.startswith("chroma_db_")]
    if not dirs:
        print("❌ No Chroma DB found")
        exit()
    db_path = os.path.join(base_dir, sorted(dirs)[-1])
    collection_name = "main"

print(f"🔍 Inspecting DB at: {db_path} (collection: {collection_name})")

vs = Chroma(persist_directory=db_path, collection_name=collection_name)
metas = vs.get(include=["metadatas"])["metadatas"]

print(f"✅ {len(metas)} chunks found")

unique_sources = set(m.get("source") for m in metas if m and "source" in m)
print("📄 Unique sources:", unique_sources)
