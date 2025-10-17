from langchain.text_splitter import RecursiveCharacterTextSplitter

def split_documents(docs, chunk_size=1500, chunk_overlap=200):
    """
    Splits long document texts into smaller chunks for embedding.
    Returns a list of dicts: [{'source': filename, 'content': chunk_text}, ...]
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    split_docs = []
    for doc in docs:
        chunks = splitter.split_text(doc["content"])
        for i, chunk in enumerate(chunks):
            split_docs.append({
                "source": f"{doc['source']} (part {i+1})",
                "content": chunk
            })
    return split_docs

