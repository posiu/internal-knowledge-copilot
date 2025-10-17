from utils.vector_store import load_existing_vectorstore
from utils.qa_chain import build_qa_chain

if __name__ == "__main__":
    # Load existing vector store
    vectorstore = load_existing_vectorstore()

    # Build QA chain
    qa = build_qa_chain(vectorstore)

    print("💬 Ask your question about the documents:")
    question = input("> ")

    response = qa.invoke({"query": question})

    print("\n🧩 Answer:\n", response["result"])
    print("\n📚 Sources:")
    for doc in response["source_documents"]:
        print(" -", doc.metadata["source"])

