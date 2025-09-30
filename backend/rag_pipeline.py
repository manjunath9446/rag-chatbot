import os
import pickle
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores.faiss import FAISS

def process_and_store_documents(upload_dir, vectorstore_path="vectorstore.pkl"):
    doc_texts = []
    for file_name in os.listdir(upload_dir):
        if file_name.endswith('.pdf'):
            pdf_path = os.path.join(upload_dir, file_name)
            pdf_reader = PdfReader(pdf_path)
            text = "".join(page.extract_text() or "" for page in pdf_reader.pages)
            doc_texts.append(text)

    if not doc_texts:
        raise ValueError("No PDF documents found in the specified directory.")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    texts = text_splitter.split_text("\n\n".join(doc_texts))
    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_texts(texts, embedding=embeddings)
    
    with open(vectorstore_path, "wb") as f:
        pickle.dump(vectorstore, f)
        
    return vectorstore