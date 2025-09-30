from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
# This import line is now updated
from langchain_community.cache import InMemoryCache 
from langchain.globals import set_llm_cache

set_llm_cache(InMemoryCache())

def create_rag_pipeline(vectorstore, groq_api_key: str):
    llm = ChatGroq(
        temperature=0, 
        groq_api_key=groq_api_key, 
        model_name="llama-3.1-8b-instant"
    )
    retriever = vectorstore.as_retriever(search_kwargs={'k': 3})
    prompt_template = """
    Use the following context to answer the question. If you don't know the answer, say you don't know.
    Context: {context}
    Question: {question}
    Answer:
    """
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )
    return qa_chain