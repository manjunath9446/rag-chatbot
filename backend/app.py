import os
import pickle
import shutil
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from ingest import process_and_store_documents
from rag_pipeline import create_rag_pipeline

load_dotenv()
app = Flask(__name__)
CORS(app)

UPLOAD_DIR = "uploaded_files"
VECTORSTORE_PATH = "vectorstore.pkl"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Global variable to hold the RAG chain
rag_chain = None

def initialize_rag_chain():
    global rag_chain
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY environment variable not set.")
    
    if os.path.exists(VECTORSTORE_PATH):
        with open(VECTORSTORE_PATH, "rb") as f:
            vectorstore = pickle.load(f)
        rag_chain = create_rag_pipeline(vectorstore, groq_api_key)
        print("RAG chain initialized successfully.")
    else:
        print("Vector store not found. Waiting for file upload.")

@app.route('/upload', methods=['POST'])
def upload_files():
    global rag_chain
    
    # Clear previous uploads
    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)
    os.makedirs(UPLOAD_DIR)

    if 'files' not in request.files:
        return jsonify({"error": "No files part in the request."}), 400
    
    files = request.files.getlist('files')
    if not files or files[0].filename == '':
        return jsonify({"error": "No files selected for uploading."}), 400

    for file in files:
        if file:
            filename = file.filename
            file.save(os.path.join(UPLOAD_DIR, filename))
    
    try:
        # Process new files and create a new vector store
        vectorstore = process_and_store_documents(UPLOAD_DIR, VECTORSTORE_PATH)
        
        # Re-initialize the RAG chain with the new vector store
        groq_api_key = os.environ.get("GROQ_API_KEY")
        rag_chain = create_rag_pipeline(vectorstore, groq_api_key)
        
        return jsonify({"message": f"{len(files)} files uploaded and processed successfully."}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred during processing: {str(e)}"}), 500

@app.route('/query', methods=['POST'])
def query_endpoint():
    if not rag_chain:
        return jsonify({"error": "RAG chain not initialized. Please upload documents first."}), 400
        
    data = request.get_json()
    query_text = data.get('query')
    if not query_text:
        return jsonify({"error": "Query text is required."}), 400
        
    try:
        result = rag_chain({"query": query_text})
        response = {
            "answer": result["result"],
            "sources": [doc.page_content for doc in result["source_documents"]]
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    initialize_rag_chain() # Initialize on startup if a vectorstore already exists
    app.run(host='0.0.0.0', port=5000)