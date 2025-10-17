from utils.loader import load_documents
from utils.vector_store import create_or_load_vectorstore, load_existing_vectorstore

if __name__ == "__main__":
    # Step 1: Load documents
    docs = load_documents("data/uploads")

    # Step 2: Create vector store
    if docs:
        vs = create_or_load_vectorstore(docs)
        print("\n✅ Vector store created successfully!\n")

    # Step 3: Load and test retrieval
    loaded_vs = load_existing_vectorstore()
    print("🔍 Testing retrieval...")
    query = "What is this document about?"
    results = loaded_vs.similarity_search(query, k=2)

    for r in results:
        print(f"\nResult from: {r.metadata['source']}")
        print(r.page_content[:300], "...\n")

