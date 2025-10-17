from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI


def build_qa_chain(vectorstore, limit_files=None):
    """
    Build a QA chain that uses filtered retrieval (by 'source' metadata)
    and produces factual answers with sources.
    """
    # Optional filtering by filename(s)
    search_kwargs = {}
    if limit_files:
        search_kwargs["filter"] = {"source": {"$in": limit_files}}

    retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)

    template = (
        "You are a helpful assistant that answers questions based strictly on the provided documents.\n"
        "If the answer cannot be found in the documents, say: 'I couldn't find relevant information in the uploaded files.'\n\n"
        "Question: {question}\n\n"
        "Relevant context from the documents:\n{context}\n\n"
        "Answer with a short factual response and include the filename(s) from which the information was taken."
    )

    prompt = PromptTemplate(template=template, input_variables=["context", "question"])

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
    )

    return qa_chain
