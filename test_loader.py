from utils.loader import load_documents

if __name__ == "__main__":
    docs = load_documents("data/uploads")
    print(f"\nLoaded {len(docs)} documents.\n")
    for d in docs:
        print(f"Source: {d['source']}")
        print(f"Preview: {d['content'][:300]}...\n")

