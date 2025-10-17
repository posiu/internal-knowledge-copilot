from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

def build_qa_chain(vectorstore):
    """
    Builds a retrieval-based QA chain using GPT-4o-mini and Chroma retriever.
    """
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # Custom prompt template
    template = """
    You are Internal Knowledge Copilot — an assistant that answers questions 
    based strictly on provided company documents.

    Use only the retrieved context below to answer the user's question.
    Be concise, factual, and cite the document names you used (from metadata 'source').

    If the answer is not found in the documents, say:
    "I couldn't find relevant information in the uploaded files."

    ----------------
    Context:
    {context}
    ----------------
    Question: {question}
    Answer (with citations):
    """

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=template
    )

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.0  # 0 for factual, consistent answers
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",   # simplest and effective method for small documents
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True
    )

    return qa_chain

